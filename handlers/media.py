import os
import random
import aiohttp
import uuid
import logging
import asyncio
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes
import config
from loader import sheets_mgr
from .chat import process_ai_request
from keyboards.ai_image import get_post_generation_keyboard, get_photo_action_keyboard

# Импортируем наш новый движок
from services.kie_client import kie_studio 

logger = logging.getLogger(__name__)
DOWNLOADS_DIR = "downloads"
if not os.path.exists(DOWNLOADS_DIR):
    os.makedirs(DOWNLOADS_DIR)

async def generate_image(update: Update, context: ContextTypes.DEFAULT_TYPE, prompt: str, ratio: str = "vertical"):
    """
    Умная генерация изображений (KIE AI + Fallback Pollinations)
    Принимает ratio: "vertical", "horizontal" или "square". По умолчанию vertical.
    """
    user_id = update.effective_user.id
    await context.bot.send_chat_action(chat_id=user_id, action=ChatAction.UPLOAD_PHOTO)
    
    img_model = context.user_data.get('img_model', config.DEFAULT_IMG_MODEL)
    
    # --- 1. ЕСЛИ ВЫБРАН БЕСПЛАТНЫЙ POLLINATIONS ---
    if img_model == "pollinations":
        if ratio == "vertical": w, h = 576, 1024
        elif ratio == "horizontal": w, h = 1024, 576
        else: w, h = 1024, 1024
            
        enhanced_prompt = f"{prompt}, highly detailed, 8k, cinematic lighting"
        seed = random.randint(1, 999999)
        image_url = f"https://image.pollinations.ai/prompt/{enhanced_prompt}?seed={seed}&width={w}&height={h}&nologo=true"
        
        try:
            # ИСПОЛЬЗУЕМ send_photo ВМЕСТО reply_photo
            await context.bot.send_photo(
                chat_id=user_id,
                photo=image_url, 
                caption=f"🎨 <b>Art by vnxORACLE</b>\nModel: <code>Pollinations (Free)</code>\nRatio: {ratio}\nPrompt: {prompt}", 
                reply_markup=get_post_generation_keyboard(), # <-- ДОБАВИЛИ КЛАВИАТУРУ
                parse_mode='HTML'
            )
        except Exception as e:
            logger.error(f"Pollinations Error: {e}")
            await context.bot.send_message(chat_id=user_id, text="⚠️ Ошибка визуализации.")
        return

    # --- 2. ЕСЛИ ВЫБРАНА МОДЕЛЬ ЧЕРЕЗ KIE.AI (Flux, Midjourney, Dalle и тд) ---
    
    # ИСПОЛЬЗУЕМ send_message ВМЕСТО reply_text
    msg = await context.bot.send_message(
        chat_id=user_id, 
        text="⏳ <i>Инициализация нейросети... Задача поставлена в очередь.</i>", 
        parse_mode='HTML'
    )
    
    # Запускаем генерацию и ПЕРЕДАЕМ FORMAT
    result_url = await kie_studio.generate_image(prompt, img_model, ratio)
    
    if result_url:
        try:
            # ИСПОЛЬЗУЕМ send_photo ВМЕСТО reply_photo
            await context.bot.send_photo(
                chat_id=user_id,
                photo=result_url, 
                caption=f"🎨 <b>Art by vnxORACLE</b>\nModel: <code>{img_model}</code>\nRatio: {ratio}\nPrompt: {prompt}", 
                reply_markup=get_post_generation_keyboard(), # <-- ДОБАВИЛИ КЛАВИАТУРУ
                parse_mode='HTML'
            )
            await msg.delete()
        except Exception as e:
            logger.error(f"Telegram Photo Send Error: {e}")
            await msg.edit_text(f"✅ Картинка готова, но Telegram не смог её загрузить (возможно, слишком большой размер).\nСсылка: {result_url}")
    else:
        await msg.edit_text("❌ <b>Сбой генерации.</b>\nНейросеть отклонила запрос или произошла ошибка тайм-аута.", parse_mode='HTML')


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Vision & Img2Img Module (Умный перехват входящих фото)
    """
    user_id = update.effective_user.id
    
    # 🛡 Умный механизм повторных попыток (Retry Policy) для Google Sheets
    user_tariff = 'START' # Значение по умолчанию на случай полного сбоя
    for attempt in range(3):
        try:
            user_tariff = sheets_mgr.get_user_tariff(user_id)
            break # Если успешно, выходим из цикла
        except Exception as e:
            logger.warning(f"⚠️ Google Sheets сбой (попытка {attempt+1}/3): {e}")
            if attempt == 2: # Если это была последняя попытка
                logger.error("❌ Google Sheets полностью недоступен.")
            else:
                await asyncio.sleep(2) # Ждем 2 секунды перед новой попыткой

    if user_tariff not in ['PRO', 'NEO']:
        return await update.message.reply_text("🧬 <b>VISION / EDIT MODULE</b>\nДоступен на уровнях PRO и NEO.", parse_mode='HTML')
    
    photo = update.message.photo[-1]
    caption = update.message.caption or "" # Текст, который юзер прикрепил к фото
    
    try:
        # Скачиваем файл
        file = await context.bot.get_file(photo.file_id)
        path = os.path.join(DOWNLOADS_DIR, f"v_{user_id}_{uuid.uuid4().hex[:8]}.jpg")
        await file.download_to_drive(path)
        
        # 🧠 Сохраняем путь к файлу и текст в "оперативную память" сессии
        context.user_data['last_photo_path'] = path
        context.user_data['last_photo_caption'] = caption
        
        # Формируем понятную инструкцию для пользователя
        instruction_text = (
            "📸 <b>Изображение получено!</b>\n\n"
            "Выберите, что вы хотите сделать:\n"
            "👁 <b>Распознать (Vision)</b> — я проанализирую фото и отвечу на ваш вопрос.\n"
            "🪄 <b>Редактировать (Img2Img)</b> — я изменю фото нейросетью по вашему описанию."
        )
        if caption:
            instruction_text += f"\n\n<i>Ваш промпт: {caption}</i>"
        else:
            instruction_text += "\n\n<i>(Вы не прикрепили текст к фото. Если выберете редактирование, я спрошу промпт следующим шагом)</i>"

        # Отправляем меню
        await update.message.reply_text(
            text=instruction_text,
            reply_markup=get_photo_action_keyboard(),
            parse_mode='HTML'
        )
        
    except Exception as e: 
        logger.error(f"Photo Handle Error: {e}")
        await update.message.reply_text("⚠️ Ошибка обработки изображения.")
