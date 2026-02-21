import os
import random
import aiohttp
import uuid
import logging
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes
import config
from loader import sheets_mgr
from .chat import process_ai_request

# Импортируем наш новый движок
from services.kie_client import kie_studio 

logger = logging.getLogger(__name__)
DOWNLOADS_DIR = "downloads"
if not os.path.exists(DOWNLOADS_DIR):
    os.makedirs(DOWNLOADS_DIR)

# Замени начало функции generate_image на это:

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
        # ... дальше код без изменений ...
        try:
            # ИСПОЛЬЗУЕМ send_photo ВМЕСТО reply_photo
            await context.bot.send_photo(
                chat_id=user_id,
                photo=image_url, 
                caption=f"🎨 <b>Art by vnxORACLE</b>\nModel: <code>Pollinations (Free)</code>\nRatio: {ratio}\nPrompt: {prompt}", 
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
    Vision Module (Обработка входящих фото)
    """
    user_id = update.effective_user.id
    if sheets_mgr.get_user_tariff(user_id) not in ['PRO', 'NEO']:
        return await update.message.reply_text("🧬 <b>VISION MODULE</b>\nДоступен на уровнях PRO и NEO.", parse_mode='HTML')
    
    photo = update.message.photo[-1]
    caption = update.message.caption or "Что на этом фото?"
    
    try:
        file = await context.bot.get_file(photo.file_id)
        path = os.path.join(DOWNLOADS_DIR, f"v_{user_id}_{uuid.uuid4().hex[:8]}.jpg")
        await file.download_to_drive(path)
        
        # Передаем в ядро чата
        await process_ai_request(update, context, caption, image_path=path)
        
    except Exception as e: 
        logger.error(f"Vision Error: {e}")
        await update.message.reply_text("⚠️ Ошибка загрузки изображения.")
