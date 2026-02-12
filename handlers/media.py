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

logger = logging.getLogger(__name__)
DOWNLOADS_DIR = "downloads"

async def generate_image(update: Update, context: ContextTypes.DEFAULT_TYPE, prompt: str):
    user_id = update.effective_user.id
    await context.bot.send_chat_action(chat_id=user_id, action=ChatAction.UPLOAD_PHOTO)
    enhanced_prompt = f"{prompt}, highly detailed, 8k, cinematic lighting"
    seed = random.randint(1, 999999)
    image_url = f"https://image.pollinations.ai/prompt/{enhanced_prompt}?seed={seed}&width=1024&height=1024&nologo=true"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as resp:
                if resp.status == 200:
                    data = await resp.read()
                    await update.message.reply_photo(photo=data, caption=f"🎨 <b>Art by vnxORACLE</b>\nPrompt: {prompt}", parse_mode='HTML')
                else:
                    await update.message.reply_text("⚠️ Сбой визуализации.")
    except Exception as e:
        logger.error(f"Img Error: {e}")
        await update.message.reply_text("⚠️ Ошибка связи с ИИ.")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if sheets_mgr.get_user_tariff(user_id) not in ['PRO', 'NEO']:
        return await update.message.reply_text("🧬 <b>VISION MODULE</b>\nДоступен на уровнях PRO и NEO.", parse_mode='HTML')
    
    photo = update.message.photo[-1]
    caption = update.message.caption or "Что на этом фото?"
    
    try:
        file = await context.bot.get_file(photo.file_id)
        if not os.path.exists(DOWNLOADS_DIR): os.makedirs(DOWNLOADS_DIR)
        path = os.path.join(DOWNLOADS_DIR, f"v_{user_id}_{uuid.uuid4().hex[:8]}.jpg")
        await file.download_to_drive(path)
        await process_ai_request(update, context, caption, image_path=path)
    except Exception as e: 
        logger.error(f"Vision Error: {e}")
        await update.message.reply_text("⚠️ Ошибка загрузки изображения.")
