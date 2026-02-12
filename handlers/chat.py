import os
import logging
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes
import config
from loader import sheets_mgr, ai_engine, db, USER_MODELS
import keyboards

logger = logging.getLogger(__name__)

async def process_ai_request(update: Update, context: ContextTypes.DEFAULT_TYPE, input_text: str, image_path: str = None):
    user_id = update.effective_user.id
    user_tariff = sheets_mgr.get_user_tariff(user_id)
    if not user_tariff: 
        from .admin import send_paywall
        return await send_paywall(update)

    await context.bot.send_chat_action(chat_id=user_id, action=ChatAction.TYPING)
    session_id = db.get_active_session(user_id)
    
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

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if config.ARCHIVE_CHANNEL_ID:
        try:
            await context.bot.forward_message(chat_id=config.ARCHIVE_CHANNEL_ID, from_chat_id=update.effective_chat.id, message_id=update.message.message_id)
            await update.message.reply_text("✅ <b>Объект сохранен.</b>", parse_mode='HTML')
        except: pass

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from .admin import send_paywall, show_profile
    from .media import generate_image
    from .audio import handle_tts_request, handle_sfx_request
    
    user_id = update.effective_user.id
    text = update.message.text.strip()
    
    # Системные перехватчики
    if text == config.BTN_NEW_DIALOG:
        context.user_data['mode'] = None
        db.create_session(user_id, title="Новый диалог")
        await update.message.reply_text("♻️ <b>Контекст очищен. Начата новая сессия.</b>", parse_mode='HTML')
        return

    if text == config.BTN_HISTORY:
        context.user_data['mode'] = None
        markup = keyboards.get_history_keyboard(user_id)
        if not markup: await update.message.reply_text("📂 Архив пуст.")
        else: await update.message.reply_text("💾 <b>ИСТОРИЯ ЧАТОВ:</b>", reply_markup=markup, parse_mode='HTML')
        return

    if text == config.BTN_CHANGE_MODEL:
        context.user_data['mode'] = None
        await update.message.reply_text("🧩 <b>МЕНЮ ВОЗМОЖНОСТЕЙ:</b>", reply_markup=keyboards.get_features_keyboard(), parse_mode='HTML')
        return
        
    if text == config.BTN_PROFILE:
        context.user_data['mode'] = None
        await show_profile(update, user_id)
        return
        
    if text == config.BTN_TARIFFS:
        context.user_data['mode'] = None
        await send_paywall(update)
        return

    # Обработка режимов
    mode = context.user_data.get('mode')
    if mode == 'tts_wait':
        await handle_tts_request(update, context, text)
        return
    if mode == 'sfx_wait':
        await handle_sfx_request(update, context, text)
        context.user_data['mode'] = None
        return
    if mode == 'img_wait':
        await generate_image(update, context, text)
        context.user_data['mode'] = None
        return

    if text.startswith("/img "):
        await generate_image(update, context, text[5:])
        return

    await process_ai_request(update, context, text)
