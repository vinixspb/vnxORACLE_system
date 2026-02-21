from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
import logging

import config
import config_models  # Наш реестр моделей
from loader import sheets_mgr, db, USER_MODELS
import keyboards

# Импортируем функции логики из соседних модулей
from .admin import show_profile

logger = logging.getLogger(__name__)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    user_id = query.from_user.id

    # =========================================================
    # 👤 ПРОФИЛЬ, ТАРИФЫ И ОПЛАТА
    # =========================================================
    if data == "profile_tariffs":
        # Собираем красивый текст о тарифах из конфига
        tariffs_text = "\n\n".join(config.TARIFF_INFO.values())
        await query.edit_message_text(
            f"{tariffs_text}\n\n👇 <b>Выберите тариф для подключения:</b>",
            reply_markup=keyboards.get_subscription_keyboard(),
            parse_mode='HTML'
        )
    
    elif data == "profile_support":
        # Показываем контакты поддержки
        await query.edit_message_text(
            config.MSG_SUPPORT,
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="back_to_profile")]])
        )

    elif data == "back_to_profile":
        # Возвращаемся в профиль (используем функцию из admin.py)
        await show_profile(update, user_id)

    elif data.startswith("buy_"):
        # Обработка нажатия "Купить"
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
        # Удаление сессии
        session_id = int(data.split("_")[1])
        db.delete_session(user_id, session_id)
        await query.answer("🗑 Диалог удален")
        
        # Обновляем список или пишем, что пусто
        markup = keyboards.get_history_keyboard(user_id, mode="delete")
        if markup:
            await query.edit_message_reply_markup(reply_markup=markup)
        else:
            await query.edit_message_text("📂 Архив пуст.", reply_markup=keyboards.get_features_keyboard())

    elif data.startswith("session_"):
        # Восстановление сессии
        session_id = int(data.split("_")[1])
        db.activate_session(user_id, session_id)
        await query.message.reply_text("📂 <b>Диалог восстановлен.</b>\nЯ помню контекст этой беседы.", parse_mode='HTML')

    # =========================================================
    # 🧠 ТЕКСТОВЫЕ МОДЕЛИ (LLM)
    # =========================================================
    elif data == "feature_text":
        context.user_data['mode'] = None
        curr = USER_MODELS.get(user_id, config.DEFAULT_MODEL)
        # Показываем меню, адаптированное под тариф юзера
        await query.edit_message_text(
            "💡 <b>ВЫБОР НЕЙРОСЕТИ:</b>",
            reply_markup=keyboards.get_models_keyboard(user_id, curr),
            parse_mode='HTML'
        )
    elif data.startswith("setmodel_"):
        new_model = data.split("setmodel_")[1]
        
        # --- ПРОВЕРКА ПРАВ (через реестр) ---
        user_tariff = sheets_mgr.get_user_tariff(user_id)
        if not config_models.is_model_allowed(user_tariff, new_model):
            await query.answer("⛔️ Модель недоступна на вашем тарифе!", show_alert=True)
            return

        USER_MODELS[user_id] = new_model
        context.user_data['mode'] = None
        try: await query.message.delete()
        except: pass
        
        # --- ПОИСК ИМЕНИ (через реестр) ---
        # Собираем полный список всех возможных моделей для поиска имени
        all_models = config_models.MODELS_START + config_models.MODELS_PRO + config_models.MODELS_NEO
        
        # Ищем красивое имя. Если не нашли, используем ID.
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
        curr_img = context.user_data.get('img_model', config.DEFAULT_IMG_MODEL)
        
        # Проверяем, есть ли модуль клавиатур для картинок (если мы его создали)
        try:
            from keyboards.ai_image import get_image_models_keyboard
            markup = get_image_models_keyboard(user_id, curr_img)
            text = "🎨 <b>СТУДИЯ ДИЗАЙНА</b>\n\nВыберите нейросеть для генерации:"
        except ImportError:
            # Заглушка, если файл еще не создан
            markup = keyboards.get_features_keyboard()
            text = "🛠 Модуль изображений в процессе настройки..."

        await query.edit_message_text(text, reply_markup=markup, parse_mode='HTML')

    elif data.startswith("setimg_"):
        new_model = data.split("setimg_")[1]
        context.user_data['img_model'] = new_model
        context.user_data['mode'] = 'img_wait' # Включаем режим ожидания промпта
        
        try: await query.message.delete()
        except: pass
        
        await context.bot.send_message(
            chat_id=user_id,
            text=f"🎨 <b>Модель выбрана!</b>\nРежим: <code>{new_model}</code>\n\n👇 Опишите, что вы хотите увидеть:",
            parse_mode='HTML'
        )
    # =========================================================
    # 📐 ВЫБОР ФОРМАТА ИЗОБРАЖЕНИЯ И ЗАПУСК ГЕНЕРАЦИИ
    # =========================================================
    elif data.startswith("img_ratio_"):
        # Извлекаем формат из callback_data (например, "9:16")
        ratio = data.split("_")[2] 
        
        # Достаем сохраненный промпт
        prompt = context.user_data.get('img_prompt')
        if not prompt:
            await query.answer("⚠️ Ошибка: промпт устарел. Начните заново.", show_alert=True)
            return
            
        # Удаляем сообщение с кнопками формата
        await query.message.delete()
        
        # Запускаем генерацию и передаем туда формат
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
        
        # Получаем живой статус из системы
        status_info = await claw_manager.check_status()
        
        # Разделяем интерфейс: для Админа — сервер, для Юзера — облачный помощник
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
        # Кнопка "Вернуться в чат" из аудио-режима
        context.user_data['mode'] = None
        db.create_session(user_id, title="Новый диалог")
        await query.message.reply_text("💬 <b>Текстовый режим восстановлен.</b>", parse_mode='HTML')

    elif data == "back_to_features":
        await query.edit_message_text(
            "🧩 <b>МЕНЮ ВОЗМОЖНОСТЕЙ:</b>",
            reply_markup=keyboards.get_features_keyboard(),
            parse_mode='HTML'
        )
    
    # Завершаем обработку (убираем часики на кнопке)
    try: await query.answer()
    except: pass
