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
from services.messages import get_wait_message, DynamicWaitMessage

logger = logging.getLogger(__name__)

async def _safe_menu_edit(query, context, text: str, markup=None):
    """
    🛡 Бронебойная функция: Безопасно заменяет меню.
    Если мы нажимаем кнопку под картинкой/видео/гс - мы убираем кнопки и шлем новый текст.
    Если мы в текстовом меню - просто плавно его редактируем.
    """
    try:
        if query.message.photo or query.message.video or query.message.document or query.message.audio or query.message.voice:
            # Оставляем медиа в чате навсегда, просто убираем кнопки
            try:
                await query.message.edit_reply_markup(reply_markup=None)
            except Exception:
                pass
            # Отправляем новое текстовое меню
            await context.bot.send_message(chat_id=query.from_user.id, text=text, reply_markup=markup, parse_mode='HTML')
        else:
            # Безопасно редактируем текстовое сообщение
            await query.edit_message_text(text=text, reply_markup=markup, parse_mode='HTML')
    except Exception as e:
        logger.warning(f"Safe Menu Edit Warning: {e}")
        try:
            await context.bot.send_message(chat_id=query.from_user.id, text=text, reply_markup=markup, parse_mode='HTML')
        except:
            pass

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    user_id = query.from_user.id
    
    if data == "video_text": return await ask_video_prompt(update, context, "text")
    elif data == "video_image": return await ask_video_prompt(update, context, "image")
    elif data == "feature_video":
        context.user_data['mode'] = None 
        from keyboards.ai_video import get_video_menu_keyboard 
        menu_text = "🎬 <b>Модуль Видео Ai (Kling 3.0 Motion)</b>\n\nВыберите способ генерации:\n📝 <b>По тексту</b> — Опишите сцену, и нейросеть создаст ролик с нуля.\n🖼 <b>По картинке</b> — Нейросеть 'оживит' готовую фотографию."
        await _safe_menu_edit(query, context, menu_text, get_video_menu_keyboard())

    elif data == "profile_tariffs":
        tariffs_text = "\n\n".join(config.TARIFF_INFO.values())
        await _safe_menu_edit(query, context, f"{tariffs_text}\n\n👇 <b>Выберите тариф для подключения:</b>", keyboards.get_subscription_keyboard())
    
    elif data == "profile_support":
        await _safe_menu_edit(query, context, config.MSG_SUPPORT, InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="back_to_profile")]]))

    elif data == "back_to_profile": 
        if query.message.photo or query.message.video or query.message.document:
            try: await query.message.edit_reply_markup(reply_markup=None)
            except: pass
        await show_profile(update, user_id)

    elif data.startswith("buy_"):
        plan = data.split("_")[1]
        await _safe_menu_edit(query, context, f"💳 <b>Оплата тарифа {plan}</b>\n\n{config.PAYMENT_INFO}")

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
            await _safe_menu_edit(query, context, "📂 Архив пуст.", keyboards.get_features_keyboard())

    elif data.startswith("session_"):
        session_id = int(data.split("_")[1])
        db.activate_session(user_id, session_id)
        await query.message.reply_text("📂 <b>Диалог восстановлен.</b>\nЯ помню контекст этой беседы.", parse_mode='HTML')

    elif data == "feature_text":
        context.user_data['mode'] = None
        curr = USER_MODELS.get(user_id, config.DEFAULT_MODEL)
        await _safe_menu_edit(query, context, "💡 <b>ВЫБОР НЕЙРОСЕТИ:</b>", keyboards.get_models_keyboard(user_id, curr))
        
    elif data.startswith("setmodel_"):
        new_model = data.split("setmodel_")[1]
        user_tariff = sheets_mgr.get_user_tariff(user_id)
        if not config_models.is_model_allowed(user_tariff, new_model):
            await query.answer("⛔️ Модель недоступна на вашем тарифе!", show_alert=True)
            return

        USER_MODELS[user_id] = new_model
        context.user_data['mode'] = None
        
        # Если переключали модель под фото - убираем у него кнопки
        if query.message.photo or query.message.video or query.message.document:
            try: await query.message.edit_reply_markup(reply_markup=None)
            except: pass
        else:
            try: await query.message.delete()
            except: pass
        
        all_models = config_models.MODELS_START + config_models.MODELS_PRO + config_models.MODELS_NEO
        model_name = next((name for name, code in all_models if code == new_model), new_model)
        await context.bot.send_message(chat_id=user_id, text=f"🧠 <b>Модель активирована:</b> {model_name}\nМожете писать запрос.", parse_mode='HTML')

    elif data == "feature_design":
        context.user_data['mode'] = None
        curr_img = context.user_data.get('img_model', config.IMG_POLLINATIONS)
        try:
            from keyboards.ai_image import get_image_models_keyboard
            markup = get_image_models_keyboard(user_id, curr_img)
            text = "🎨 <b>СТУДИЯ ДИЗАЙНА vnxORACLE</b>\n\nЯ могу нарисовать всё, что вы представите. Выберите нейросеть, которая лучше всего подходит под вашу задачу:\n\n🔥 <b>Flux 2 Ultra</b> — Лидер 2026. Фотореализм, логотипы, сложные композиции.\n🎨 <b>Midjourney v7</b> — Художественные арты и идеальная детализация.\n🖌 <b>Qwen VL</b> — Пишет текст на картинке без ошибок (постеры, баннеры).\n🌟 <b>DALL-E 4</b> — Креативные концепты и неожиданные решения.\n⚡️ <b>Ideogram 3</b> — Типографика премиум-уровня и дизайнерские шрифты.\n🆓 <b>Pollinations</b> — Быстрая генерация без ограничений.\n\n👇 <i>Нажмите на кнопку, чтобы выбрать:</i>"
        except ImportError:
            markup = keyboards.get_features_keyboard()
            text = "🛠 Модуль изображений в процессе настройки..."
        await _safe_menu_edit(query, context, text, markup)

    elif data.startswith("setimg_"):
        new_model = data.split("setimg_")[1]
        context.user_data['img_model'] = new_model
        context.user_data['mode'] = 'img_wait'
        
        if query.message.photo or query.message.video or query.message.document:
            try: await query.message.edit_reply_markup(reply_markup=None)
            except: pass
        else:
            try: await query.message.delete()
            except: pass
            
        await context.bot.send_message(chat_id=user_id, text=f"🎨 <b>Модель выбрана!</b>\n\n👇 Опишите, что вы хотите увидеть (чем подробнее, тем лучше):", parse_mode='HTML')

    elif data == "photo_vision":
        path = context.user_data.get('last_photo_path')
        caption = context.user_data.get('last_photo_caption') or "Что на этом фото подробно?"

        if not path or not os.path.exists(path):
            await query.answer("⚠️ Файл устарел. Загрузите фото заново.", show_alert=True)
            return

        # 🔥 ОСТАВЛЯЕМ ФОТО, удаляем только кнопки
        try: await query.message.edit_reply_markup(reply_markup=None)
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
        
        # 🔥 ОСТАВЛЯЕМ ФОТО в чате! Оно никуда не исчезнет, просто убираем кнопки.
        try: await query.message.edit_reply_markup(reply_markup=None)
        except Exception as e: logger.warning(f"Message edit markup error: {e}")

        menu_text = (
            "🪄 <b>Режим редактирования активирован!</b>\n\n"
            "Напишите, что нужно изменить на фото.\n\n"
            "Примеры:\n"
            "• 'Сделай небо синим'\n"
            "• 'Добавь радугу'\n"
            "• 'Сделай в мультяшном стиле'\n\n"
            "💡 <i>Для выхода напишите 'отмена'</i>"
        )
        await context.bot.send_message(chat_id=user_id, text=menu_text, parse_mode='HTML')

    elif data == "photo_upscale":
        path = context.user_data.get('last_photo_path')
        task_id = context.user_data.get('last_task_id') # 🔥 Забираем Task ID
        
        if not path or not os.path.exists(path):
            await query.answer("⚠️ Файл устарел или утерян сервером. Загрузите фото заново.", show_alert=True)
            return
        
        # 🔥 ОСТАВЛЯЕМ ФОТО в чате!
        try: await query.message.edit_reply_markup(reply_markup=None)
        except Exception as e: logger.warning(f"Message edit markup error: {e}")
            
        prefix = "✨ <b>Улучшение качества...</b>\n"
        wait_msg = await context.bot.send_message(chat_id=user_id, text=f"{prefix}{get_wait_message('image')}", parse_mode='HTML')
        
        loader = DynamicWaitMessage(wait_msg, "image", prefix)
        loader.start()
        
        try:
            from services.kie_client import kie_studio
            # 🔥 Вызываем умный гибридный пайплайн (KIE + ESRGAN)
            upscaled_url, provider = await kie_studio.upscale_pipeline(task_id=task_id, image_path=path)
        finally:
            loader.stop()
        
        if upscaled_url:
            from keyboards.ai_image import get_post_generation_keyboard
            # 🔥 Красиво выводим название движка
            provider_text = "KIE Upscale" if provider == "KIE" else "Real-ESRGAN"
            caption = f"✨ <b>Качество успешно улучшено!</b>\n⚙️ <i>Движок: {provider_text}</i>"
            
            await context.bot.send_photo(chat_id=user_id, photo=upscaled_url, caption=caption, reply_markup=get_post_generation_keyboard(), parse_mode='HTML')
            await wait_msg.delete()
        else:
            # 🔥 Дружелюбный ответ, если нет ключа для пользовательских фото
            if not task_id and not getattr(config, 'REPLICATE_API_KEY', None):
                await wait_msg.edit_text("⚠️ <b>Внешний Upscale не настроен.</b>\nДля улучшения ваших фото добавьте <code>REPLICATE_API_KEY</code> (Replicate.com) в файл config.py.", parse_mode='HTML')
            else:
                await wait_msg.edit_text("❌ Ошибка Upscale. Нейросеть отклонила запрос. Проверьте логи.", parse_mode='HTML')

    elif data.startswith("img_ratio_"):
        ratio = data.split("_")[2] 
        prompt = context.user_data.get('img_prompt')
        
        if context.user_data.get('mode') == 'img_ratio_wait':
            context.user_data['mode'] = None
            
        if not prompt:
            await query.answer("⚠️ Ошибка: промпт устарел. Начните заново.", show_alert=True)
            return
            
        try: await query.message.delete()
        except: pass
        from handlers.media import generate_image
        await generate_image(update, context, prompt, ratio)
        
    elif data == "feature_audio":
        await _safe_menu_edit(query, context, "🎤 <b>АУДИО СЕРВИСЫ:</b>", keyboards.get_audio_keyboard())
        
    elif data == "audio_tts":
        curr_voice = context.user_data.get('voice_id', config.DEFAULT_VOICE)
        await _safe_menu_edit(query, context, "🗣 <b>ВЫБЕРИТЕ ГОЛОС ДИКТОРА:</b>", keyboards.get_voice_selection_keyboard(curr_voice))
        
    elif data.startswith("setvoice_"):
        context.user_data['voice_id'] = data.split("setvoice_")[1]
        context.user_data['mode'] = 'tts_wait'
        await query.answer("🎙 Голос выбран")
        
        if query.message.photo or query.message.video or query.message.document:
            try: await query.message.edit_reply_markup(reply_markup=None)
            except: pass
        else:
            try: await query.message.delete()
            except: pass
            
        await context.bot.send_message(chat_id=user_id, text="🗣 <b>Режим диктора активен.</b>\nПришлите текст для озвучки:", parse_mode='HTML')
        
    elif data == "audio_tts_again":
        context.user_data['mode'] = 'tts_wait'
        if query.message.photo or query.message.video or query.message.document or query.message.audio or query.message.voice:
            try: await query.message.edit_reply_markup(reply_markup=None)
            except: pass
        await context.bot.send_message(chat_id=user_id, text="🎤 Жду текст для озвучки:", parse_mode='HTML')
        
    elif data == "audio_sfx":
        context.user_data['mode'] = 'sfx_wait'
        if query.message.photo or query.message.video or query.message.document or query.message.audio or query.message.voice:
            try: await query.message.edit_reply_markup(reply_markup=None)
            except: pass
        await context.bot.send_message(chat_id=user_id, text="🔊 <b>Опишите звук (на английском):</b>", parse_mode='HTML')

    elif data == "feature_openclaw":
        from services.openclaw_core import claw_manager
        status_info = await claw_manager.check_status()
        
        if user_id == config.ADMIN_ID:
            claw_text = f"🦞 <b>OpenClaw: Интерфейс vnxMATRIX</b>\n\nАвтономный Агент для управления ядром. Доступны терминал, файлы и процессы.\n\n{status_info}\n🔓 <b>Уровень: АРХИТЕКТОР (ROOT)</b>\n\n👇 <b>Введите команду:</b>"
        else:
            claw_text = f"🦞 <b>Твой Цифровой Секретарь</b>\n\nЯ умею искать информацию в интернете, собирать данные с сайтов и автоматизировать рутину.\n\n🛡 <b>Уровень: БЕЗОПАСНЫЙ</b>\nДоступен поиск в сети и анализ данных.\n\n👇 <b>Что мне найти или сделать для тебя?</b>"
        
        context.user_data['mode'] = 'openclaw_wait'
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад в меню", callback_data="back_to_features")]])
        await _safe_menu_edit(query, context, claw_text, markup)
        
    elif data == "mode_chat_reset":
        context.user_data['mode'] = None
        db.create_session(user_id, title="Новый диалог")
        
        if query.message.photo or query.message.video or query.message.document or query.message.audio or query.message.voice:
            try: await query.message.edit_reply_markup(reply_markup=None)
            except: pass
        
        await context.bot.send_message(chat_id=user_id, text="💬 <b>Текстовый режим восстановлен.</b>", parse_mode='HTML')

    elif data == "back_to_features":
        await _safe_menu_edit(query, context, "🧩 <b>МЕНЮ ВОЗМОЖНОСТЕЙ:</b>", keyboards.get_features_keyboard())
    
    try: await query.answer()
    except: pass
