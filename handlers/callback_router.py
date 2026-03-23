import logging
import os
import config
import config_models
from loader import sheets_mgr, db, USER_MODELS
import keyboards
from handlers.video import ask_video_prompt
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from .admin import show_profile

logger = logging.getLogger(__name__)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    user_id = query.from_user.id
    
    # =========================================================
    # 📸 ОБРАБОТКА ВХОДЯЩИХ ФОТО И ДЕЙСТВИЯ С НИМИ
    # =========================================================
    elif data == "photo_vision":
        path = context.user_data.get('last_photo_path')
        caption = context.user_data.get('last_photo_caption') or "Что на этом фото подробно?"

        if not path or not os.path.exists(path):
            await query.answer("⚠️ Файл устарел. Загрузите фото заново.", show_alert=True)
            return

        # Удаляем сообщение с картинкой
        try:
            await query.message.delete()
        except:
            pass
            
        from handlers.chat import process_ai_request
        await process_ai_request(update, context, caption, image_path=path)

    elif data == "photo_edit":
        path = context.user_data.get('last_photo_path')
        caption = context.user_data.get('last_photo_caption')

        if not path or not os.path.exists(path):
            await query.answer("⚠️ Файл устарел. Загрузите фото заново.", show_alert=True)
            return

        # 🔥 ВКЛЮЧАЕМ РЕЖИМ IMG2IMG
        context.user_data['mode'] = 'img2img_wait'
        context.user_data['img2img_source_path'] = path  # Сохраняем путь к исходному фото
        
        # 🔥 БЕЗОПАСНОСТЬ: Жестко удаляем старое фото перед отправкой текста
        try:
            await query.message.delete()
        except Exception as e:
            logger.warning(f"Message delete error: {e}")

        await context.bot.send_message(
            chat_id=user_id,
            text="🪄 <b>Режим редактирования активирован!</b>\n\nНапишите, что нужно изменить на фото.\n\nПримеры:\n• 'Сделай небо синим'\n• 'Добавь радугу'\n• 'Измени цвет машины на красный'\n\n💡 <i>Для выхода напишите 'отмена'</i>",
            parse_mode='HTML'
        )

    elif data == "photo_upscale":
        path = context.user_data.get('last_photo_path')
        
        if not path or not os.path.exists(path):
            await query.answer("⚠️ Файл устарел. Загрузите фото заново.", show_alert=True)
            return
        
        # 🔥 БЕЗОПАСНОСТЬ: Жестко удаляем старое фото
        try:
            await query.message.delete()
        except Exception as e:
            logger.warning(f"Message delete error: {e}")
            
        from services.messages import get_wait_message
        wait_text = get_wait_message("image")
        
        wait_msg = await context.bot.send_message(
            chat_id=user_id,
            text=f"✨ <b>Улучшение качества...</b>\n{wait_text}",
            parse_mode='HTML'
        )
        
        from services.kie_client import kie_studio
        upscaled_url = await kie_studio.upscale_image(path)
        
        if upscaled_url:
            from keyboards.ai_image import get_post_generation_keyboard
            await context.bot.send_photo(
                chat_id=user_id,
                photo=upscaled_url,
                caption="✨ <b>Качество успешно улучшено! (Upscaled)</b>",
                reply_markup=get_post_generation_keyboard(),
                parse_mode='HTML'
            )
            await wait_msg.delete()
        else:
            await wait_msg.edit_text("❌ Ошибка Upscale. Нейросеть отклонила запрос. Проверьте логи.")

    # =========================================================
    # 📐 ВЫБОР ФОРМАТА ИЗОБРАЖЕНИЯ И ЗАПУСК ГЕНЕРАЦИИ
    # =========================================================
    elif data.startswith("img_ratio_"):
        ratio = data.split("_")[2] 
        prompt = context.user_data.get('img_prompt')
        
        if not prompt:
            await query.answer("⚠️ Ошибка: промпт устарел. Начните заново.", show_alert=True)
            return
            
        await query.message.delete()
        from handlers.media import generate_image
        await generate_image(update, context, prompt, ratio)
        
    # =========================================================
    # 🎤 АУДИО СЕРВИСЫ
    # =========================================================
    elif data == "feature_audio":
        await query.edit_message_text(
            "🎤 <b>АУДИО СЕРВИСЫ:</b>",
            reply_markup=keyboards.get_audio_keyboard(),
            parse_mode='HTML'
        )
        
    elif data == "audio_tts":
        curr_voice = context.user_data.get('voice_id', config.DEFAULT_VOICE)
        await query.edit_message_text(
            "🗣 <b>ВЫБЕРИТЕ ГОЛОС ДИКТОРА:</b>",
            reply_markup=keyboards.get_voice_selection_keyboard(curr_voice),
            parse_mode='HTML'
        )
        
    elif data.startswith("setvoice_"):
        context.user_data['voice_id'] = data.split("setvoice_")[1]
        context.user_data['mode'] = 'tts_wait'
        await query.answer("🎙 Голос выбран")
        await query.message.reply_text(
            "🗣 <b>Режим диктора активен.</b>\nПришлите текст для озвучки:", 
            parse_mode='HTML'
        )
        
    elif data == "audio_tts_again":
        context.user_data['mode'] = 'tts_wait'
        await query.message.reply_text("🎤 Жду текст для озвучки:", parse_mode='HTML')
        
    elif data == "audio_sfx":
        context.user_data['mode'] = 'sfx_wait'
        await query.message.reply_text("🔊 <b>Опишите звук (на английском):</b>", parse_mode='HTML')

    # =========================================================
    # 🦞 OPENCLAW (АВТОНОМНЫЙ ИИ-АГЕНТ)
    # =========================================================
    elif data == "feature_openclaw":
        from services.openclaw_core import claw_manager
        status_info = await claw_manager.check_status()
        
        if user_id == config.ADMIN_ID:
            claw_text = (
                f"🦞 <b>OpenClaw: Интерфейс vnxMATRIX</b>\n\n"
                f"Автономный Агент для управления ядром. Доступны терминал, файлы и процессы.\n\n"
                f"{status_info}\n"
                f"🔓 <b>Уровень: АРХИТЕКТОР (ROOT)</b>\n\n"
                f"👇 <b>Введите команду:</b>"
            )
        else:
            claw_text = (
                f"🦞 <b>Твой Цифровой Секретарь</b>\n\n"
                f"Я умею искать информацию в интернете, собирать данные с сайтов и автоматизировать рутину.\n\n"
                f"🛡 <b>Уровень: БЕЗОПАСНЫЙ</b>\n"
                f"Доступен поиск в сети и анализ данных.\n\n"
                f"👇 <b>Что мне найти или сделать для тебя?</b>"
            )
        
        context.user_data['mode'] = 'openclaw_wait'
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад в меню", callback_data="back_to_features")]])
        await query.edit_message_text(claw_text, reply_markup=markup, parse_mode='HTML')
        
    # =========================================================
    # ⚙️ ОБЩИЕ ДЕЙСТВИЯ
    # =========================================================
    elif data == "mode_chat_reset":
        context.user_data['mode'] = None
        db.create_session(user_id, title="Новый диалог")
        await query.message.reply_text("💬 <b>Текстовый режим восстановлен.</b>", parse_mode='HTML')

    elif data == "back_to_features":
        await query.edit_message_text(
            "🧩 <b>МЕНЮ ВОЗМОЖНОСТЕЙ:</b>",
            reply_markup=keyboards.get_features_keyboard(),
            parse_mode='HTML'
        )
    
    try: 
        await query.answer()
    except: 
        pass
