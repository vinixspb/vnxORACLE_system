import os
import logging
import random
import aiohttp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import BadRequest
from telegram.ext import ContextTypes
from telegram.constants import ChatAction

import config
from loader import sheets_mgr, ai_engine, db, USER_MODELS, audio_studio
import keyboards

logger = logging.getLogger(__name__)

# Папка для временных файлов
DOWNLOADS_DIR = "downloads"
if not os.path.exists(DOWNLOADS_DIR):
    os.makedirs(DOWNLOADS_DIR)

# --- Вспомогательные функции ---
async def send_paywall(update: Update):
    await update.message.reply_text(config.MSG_NO_SUB, reply_markup=keyboards.get_subscription_keyboard(), parse_mode='HTML')

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
                    await update.message.reply_photo(
                        photo=data, 
                        caption=f"🎨 <b>Art by vnxORACLE</b>\nPrompt: {prompt}",
                        parse_mode='HTML'
                    )
                else:
                    await update.message.reply_text("⚠️ Сбой визуализации.")
    except Exception as e:
        logger.error(f"Img Error: {e}")
        await update.message.reply_text("⚠️ Ошибка связи с ИИ.")

async def process_ai_request(update: Update, context: ContextTypes.DEFAULT_TYPE, input_text: str, image_path: str = None):
    """
    Универсальный обработчик запросов (Текст + Зрение).
    """
    user_id = update.effective_user.id
    user_tariff = sheets_mgr.get_user_tariff(user_id)
    if not user_tariff: return await send_paywall(update)

    await context.bot.send_chat_action(chat_id=user_id, action=ChatAction.TYPING)
    session_id = db.get_active_session(user_id)
    
    # Авто-заголовок для новых чатов
    history = db.get_history(session_id, limit=1)
    if not history:
        clean_title = input_text.replace("[Audio Input]: ", "")[:30]
        db.update_session_title(session_id, clean_title)
    
    # Сохраняем запрос пользователя в базу (только текст)
    db.add_message(session_id, "user", input_text)
    
    history_depth = config.LIMITS.get(user_tariff, 10)
    full_context = db.get_history(session_id, limit=history_depth)
    model = USER_MODELS.get(user_id, config.DEFAULT_MODEL)

    try:
        # Вызов обновленного AI Engine с поддержкой Vision
        ai_response, tokens_spent = await ai_engine.get_response(full_context, model, image_path=image_path)
        
        db.add_message(session_id, "assistant", ai_response, model=model)
        db.update_tokens(user_id, tokens_spent)
        
        model_name = model.split('/')[-1].replace(":free", "")
        final_text = (f"{ai_response}\n\n<blockquote>⚙️ {model_name} | 🎫 {tokens_spent} | ∑ {db.get_total_tokens(user_id)}</blockquote>")
        await update.message.reply_text(final_text, parse_mode='HTML')
    except Exception as e:
        logger.error(f"AI Error: {e}")
        await update.message.reply_text("⚠️ Ошибка нейро-интерфейса.")
    finally:
        # Всегда удаляем временное изображение после обработки
        if image_path and os.path.exists(image_path):
            os.remove(image_path)

# --- НОВЫЙ ХЕНДЛЕР: VISION (ОБРАБОТКА ФОТО) ---

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка входящих изображений для анализа ИИ"""
    user_id = update.effective_user.id
    user_tariff = sheets_mgr.get_user_tariff(user_id)
    
    # Vision доступен только для PRO и NEO
    if user_tariff not in ['PRO', 'NEO']:
        return await update.message.reply_text("🧬 <b>VISION MODULE</b>\n\nАнализ изображений доступен только на тарифах <b>PRO</b> и <b>NEO</b>.", parse_mode='HTML')

    caption = update.message.caption or "Что на этом изображении?"
    photo = update.message.photo[-1] # Берем самое высокое качество
    
    await context.bot.send_chat_action(chat_id=user_id, action=ChatAction.TYPING)
    
    try:
        photo_file = await context.bot.get_file(photo.file_id)
        temp_path = os.path.join(DOWNLOADS_DIR, f"vision_{user_id}_{photo.file_id}.jpg")
        await photo_file.download_to_drive(temp_path)
        
        await process_ai_request(update, context, caption, image_path=temp_path)
    except Exception as e:
        logger.error(f"Vision Handler Error: {e}")
        await update.message.reply_text("⚠️ Не удалось загрузить образ для анализа.")

# --- ОСТАЛЬНЫЕ ХЕНДЛЕРЫ (БЕЗ ИЗМЕНЕНИЙ) ---
# ... (start, handle_text, handle_voice, handle_callback остаются прежними) ...
