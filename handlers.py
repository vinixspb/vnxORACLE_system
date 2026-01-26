import os
import logging
import random
import aiohttp
import uuid
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import BadRequest
from telegram.ext import ContextTypes
from telegram.constants import ChatAction

import config
from loader import sheets_mgr, ai_engine, db, USER_MODELS, audio_studio
import keyboards

logger = logging.getLogger(__name__)
DOWNLOADS_DIR = "downloads"

async def process_ai_request(update: Update, context: ContextTypes.DEFAULT_TYPE, input_text: str, image_path: str = None):
    user_id = update.effective_user.id
    user_tariff = sheets_mgr.get_user_tariff(user_id)
    if not user_tariff: return await send_paywall(update)

    await context.bot.send_chat_action(chat_id=user_id, action=ChatAction.TYPING)
    session_id = db.get_active_session(user_id)
    
    # Авто-заголовок
    history = db.get_history(session_id, limit=1)
    if not history:
        clean_title = input_text.replace("[Audio Input]: ", "")[:30]
        db.update_session_title(session_id, clean_title)
    
    db.add_message(session_id, "user", input_text)
    history_depth = config.LIMITS.get(user_tariff, 10)
    full_context = db.get_history(session_id, limit=history_depth)
    model = USER_MODELS.get(user_id, config.DEFAULT_MODEL)

    try:
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
        if image_path and os.path.exists(image_path):
            try: os.remove(image_path)
            except: pass

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if sheets_mgr.get_user_tariff(user_id) not in ['PRO', 'NEO']:
        return await update.message.reply_text("🧬 <b>VISION MODULE</b>\nДоступен на уровнях PRO и NEO.", parse_mode='HTML')
    
    photo = update.message.photo[-1]
    caption = update.message.caption or "Что на этом фото?"
    try:
        file = await context.bot.get_file(photo.file_id)
        path = os.path.join(DOWNLOADS_DIR, f"v_{uuid.uuid4().hex[:8]}.jpg")
        await file.download_to_drive(path)
        await process_ai_request(update, context, caption, image_path=path)
    except Exception as e: logger.error(f"Vision Error: {e}")

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    user_id = query.from_user.id

    # --- Навигация по Архиву ---
    if data == "history_manage":
        await query.edit_message_reply_markup(reply_markup=keyboards.get_history_keyboard(user_id, mode="delete"))
    elif data == "history_back":
        await query.edit_message_reply_markup(reply_markup=keyboards.get_history_keyboard(user_id, mode="view"))
    elif data.startswith("del_"):
        db.delete_session(user_id, int(data.split("_")[1]))
        await query.answer("🗑 Удалено")
        markup = keyboards.get_history_keyboard(user_id, mode="delete")
        if markup: await query.edit_message_reply_markup(reply_markup=markup)
        else: await query.edit_message_text("📂 Архив пуст.", reply_markup=keyboards.get_features_keyboard())
    
    # --- Остальные Callbacks ---
    elif data.startswith("session_"):
        db.activate_session(user_id, int(data.split("_")[1]))
        await query.message.reply_text("📂 <b>Диалог восстановлен.</b>", parse_mode='HTML')
    elif data == "feature_audio":
        await query.edit_message_text("🎤 <b>АУДИО СЕРВИСЫ:</b>", reply_markup=keyboards.get_audio_keyboard(), parse_mode='HTML')
    elif data == "audio_tts":
        await query.edit_message_text("🗣 <b>ВЫБЕРИТЕ ГОЛОС:</b>", reply_markup=keyboards.get_voice_selection_keyboard(), parse_mode='HTML')
    elif data.startswith("setvoice_"):
        context.user_data['voice_id'] = data.split("_")[1]
        context.user_data['mode'] = 'tts_wait'
        await query.message.reply_text("🗣 <b>Режим диктора активен.</b>\nЖду текст:", parse_mode='HTML')
    
    await query.answer()

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    
    if text == config.BTN_HISTORY:
        markup = keyboards.get_history_keyboard(user_id)
        if not markup: await update.message.reply_text("📂 Архив пуст.")
        else: await update.message.reply_text("💾 <b>ИСТОРИЯ ЧАТОВ:</b>", reply_markup=markup, parse_mode='HTML')
        return
    # ... (start, handle_voice, handle_document остаются как в прошлых версиях)
