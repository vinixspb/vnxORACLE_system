import os
import logging
import html
import keyboards
import config
import urllib.parse
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes
from loader import sheets_mgr, ai_engine, db, USER_MODELS

from keyboards.ai_video import get_video_menu_keyboard

logger = logging.getLogger(__name__)

# --- Вспомогательная функция для безопасной отправки текста ---
def escape_html(text):
    if text is None:
        return ""
    return html.escape(str(text))

async def process_ai_request(update: Update, context: ContextTypes.DEFAULT_TYPE, input_text: str, image_path: str = None):
    """
    Главная функция обработки AI запросов.
    Поддерживает Vision (передача изображений).
    """
    if not update.message:
        return
        
    user_id = update.effective_user.id
    user_tariff = sheets_mgr.get_user_tariff(user_id)
    
    if not user_tariff: 
        from .admin import send_paywall
        return await send_paywall(update)

    await context.bot.send_chat_action(chat_id=user_id, action=ChatAction.TYPING)
    session_id = db.get_active_session(user_id)
    
    # Создаем заголовок для новой сессии
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
        
        final_text = f"{safe_response}\n\n<blockquote>⚙️ {model_name} | 🎫 {tokens_spent} | ∑ {db.get_total_tokens(user_id)}</blockquote>"
        await update.message.reply_text(final_text, parse_mode='HTML')
        
    except Exception as e:
        logger.error(f"AI Error: {e}")
        await update.message.reply_text("⚠️ Ошибка нейро-интерфейса.")
        
    finally:
        # Удаляем временное фото только если это НЕ активная Vision сессия
        if image_path and os.path.exists(image_path) and not context.user_data.get('vision_mode'):
            try:
                os.remove(image_path)
            except:
                pass


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сохранение документов в архив"""
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
# 📝 ГЛАВНЫЙ ОБРАБОТЧИК ТЕКСТА
# =========================================================
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    from .admin import send_paywall, show_profile
    from .audio import handle_tts_request, handle_sfx_request
    
    user_id = update.effective_user.id
    text = update.message.text.strip()
    
    # =========================================================
    # 🔥 ПРОВЕРКА VISION MODE (ПРОДОЛЖЕНИЕ РАБОТЫ С ФОТО)
    # =========================================================
    if context.user_data.get('vision_mode'):
        # Команды для выхода из Vision режима
        if text.lower() in ['стоп', 'закончить', 'новое фото', 'другое фото', 'хватит', 'выход']:
            context.user_data['vision_mode'] = False
            context.user_data['last_photo_path'] = None
            await update.message.reply_text(
                "✅ <b>Работа с фото завершена.</b>\n\nМожете загрузить новое изображение или продолжить текстовый диалог.",
                parse_mode='HTML'
            )
            return
        
        # Иначе продолжаем работать с фото
        image_path = context.user_data.get('last_photo_path')
        if image_path and os.path.exists(image_path):
            logger.info(f"👁 Vision Mode: продолжение работы с {image_path}")
            await process_ai_request(update, context, text, image_path=image_path)
            return
        else:
            # Если файл потерялся
            context.user_data['vision_mode'] = False
            await update.message.reply_text(
                "⚠️ Изображение больше недоступно. Загрузите новое.",
                parse_mode='HTML'
            )
            return
    
    # =========================================================
    # 🎹 СИСТЕМНЫЕ КНОПКИ МЕНЮ
    # =========================================================
    if text == config.BTN_NEW_DIALOG:
        context.user_data['mode'] = None
        context.user_data['vision_mode'] = False  # 🔥 Сбрасываем Vision
        db.create_session(user_id, title="Новый диалог")
        await update.message.reply_text("♻️ <b>Контекст очищен. Начата новая сессия.</b>", parse_mode='HTML')
        return

    if text == config.BTN_HISTORY:
        context.user_data['mode'] = None
        markup = keyboards.get_history_keyboard(user_id)
        if not markup:
            await update.message.reply_text("📂 Архив пуст.")
        else:
            await update.message.reply_text("💾 <b>ИСТОРИЯ ЧАТОВ:</b>", reply_markup=markup, parse_mode='HTML')
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

    # =========================================================
    # 🦞 OPENCLAW АГЕНТ
    # =========================================================
    if text == config.BTN_OPENCLAW:
        context.user_data['mode'] = 'openclaw_wait'
        context.user_data['vision_mode'] = False  # 🔥 Выходим из Vision
        from services.openclaw_core import claw_manager
        status_info = await claw_manager.check_status()
        await update.message.reply_text(
            f"🦞 <b>Твой Цифровой Секретарь</b>\n\n{status_info}\n\n👇 <b>Что мне найти или сделать для тебя?</b>", 
            parse_mode='HTML'
        )
        return


    # =========================================================
    # 🪄 РЕЖИМ IMG2IMG (РЕДАКТИРОВАНИЕ ФОТО)
    # =========================================================
    if mode == 'img2img_wait':
     # Проверяем команду отмены
       if text.lower() in ['отмена', 'cancel', 'стоп', 'выход']:
        context.user_data['mode'] = None
        await update.message.reply_text("✅ Режим редактирования отменен.", parse_mode='HTML')
        return
    
    # Берем исходное фото
    source_path = context.user_data.get('img2img_source_path')
    
    if not source_path or not os.path.exists(source_path):
        await update.message.reply_text(
            "⚠️ Исходное фото потеряно. Загрузите новое.",
            parse_mode='HTML'
        )
        context.user_data['mode'] = None
        return
    
    # Сбрасываем режим
    context.user_data['mode'] = None
    
    # Сохраняем промпт и путь
    context.user_data['img_prompt'] = text
    context.user_data['img2img_mode'] = True  # Флаг что это img2img
    
    # Показываем выбор формата
    from keyboards.ai_image import get_ratio_keyboard
    await update.message.reply_text(
        f"📐 <b>Выберите формат результата:</b>\n\n"
        f"<i>Изменение: {text[:50]}...</i>",
        reply_markup=get_ratio_keyboard(),
        parse_mode='HTML'
    )
    return
    
    # =========================================================
    # 🎨 РЕЖИМ ГЕНЕРАЦИИ ИЗОБРАЖЕНИЙ
    # =========================================================
    if text.startswith("/img "):
        prompt = text[5:]
        context.user_data['mode'] = None
        context.user_data['vision_mode'] = False  # 🔥 Выходим из Vision
        context.user_data['img_prompt'] = prompt
        
        from keyboards.ai_image import get_ratio_keyboard
        await update.message.reply_text(
            f"📐 <b>Выберите формат изображения:</b>\n\n<i>Промпт: {prompt[:50]}...</i>",
            reply_markup=get_ratio_keyboard(),
            parse_mode='HTML'
        )
        return

    # =========================================================
    # 🎬 ОБРАБОТКА АКТИВНЫХ РЕЖИМОВ
    # =========================================================
    mode = context.user_data.get('mode')
    
    if mode == 'openclaw_wait':
        wait_msg = await update.message.reply_text("🦞 <i>Агент принял задачу...</i>", parse_mode='HTML')
        from services.openclaw_core import claw_manager
        
        # Определяем Brave API ключ по тарифу
        user_tariff = sheets_mgr.get_user_tariff(user_id)
        if user_tariff == 'NEO':
            b_key = config.BRAVE_API_KEY_NEO
        elif user_tariff == 'PRO':
            b_key = config.BRAVE_API_KEY_PRO
        else:
            b_key = config.BRAVE_API_KEY_START

        # Выполняем задачу
        if text.lower() in ['статус', 'status', 'ping']:
            ans = await claw_manager.check_status()
        else:
            ans = await claw_manager.execute_task(text, user_id, update.effective_user.full_name, brave_key=b_key)
            
        # Безопасная отправка (защита от Timeout)
        try:
            await wait_msg.edit_text(ans, parse_mode='HTML')
        except Exception as e:
            logger.warning(f"⚠️ Telegram Timeout: {e}")
            try:
                await update.message.reply_text(ans, parse_mode='HTML')
            except Exception as e2:
                logger.error(f"❌ Критический сбой: {e2}")
        return
    if mode == 'img2img_wait':
        # Проверяем команду отмены
        if text.lower() in ['отмена', 'cancel', 'стоп', 'выход']:
            context.user_data['mode'] = None
            await update.message.reply_text("✅ Режим редактирования отменен.", parse_mode='HTML')
            return
        
        # Берем исходное фото
        source_path = context.user_data.get('img2img_source_path')
        
        if not source_path or not os.path.exists(source_path):
            await update.message.reply_text(
                "⚠️ Исходное фото потеряно. Загрузите новое.",
                parse_mode='HTML'
            )
            context.user_data['mode'] = None
            return
        
        # Сбрасываем режим
        context.user_data['mode'] = None
        
        # Сохраняем промпт и путь
        context.user_data['img_prompt'] = text
        context.user_data['img2img_mode'] = True  # Флаг что это img2img
        
        # Показываем выбор формата
        from keyboards.ai_image import get_ratio_keyboard
        await update.message.reply_text(
            f"📐 <b>Выберите формат результата:</b>\n\n"
            f"<i>Изменение: {text[:50]}...</i>",
            reply_markup=get_ratio_keyboard(),
            parse_mode='HTML'
        )
        return
        
    if mode == 'img_wait':
        prompt = text
        context.user_data['mode'] = None
        context.user_data['img_prompt'] = prompt
        
        from keyboards.ai_image import get_ratio_keyboard
        await update.message.reply_text(
            f"📐 <b>Выберите формат изображения:</b>\n\n<i>Промпт: {prompt[:50]}...</i>",
            reply_markup=get_ratio_keyboard(),
            parse_mode='HTML'
        )
        return

    if mode == 'video_text_wait':
        from handlers.video import handle_video_text_request
        await handle_video_text_request(update, context, text)
        return

    # =========================================================
    # 🧠 СТАНДАРТНЫЙ ЗАПРОС К AI
    # =========================================================
   await process_ai_request(update, context, text)
