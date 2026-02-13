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

async def generate_image(update: Update, context: ContextTypes.DEFAULT_TYPE, prompt: str):
    """
    Умная генерация изображений (KIE AI + Fallback Pollinations)
    """
    user_id = update.effective_user.id
    await context.bot.send_chat_action(chat_id=user_id, action=ChatAction.UPLOAD_PHOTO)
    
    # Получаем модель из памяти или берем дефолтную (Flux)
    img_model = context.user_data.get('img_model', config.DEFAULT_IMG_MODEL)
    
    # --- 1. ЕСЛИ ВЫБРАН БЕСПЛАТНЫЙ POLLINATIONS ---
    if img_model == "pollinations":
        enhanced_prompt = f"{prompt}, highly detailed, 8k, cinematic lighting"
        seed = random.randint(1, 999999)
        image_url = f"https://image.pollinations.ai/prompt/{enhanced_prompt}?seed={seed}&width=1024&height=1024&nologo=true"
        
        try:
            await update.message.reply_photo(
                photo=image_url, 
                caption=f"🎨 <b>Art by vnxORACLE</b>\nModel: <code>Pollinations (Free)</code>\nPrompt: {prompt}", 
                parse_mode='HTML'
            )
        except Exception as e:
            logger.error(f"Pollinations Error: {e}")
            await update.message.reply_text("⚠️ Ошибка визуализации.")
        return

    # --- 2. ЕСЛИ ВЫБРАНА МОДЕЛЬ ЧЕРЕЗ KIE.AI (Flux, Midjourney, Dalle и тд) ---
    
    # Сообщаем пользователю, что начали (т.к. асинхрон может занять 30-60 секунд)
    msg = await update.message.reply_text("⏳ <i>Инициализация нейросети... Задача поставлена в очередь.</i>", parse_mode='HTML')
    
    # Запускаем генерацию
    result_url = await kie_studio.generate_image(prompt, img_model)
    
    if result_url:
        try:
            # Отправляем фото и удаляем сообщение "Ожидайте"
            await update.message.reply_photo(
                photo=result_url, 
                caption=f"🎨 <b>Art by vnxORACLE</b>\nModel: <code>{img_model}</code>\nPrompt: {prompt}", 
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
