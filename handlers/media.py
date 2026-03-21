import os
import random
import uuid
import logging
import asyncio
import urllib.parse  # 🔥 КРИТИЧЕСКИ ВАЖНО!
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes

import config
from loader import sheets_mgr
from .chat import process_ai_request
from keyboards.ai_image import get_post_generation_keyboard, get_photo_action_keyboard
from services.prompt_censor import is_prompt_safe, clean_prompt
from services.kie_client import kie_studio 

logger = logging.getLogger(__name__)
DOWNLOADS_DIR = "downloads"
if not os.path.exists(DOWNLOADS_DIR):
    os.makedirs(DOWNLOADS_DIR)

async def generate_image(update: Update, context: ContextTypes.DEFAULT_TYPE, prompt: str, ratio: str = "vertical"):
    """
    🛡 БРОНЕБОЙНАЯ ГЕНЕРАЦИЯ (KIE AI + Автоматический Fallback на Pollinations)
    """
    user_id = update.effective_user.id
    await context.bot.send_chat_action(chat_id=user_id, action=ChatAction.UPLOAD_PHOTO)
    
    img_model = context.user_data.get('img_model', config.IMG_POLLINATIONS)
    safe_prompt = clean_prompt(prompt)
    
    # --- Функция-помощник: Pollinations Fallback ---
    async def generate_pollinations_fallback(reason_text: str):
        logger.warning(f"⚠️ Fallback to Pollinations for user {user_id}. Reason: {reason_text}")
        
        if ratio == "vertical":
            w, h = 576, 1024
        elif ratio == "horizontal":
            w, h = 1024, 576
        else:
            w, h = 1024, 1024
            
        enhanced_prompt = f"{safe_prompt}, highly detailed, 8k, cinematic lighting"
        
        # 🔥 КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: URL-кодирование
        encoded_prompt = urllib.parse.quote(enhanced_prompt)
        seed = random.randint(1, 999999)
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?seed={seed}&width={w}&height={h}&nologo=true"
        
        try:
            await context.bot.send_photo(
                chat_id=user_id,
                photo=image_url, 
                caption=f"🎨 <b>Art by vnxORACLE</b>\nModel: <code>Pollinations (Fallback)</code>\nPrompt: {safe_prompt}\n\n⚠️ <i>Основная нейросеть временно недоступна, использован резерв.</i>", 
                reply_markup=get_post_generation_keyboard(),
                parse_mode='HTML'
            )
        except Exception as e:
            logger.error(f"❌ Pollinations Fallback Error: {e}")
            await context.bot.send_message(
                chat_id=user_id, 
                text="⚠️ <b>Критическая ошибка визуализации.</b>\n\nВсе нейросети временно недоступны. Попробуйте через 1-2 минуты.",
                parse_mode='HTML'
            )

    # --- 1. ЕСЛИ ВЫБРАН POLLINATIONS ---
    if img_model == config.IMG_POLLINATIONS:
        return await generate_pollinations_fallback("User selected free model")

    # --- 2. ГЕНЕРАЦИЯ KIE.AI ---
    msg = await context.bot.send_message(
        chat_id=user_id, 
        text="⏳ <i>Инициализация нейросети... Задача поставлена в очередь.</i>", 
        parse_mode='HTML'
    )
    
    result_url, task_id = await kie_studio.generate_image(safe_prompt, img_model, ratio)
    
    if result_url:
        try:
            await context.bot.send_photo(
                chat_id=user_id,
                photo=result_url, 
                caption=f"🎨 <b>Art by vnxORACLE</b>\nModel: <code>{img_model}</code>\nRatio: {ratio}\nPrompt: {safe_prompt}", 
                reply_markup=get_post_generation_keyboard(),
                parse_mode='HTML'
            )
            await msg.delete()
        except Exception as e:
            logger.error(f"❌ Telegram Photo Send Error: {e}")
            await msg.edit_text(f"✅ Картинка готова, но Telegram не смог её загрузить.\nСсылка: {result_url}")
    else:
        # 🔥 FALLBACK
        await msg.delete()
        await generate_pollinations_fallback(f"KIE Error with model {img_model}")


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    mode = context.user_data.get('mode')
    
    photo = update.message.photo[-1]
    caption = update.message.caption or ""
    
    file = await context.bot.get_file(photo.file_id)
    path = os.path.abspath(os.path.join(DOWNLOADS_DIR, f"p_{user_id}_{uuid.uuid4().hex[:8]}.jpg"))
    await file.download_to_drive(path)

    if mode == 'openclaw_wait':
        from services.openclaw_core import claw_manager
        user_name = update.effective_user.first_name or "User"
        msg = await update.message.reply_text("🦞 <i>Агент изучает изображение...</i>", parse_mode='HTML')
        
        injected_prompt = f"{caption}\n\n[SYSTEM: Пользователь прикрепил картинку. Путь: {path}. Опиши её или выполни задачу.]"
        response = await claw_manager.execute_task(injected_prompt, user_id, user_name)
        return await msg.edit_text(response, parse_mode='HTML')

    elif mode == 'video_im
