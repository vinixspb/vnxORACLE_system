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
from services.messages import get_wait_message

logger = logging.getLogger(__name__)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    user_id = query.from_user.id
    
    # =========================================================
    # 🎬 МЕНЮ ВИДЕО AI (РЕЖИССЕРСКАЯ)
    # =========================================================
    if data == "video_text":
        return await ask_video_prompt(update, context, "text")
        
    elif data == "video_image":
        return await ask_video_prompt(update, context, "image")

    elif data == "feature_video":
        context.user_data['mode'] = None 
        from keyboards.ai_video import get_video_menu_keyboard 
        
        menu_text = (
            "🎬 <b>Модуль Видео Ai (Kling 3.0 Motion)</b>\n\n"
            "Выберите способ генерации:\n"
            "📝 <b>По тексту</b> — Опишите сцену, и нейросеть создаст ролик с нуля.\n"
            "🖼 <b>По картинке</b> — Нейросеть 'оживит' готовую фотографию."
        )
        
        await query.edit_message_text(
            text=menu_text,
            reply_markup=get_video_menu_keyboard(),
            parse_mode='HTML'
        )

    # =========================================================
    # 👤 ПРОФИЛЬ, ТАРИФЫ И ОПЛАТА
    # =========================================================
    elif data == "profile_tariffs":
        tariffs_text = "\n\n".join(config.TARIFF_INFO.values())
        await query.edit_message_text(
            f"{tariffs_text}\n\n👇 <b>Выберите тариф для подключения:</b>",
            reply_markup=keyboards.get_subscription_keyboard(),
            parse_mode='HTML'
        )
    
    elif data == "profile_support":
        await query.edit_message_text(
            config.MSG_SUPPORT,
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="back_to_profile")]])
        )

    elif data == "back_to_profile":
        await show_profile(update, user_id)

    elif data.startswith("buy_"):
        plan = data.split("_")[1]
        await query.edit_message_text(
            f"💳 <b>Оплата тарифа {plan}</b>\n\n{config.PAYMENT_INFO}",
            parse_mode='HTML'
        )

    # =========================================================
    # 🗄 УПРАВЛЕНИЕ ИСТОРИЕЙ (АРХИВ)
    # =========================================================
    elif data == "history_manage":
        await query.edit_message_reply_markup(reply_markup=keyboards.get_history_keyboard(user_id, mode="delete"))

    elif data == "history_back":
        await query.edit_message_reply_markup(reply_markup=keyboards.get_history_keyboard(user_id, mode="view"))

    elif data.startswith("del_"):
        session_id = int(data.split("_")[1])
        db.delete_session(user_id, session_id)
        await query.answer("🗑 Диалог удален")
        
        markup = keyboards.get_history_keyboard(user_id, mode="delete")
        if markup:
            await query.edit_message_reply_markup(reply_markup=markup)
        else:
            await query.edit_message_text("📂 Архив пуст.", reply_markup=keyboards.get_features_keyboard())

    elif data.startswith("session_"):
        session_id = int(data.split("_")[1])
        db.activate_session(user_id, session_id)
        await query.message.reply_text("📂 <b>Диалог восстановлен.</b>\nЯ помню контекст этой беседы.", parse_mode='HTML')

    # =========================================================
    # 🧠 ТЕКСТОВЫЕ МОДЕЛИ (LLM)
    # =========================================================
    elif data == "feature_text":
        context.user_data['mode'] = None
        curr = USER_MODELS.get(user_id, config.DEFAULT_MODEL)
        await query.edit_message_text(
            "💡 <b>ВЫБОР НЕЙРОСЕТИ:</b>",
            reply_markup=keyboards.get_models_keyboard(user_id, curr),
            parse_mode='HTML'
        )
        
    elif data.startswith("setmodel_"):
        new_model = data.split("setmodel_")[1]
        
        user_tariff = sheets_mgr.get_user_tariff(user_id)
        if not config_models.is_model_allowed(user_tariff, new_model):
            await query.answer("⛔️ Модель недоступна на вашем тарифе!", show_alert=True)
            return

        USER_MODELS[user_id] = new_model
        context.user_data['mode'] = None
        try: await query.message.delete()
        except: pass
        
        all_models = config_models.MODELS_START + config_models.MODELS_PRO + config_models.MODELS_NEO
        model_name = next((name for name, code in all_models if code == new_model), new_model)
        
        await context.bot.send_message(
            chat_id=user_id, 
            text=f"🧠 <b>Модель активирована:</b> {model_name}\nМожете писать запрос.", 
            parse_mode='HTML'
        )

    # =========================================================
    # 🎨 ИЗОБРАЖЕНИЯ (DESIGN STUDIO)
    # =========================================================
    elif data == "feature_design":
        context.user_data['mode'] = None
        curr_img = context.user_data.get('img_model', config.IMG_POLLINATIONS)
        
        try:
            from keyboards.ai_image import get_image_models_keyboard
            markup = get_image_models_keyboard(user_id, curr_img)
            
            text = (
                "🎨 <b>СТУДИЯ ДИЗАЙНА vnxORACLE</b>\n\n"
                "Я могу нарисовать всё, что вы представите. Выберите "
                "нейросеть, которая лучше всего подходит под вашу задачу:\n\n"
                "⚡️ <b>Flux Pro</b> — Идеально понимает сложные запросы и делает логотипы.\n"
                "🍌 <b>Nano Banana</b> — Создает сочные, яркие и невероятно креативные арты.\n"
                "🖌 <b>Qwen 2.0</b> — Элитная типографика и постеры (пишет текст на картинке).\n"
                "🌌 <b>Seedream</b> — Лучший выбор для волшебных миров и фэнтези.\n"
                "🆓 <b>Pollinations</b> — Простая и сверхбыстрая модель без ограничений.\n\n"
                "👇 <i>Нажмите на кнопку, чтобы выбрать:</i>"
            )
        except ImportError:
            markup = keyboards.get_features_keyboard()
            text = "🛠 Модуль изображений в процессе настройки..."

        await query.edit_message_text(text, reply_markup=markup, parse_mode='HTML')

    elif data.startswith("setimg_"):
        new_model = data.split("setimg_")[1]
        context.user_data['img_model'] = new_model
        context.user_data['mode'] = 'img_wait'
        
        try: await query.message.delete()
        except: pass
        
        await context.bot.send_message(
            chat_id=user_id,
            text=f"🎨 <b>Модель выбрана!</b>\n\n👇 Опишите, что вы хотите увидеть (чем подробнее, тем лучше):",
            parse_mode='HTML'
        )

    # =========================================================
    # 📸 ОБРАБОТКА ВХОДЯЩИХ ФОТО И ДЕЙСТВИЯ С НИМИ
    # =========================================================
    elif data == "photo_vision":
        path = context.user_data.get('last_photo_path')
        caption = context.user_data.get('last_photo_caption') or "Что на этом фото подробно?"

        if not path or not os.path.exists(path):
            await query.answer("⚠️ Файл устарел. Загрузите фото заново.", show_alert=True)
            return

        try: await query.message.delete()
        except: pass
            
        from handlers.chat import process_ai_request
        await process_ai_request(update, context, caption, image_path=path)

    elif data == "photo_edit":
        path = context.user_data.get('last_photo_path')

        if not path or not os.path.exists(path):
            await query.answer("⚠️ Файл устарел. Загрузите фото заново.", show_alert=True)
            return

        context.user_data['mode'] = 'img2img_wait'
        context.user_data['img2img_source_path'] = path  
        
        try: await query.message.delete()
        except Exception as e: logger.warning(f"Message delete error: {e}")

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
        
        try: await query.message.delete()
        except Exception as e: logger.warning(f"Message delete error: {e}")
            
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
            
        try: await query.message.delete()
        except: pass
        
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
