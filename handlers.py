import os
import logging
import uuid
import time
import random
import aiohttp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ChatAction
from telegram.ext import ContextTypes

import config
from loader import sheets_mgr, ai_engine, db, USER_MODELS, audio_studio
import keyboards
# Если вы уже перешли на новую структуру папок, то импорт keyboards верный.
# Если нет, убедитесь, что файлы лежат правильно.

logger = logging.getLogger(__name__)
DOWNLOADS_DIR = "downloads"
if not os.path.exists(DOWNLOADS_DIR):
    os.makedirs(DOWNLOADS_DIR)

# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---

async def send_paywall(update: Update):
    """Отправка сообщения об ограничении доступа"""
    await update.message.reply_text(config.MSG_NO_SUB, reply_markup=keyboards.get_subscription_keyboard(), parse_mode='HTML')

async def generate_image(update: Update, context: ContextTypes.DEFAULT_TYPE, prompt: str):
    """Генерация изображений через Pollinations (Free) - вызывается командой /img"""
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
    """Ядро обработки запросов: Текст + Контекст + Зрение"""
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

# --- МУЛЬТИМЕДИА ХЕНДЛЕРЫ ---

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Vision Module"""
    user_id = update.effective_user.id
    if sheets_mgr.get_user_tariff(user_id) not in ['PRO', 'NEO']:
        return await update.message.reply_text("🧬 <b>VISION MODULE</b>\nДоступен на уровнях PRO и NEO.", parse_mode='HTML')
    
    photo = update.message.photo[-1]
    caption = update.message.caption or "Что на этом фото?"
    
    try:
        file = await context.bot.get_file(photo.file_id)
        path = os.path.join(DOWNLOADS_DIR, f"v_{user_id}_{uuid.uuid4().hex[:8]}.jpg")
        await file.download_to_drive(path)
        await process_ai_request(update, context, caption, image_path=path)
    except Exception as e: 
        logger.error(f"Vision Error: {e}")
        await update.message.reply_text("⚠️ Ошибка загрузки изображения.")

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Whisper STT"""
    user_id = update.effective_user.id
    if not sheets_mgr.get_user_tariff(user_id): return await send_paywall(update)
    
    await context.bot.send_chat_action(chat_id=user_id, action=ChatAction.TYPING)
    file_path = os.path.join(DOWNLOADS_DIR, f"v_{user_id}_{uuid.uuid4().hex[:8]}.ogg")
    
    try:
        voice_file = await context.bot.get_file(update.message.voice.file_id)
        await voice_file.download_to_drive(file_path)
        transcript = await ai_engine.transcribe_audio(file_path)
        
        if transcript:
            await update.message.reply_text(f"🎤 <i>Распознано:</i> \"{transcript}\"", parse_mode='HTML')
            ai_input = f"[Audio Input]: {transcript}"
            await process_ai_request(update, context, ai_input)
        else:
            await update.message.reply_text("🎤 <b>Не удалось распознать голос.</b>", parse_mode='HTML')
            
    except Exception as e:
        logger.error(f"Voice Error: {e}")
        await update.message.reply_text("⚠️ Ошибка обработки голоса.")
    finally:
        if os.path.exists(file_path):
            try: os.remove(file_path)
            except: pass

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Archive Vault"""
    if config.ARCHIVE_CHANNEL_ID:
        try:
            await context.bot.forward_message(chat_id=config.ARCHIVE_CHANNEL_ID, from_chat_id=update.effective_chat.id, message_id=update.message.message_id)
            await update.message.reply_text("✅ <b>Объект сохранен.</b>", parse_mode='HTML')
        except: pass

# --- ОБРАБОТЧИКИ СООБЩЕНИЙ ---

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    
    # Системные кнопки (Новое меню 4 кнопки)
    sys_buttons = [config.BTN_NEW_DIALOG, config.BTN_HISTORY, config.BTN_PROFILE, config.BTN_CHANGE_MODEL]
    
    if text in sys_buttons:
        context.user_data['mode'] = None # Сброс режима
        
        if text == config.BTN_NEW_DIALOG:
            db.create_session(user_id, title="Новый диалог")
            await update.message.reply_text("♻️ <b>Контекст очищен. Начата новая сессия.</b>", parse_mode='HTML')
            
        elif text == config.BTN_HISTORY:
            markup = keyboards.get_history_keyboard(user_id)
            if not markup: await update.message.reply_text("📂 Архив пуст.")
            else: await update.message.reply_text("💾 <b>ИСТОРИЯ ЧАТОВ:</b>", reply_markup=markup, parse_mode='HTML')
            
        elif text == config.BTN_CHANGE_MODEL:
            await update.message.reply_text("🧩 <b>МЕНЮ ВОЗМОЖНОСТЕЙ:</b>", reply_markup=keyboards.get_features_keyboard(), parse_mode='HTML')
            
        elif text == config.BTN_PROFILE:
            # Логика профиля
            user_tariff = sheets_mgr.get_user_tariff(user_id)
            if not user_tariff: return await send_paywall(update)
            
            status = f"✅ {user_tariff}"
            total_tokens = db.get_total_tokens(user_id)
            current_model = USER_MODELS.get(user_id, config.DEFAULT_MODEL)
            
            profile_text = (
                f"👤 <b>МОЙ ПРОФИЛЬ</b>\n"
                f"ID: <code>{user_id}</code>\n"
                f"Статус: <b>{status}</b>\n"
                f"Расход токенов: <b>{total_tokens}</b>\n"
                f"Активная модель: <code>{current_model}</code>"
            )
            await update.message.reply_text(profile_text, reply_markup=keyboards.get_profile_keyboard(), parse_mode='HTML')

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
    if mode == 'img_wait': # Режим ожидания промпта для картинки
        # Здесь мы должны вызвать генерацию картинки
        # Пока используем старую функцию generate_image (Pollinations), 
        # но в будущем здесь будет вызов services.image_engine
        await generate_image(update, context, text)
        context.user_data['mode'] = None
        return

    if text.startswith("/img "):
        await generate_image(update, context, text[5:])
        return

    await process_ai_request(update, context, text)


# --- CALLBACKS (ВОТ ЗДЕСЬ БЫЛА ОШИБКА) ---

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    user_id = query.from_user.id

    # 1. Профиль и Тарифы
    if data == "profile_tariffs":
        tariffs_text = "\n\n".join(config.TARIFF_INFO.values())
        await query.edit_message_text(f"{tariffs_text}\n\n👇 <b>Выберите тариф для подключения:</b>", reply_markup=keyboards.get_subscription_keyboard(), parse_mode='HTML')
    
    elif data == "profile_support":
        await query.edit_message_text(config.MSG_SUPPORT, parse_mode='HTML', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="back_to_profile")]]))

    elif data == "back_to_profile":
        user_tariff = sheets_mgr.get_user_tariff(user_id)
        if not user_tariff:
            await query.edit_message_text(config.MSG_NO_SUB, reply_markup=keyboards.get_subscription_keyboard(), parse_mode='HTML')
            return

        status = f"✅ {user_tariff}"
        total_tokens = db.get_total_tokens(user_id)
        current_model = USER_MODELS.get(user_id, config.DEFAULT_MODEL)
        profile_text = (
            f"👤 <b>МОЙ ПРОФИЛЬ</b>\n"
            f"ID: <code>{user_id}</code>\n"
            f"Статус: <b>{status}</b>\n"
            f"Расход токенов: <b>{total_tokens}</b>\n"
            f"Активная модель: <code>{current_model}</code>"
        )
        await query.edit_message_text(profile_text, reply_markup=keyboards.get_profile_keyboard(), parse_mode='HTML')

    # 2. Покупка
    elif data.startswith("buy_"):
        plan = data.split("_")[1]
        await query.edit_message_text(f"💳 <b>Оплата тарифа {plan}</b>\n\n{config.PAYMENT_INFO}", parse_mode='HTML')

    # 3. Навигация Архива
    elif data == "history_manage":
        await query.edit_message_reply_markup(reply_markup=keyboards.get_history_keyboard(user_id, mode="delete"))
    elif data == "history_back":
        await query.edit_message_reply_markup(reply_markup=keyboards.get_history_keyboard(user_id, mode="view"))
    elif data.startswith("del_"):
        db.delete_session(user_id, int(data.split("_")[1]))
        await query.answer("🗑 Удалено")
        markup = keyboards.get_history_keyboard(user_id, mode="delete")
        if markup: await query.edit_message_reply_markup(reply_markup=markup)
        else: await query.edit_message_text("📂 Архив пуст.", reply_markup=keyboards.get_features_keyboard())
    elif data.startswith("session_"):
        db.activate_session(user_id, int(data.split("_")[1]))
        await query.message.reply_text("📂 <b>Диалог восстановлен.</b>", parse_mode='HTML')

    # 4. Меню и Модели (ТЕКСТ)
    elif data == "feature_text":
        context.user_data['mode'] = None
        curr = USER_MODELS.get(user_id, config.DEFAULT_MODEL)
        await query.edit_message_text("💡 <b>ВЫБОР МОДЕЛИ:</b>", reply_markup=keyboards.get_models_keyboard(curr), parse_mode='HTML')
    
    elif data.startswith("setmodel_"):
        # Логика: Меняем модель -> Удаляем меню -> Пишем подтверждение
        new_model = data.split("setmodel_")[1]
        USER_MODELS[user_id] = new_model
        context.user_data['mode'] = None
        
        # Удаляем меню
        try: await query.message.delete()
        except: pass
        
        # Ищем красивое имя модели
        model_name = next((name for name, code in config.MODELS_LIST if code == new_model), new_model)
        await context.bot.send_message(
            chat_id=user_id, 
            text=f"🧠 <b>Модель активирована:</b> {model_name}\nМожете писать запрос.", 
            parse_mode='HTML'
        )

    # 5. Студия Дизайна (ИЗОБРАЖЕНИЯ)
    elif data == "feature_design":
        context.user_data['mode'] = None
        # Для использования get_image_models_keyboard убедитесь, что она импортирована
        # Если вы еще не создали keyboards/ai_image.py, удалите эту ветку или замените на заглушку
        try:
            curr_img = context.user_data.get('img_model', config.DEFAULT_IMG_MODEL)
            await query.edit_message_text(
                "🎨 <b>СТУДИЯ ДИЗАЙНА</b>\n\nВыберите нейросеть для генерации:", 
                reply_markup=keyboards.get_image_models_keyboard(user_id, curr_img), 
                parse_mode='HTML'
            )
        except AttributeError:
            await query.answer("🔧 Модуль в разработке")

    elif data.startswith("setimg_"):
        new_model = data.split("setimg_")[1]
        context.user_data['img_model'] = new_model
        context.user_data['mode'] = 'img_wait' # Включаем режим ожидания промпта
        
        try: await query.message.delete()
        except: pass
        
        await context.bot.send_message(
            chat_id=user_id,
            text=f"🎨 <b>Модель выбрана!</b>\nРежим: <code>{new_model}</code>\n\nОпишите, что вы хотите увидеть:",
            parse_mode='HTML'
        )

    # 6. Аудио
    elif data == "feature_audio":
        await query.edit_message_text("🎤 <b>АУДИО СЕРВИСЫ:</b>", reply_markup=keyboards.get_audio_keyboard(), parse_mode='HTML')
    elif data == "audio_tts":
        await query.edit_message_text("🗣 <b>ВЫБЕРИТЕ ГОЛОС:</b>", reply_markup=keyboards.get_voice_selection_keyboard(), parse_mode='HTML')
    elif data.startswith("setvoice_"):
        context.user_data['voice_id'] = data.split("setvoice_")[1]
        context.user_data['mode'] = 'tts_wait'
        await query.answer("🎙 Голос выбран")
        await query.message.reply_text("🗣 <b>Режим диктора активен.</b>\nПришлите текст для озвучки:", parse_mode='HTML')
    elif data == "audio_tts_again":
        context.user_data['mode'] = 'tts_wait'
        await query.message.reply_text("🎤 Жду текст:", parse_mode='HTML')
    elif data == "audio_sfx":
        context.user_data['mode'] = 'sfx_wait'
        await query.message.reply_text("🔊 <b>Опишите звук (на англ):</b>", parse_mode='HTML')
    elif data == "mode_chat_reset":
        context.user_data['mode'] = None
        db.create_session(user_id, title="Новый диалог")
        await query.message.reply_text("💬 <b>Текстовый режим.</b>", parse_mode='HTML')

    # 7. Общие возвраты
    elif data == "back_to_features":
        await query.edit_message_text("🧩 <b>МЕНЮ ВОЗМОЖНОСТЕЙ:</b>", reply_markup=keyboards.get_features_keyboard(), parse_mode='HTML')
    
    try: await query.answer()
    except: pass


# --- ВНУТРЕННИЕ ФУНКЦИИ ---

async def handle_tts_request(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    user_id = update.effective_user.id
    voice = context.user_data.get('voice_id', config.DEFAULT_VOICE)
    await context.bot.send_chat_action(chat_id=user_id, action=ChatAction.RECORD_VOICE)
    
    audio_data, engine, is_fallback = await audio_studio.text_to_speech(text, voice)
    context.user_data['mode'] = None 
    
    if audio_data:
        warn = "⚠️ <i>Резервный ИИ</i>\n" if is_fallback else ""
        caption = f"🎙 <b>Готово!</b>\n\n{warn}<blockquote>⚙️ {engine} | 🎫 {len(text)}</blockquote>"
        keyboard = [[
            InlineKeyboardButton("🎤 Озвучить еще", callback_data="audio_tts_again"),
            InlineKeyboardButton("💬 Вернуться в чат", callback_data="mode_chat_reset")
        ]]
        await update.message.reply_audio(
            audio=audio_data, caption=caption, parse_mode='HTML', 
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        db.update_tokens(user_id, len(text))
    else:
        await update.message.reply_text("❌ Ошибка синтеза.")

async def handle_sfx_request(update: Update, context: ContextTypes.DEFAULT_TYPE, desc: str):
    user_id = update.effective_user.id
    await context.bot.send_chat_action(chat_id=user_id, action=ChatAction.RECORD_VOICE)
    sfx = await audio_studio.generate_sfx(desc)
    if sfx:
        await update.message.reply_audio(audio=sfx, caption=f"🔊 <b>{desc}</b>", parse_mode='HTML')
    else:
        await update.message.reply_text("⚠️ Ошибка SFX.")

# --- КОМАНДА START ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    user = update.effective_user
    user_id = user.id
    
    # Сначала проверяем доступ (Paywall)
    tariff = sheets_mgr.get_user_tariff(user_id)
    if not tariff:
        await update.message.reply_text(config.MSG_NO_SUB, reply_markup=keyboards.get_subscription_keyboard(), parse_mode='HTML')
        return
    
    # Если доступ есть — создаем сессию и показываем интерфейс
    db.create_session(user_id, title="Новый чат")
    
    first_name = user.first_name or "Пользователь"
    welcome_text = (
        f"👋 <b>Здравствуйте, {first_name}!</b>\n\n"
        "Я — <b>vnxORACLE</b>, ваш персональный нейро-ассистент.\n"
        "Готов решать задачи любой сложности: от анализа фото до генерации кода.\n\n"
        "👇 <b>С чего начнем?</b>"
    )
    
    # Показываем нижнее меню (4 кнопки)
    await update.message.reply_text("🖥 <b>Терминал запущен.</b>", reply_markup=keyboards.get_main_keyboard(), parse_mode='HTML')
    
    # Показываем главное меню возможностей (Inline)
    await update.message.reply_text(welcome_text, reply_markup=keyboards.get_features_keyboard(), parse_mode='HTML')
