import os
import logging
import html  # Добавили для безопасной отправки текста
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes
import config
from loader import sheets_mgr, ai_engine, db, USER_MODELS
import keyboards

logger = logging.getLogger(__name__)

# --- Вспомогательная функция для очистки HTML ---
def escape_html(text):
    return html.escape(str(text))

async def process_ai_request(update: Update, context: ContextTypes.DEFAULT_TYPE, input_text: str, image_path: str = None):
    if not update.message: return # Защита от пустых апдейтов
    user_id = update.effective_user.id
    user_tariff = sheets_mgr.get_user_tariff(user_id)
    
    if not user_tariff: 
        from .admin import send_paywall
        return await send_paywall(update)

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
        ai_response, tokens_spent = await ai_engine.get_response(
            messages=full_context, 
            model=model, 
            user_tariff=user_tariff, 
            image_path=image_path
        )
        
        db.add_message(session_id, "assistant", ai_response, model=model)
        db.update_tokens(user_id, tokens_spent)
        
        model_name = model.split('/')[-1].replace(":free", "")
        # Экранируем ответ AI, чтобы не было ошибок парсинга HTML
        safe_response = escape_html(ai_response)
        
        final_text = (f"{safe_response}\n\n<blockquote>⚙️ {model_name} | 🎫 {tokens_spent} | ∑ {db.get_total_tokens(user_id)}</blockquote>")
        await update.message.reply_text(final_text, parse_mode='HTML')
    except Exception as e:
        logger.error(f"AI Error: {e}")
        await update.message.reply_text("⚠️ Ошибка нейро-интерфейса.")
    finally:
        if image_path and os.path.exists(image_path):
            try: os.remove(image_path)
            except: pass

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ЗАЩИТА: Если это не текстовое сообщение — выходим
    if not update.message or not update.message.text:
        return

    from .admin import send_paywall, show_profile
    from .media import generate_image
    from .audio import handle_tts_request, handle_sfx_request
    
    user_id = update.effective_user.id
    text = update.message.text.strip()
    
    # Системные перехватчики
    if text == config.BTN_NEW_DIALOG:
        context.user_data['mode'] = None
        db.create_session(user_id, title="Новый диалог")
        await update.message.reply_text("♻️ <b>Контекст очищен.</b>", parse_mode='HTML')
        return

    if text == config.BTN_CHANGE_MODEL:
        context.user_data['mode'] = None
        await update.message.reply_text("🧩 <b>МЕНЮ:</b>", reply_markup=keyboards.get_features_keyboard(), parse_mode='HTML')
        return
    
    # (Остальные кнопки оставляем как были...)
    if text == config.BTN_PROFILE:
        context.user_data['mode'] = None
        await show_profile(update, user_id)
        return

    # Режимы
    mode = context.user_data.get('mode')
    
    if mode == 'openclaw_wait':
        wait_msg = await update.message.reply_text("🦞 <i>Агент принял задачу...</i>", parse_mode='HTML')
        from services.openclaw_core import claw_manager
        
        if text.lower() in ['статус', 'status', 'ping']:
            ans = await claw_manager.check_status()
        else:
            ans = await claw_manager.execute_task(text, user_id)
            
        await wait_msg.edit_text(ans, parse_mode='HTML')
        return

    # Обычный запрос к AI
    await process_ai_request(update, context, text)
