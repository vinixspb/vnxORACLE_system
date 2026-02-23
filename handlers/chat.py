import os
import logging
import html
import keyboards
import config
import urllib.parse # <-- ДОБАВИЛИ ДЛЯ ГЕНЕРАЦИИ ССЫЛОК
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes
from loader import sheets_mgr, ai_engine, db, USER_MODELS


from keyboards.ai_video import get_video_menu_keyboard

logger = logging.getLogger(__name__)

# --- Вспомогательная функция для безопасной отправки текста ---
def escape_html(text):
    if text is None: return ""
    return html.escape(str(text))

async def process_ai_request(update: Update, context: ContextTypes.DEFAULT_TYPE, input_text: str, image_path: str = None):
    # ... (весь твой код process_ai_request оставляем без изменений) ...
    if not update.message: return
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
        ai_response, tokens_spent = await ai_engine.get_response(
            messages=full_context, 
            model=model, 
            user_tariff=user_tariff, 
            image_path=image_path
        )
        
        db.add_message(session_id, "assistant", ai_response, model=model)
        db.update_tokens(user_id, tokens_spent)
        
        model_name = model.split('/')[-1].replace(":free", "")
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

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ... (твой код handle_document без изменений) ...
    if config.ARCHIVE_CHANNEL_ID:
        try:
            await context.bot.forward_message(
                chat_id=config.ARCHIVE_CHANNEL_ID, 
                from_chat_id=update.effective_chat.id, 
                message_id=update.message.message_id
            )
            await update.message.reply_text("✅ <b>Объект сохранен в архив.</b>", parse_mode='HTML')
        except Exception as e:
            logger.error(f"Archive Error: {e}")

# =========================================================
# 📝 ГЛАВНЫЙ ОБРАБОТЧИК ТЕКСТА (ОБНОВЛЕН)
# =========================================================
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    from .admin import send_paywall, show_profile
    from .audio import handle_tts_request, handle_sfx_request
    
    user_id = update.effective_user.id
    text = update.message.text.strip()
    
    # --- СИСТЕМНЫЕ КНОПКИ МЕНЮ ---
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

    # 🦞 ПЕРЕХВАТЧИК КНОПКИ OPENCLAW (Reply Keyboard)
    if text == config.BTN_OPENCLAW:
        context.user_data['mode'] = 'openclaw_wait'
        from services.openclaw_core import claw_manager
        status_info = await claw_manager.check_status()
        await update.message.reply_text(
            f"🦞 <b>Твой Цифровой Секретарь</b>\n\n{status_info}\n\n👇 <b>Что мне найти или сделать для тебя?</b>", 
            parse_mode='HTML'
        )
        return

    # --- ОБРАБОТКА АКТИВНЫХ РЕЖИМОВ ---
    mode = context.user_data.get('mode')
    
    if mode == 'openclaw_wait':
        wait_msg = await update.message.reply_text("🦞 <i>Агент принял задачу...</i>", parse_mode='HTML')
        from services.openclaw_core import claw_manager
        
        # 🧠 1. Проверяем тариф и берем соответствующий ключ Brave
        user_tariff = sheets_mgr.get_user_tariff(user_id)
        if user_tariff == 'NEO':
            b_key = config.BRAVE_API_KEY_NEO
        elif user_tariff == 'PRO':
            b_key = config.BRAVE_API_KEY_PRO
        else:
            b_key = config.BRAVE_API_KEY_START

        # 🧠 2. Выполняем задачу
        if text.lower() in ['статус', 'status', 'ping']:
            ans = await claw_manager.check_status()
        else:
            ans = await claw_manager.execute_task(text, user_id, update.effective_user.full_name, brave_key=b_key)
            
        # 🛡 3. Безопасная отправка ответа (Защита от TimedOut)
        try:
            await wait_msg.edit_text(ans, parse_mode='HTML')
        except Exception as e:
            logger.warning(f"⚠️ Ошибка редактирования сообщения (Таймаут Telegram): {e}")
            try:
                # Если Telegram разорвал соединение, отправляем новым сообщением
                await update.message.reply_text(ans, parse_mode='HTML')
            except Exception as e2:
                logger.error(f"❌ Критический сбой отправки ответа: {e2}")
                
        return

  # 🎨 ПЕРЕХВАТЧИК ГЕНЕРАЦИИ ИЗОБРАЖЕНИЙ (ШАГ 1: ЗАПРОС ФОРМАТА)
    if mode == 'img_wait' or text.startswith("/img "):
        prompt = text[5:] if text.startswith("/img ") else text
        
        # Сбрасываем режим
        context.user_data['mode'] = None
        
        # Сохраняем промпт в памяти пользователя, чтобы достать его после клика
        context.user_data['img_prompt'] = prompt
        
        # Вызываем клавиатуру с выбором формата
        from keyboards.ai_image import get_ratio_keyboard
        await update.message.reply_text(
            f"📐 <b>Выберите формат изображения:</b>\n\n"
            f"<i>Промпт: {prompt[:50]}...</i>",
            reply_markup=get_ratio_keyboard(),
            parse_mode='HTML'
        )
        return

    # ПЕРЕХВАТЧИК ПРОМПТА ДЛЯ ВИДЕО
    if mode == 'video_text_wait':
        from handlers.video import handle_video_text_request
        await handle_video_text_request(update, context, text)
        return


    
    # --- СТАНДАРТНЫЙ ЗАПРОС К ИИ ---
    await process_ai_request(update, context, text)
