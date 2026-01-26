import os
import logging
import random
import aiohttp
import uuid
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import BadRequest
from telegram.ext import ContextTypes
from telegram.constants import ChatAction

import config
from loader import sheets_mgr, ai_engine, db, USER_MODELS, audio_studio
import keyboards

logger = logging.getLogger(__name__)

# Папка для временных файлов
DOWNLOADS_DIR = "downloads"
if not os.path.exists(DOWNLOADS_DIR):
    os.makedirs(DOWNLOADS_DIR)

# --- Вспомогательные функции ---

async def send_paywall(update: Update):
    """Вывод сообщения о необходимости подписки"""
    await update.message.reply_text(
        config.MSG_NO_SUB, 
        reply_markup=keyboards.get_subscription_keyboard(), 
        parse_mode='HTML'
    )

async def generate_image(update: Update, context: ContextTypes.DEFAULT_TYPE, prompt: str):
    """Генерация изображений через Pollinations AI"""
    user_id = update.effective_user.id
    await context.bot.send_chat_action(chat_id=user_id, action=ChatAction.UPLOAD_PHOTO)
    
    enhanced_prompt = f"{prompt}, highly detailed, 8k, cinematic lighting, cyberpunk aesthetic"
    seed = random.randint(1, 999999)
    image_url = f"https://image.pollinations.ai/prompt/{enhanced_prompt}?seed={seed}&width=1024&height=1024&nologo=true"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as resp:
                if resp.status == 200:
                    data = await resp.read()
                    await update.message.reply_photo(
                        photo=data, 
                        caption=f"🎨 <b>Art by vnxORACLE</b>\nPrompt: <i>{prompt}</i>",
                        parse_mode='HTML'
                    )
                else:
                    await update.message.reply_text("⚠️ Сбой визуализации. Матрица нестабильна.")
    except Exception as e:
        logger.error(f"Img Error: {e}")
        await update.message.reply_text("⚠️ Ошибка связи с нейро-холстом.")

async def process_ai_request(update: Update, context: ContextTypes.DEFAULT_TYPE, input_text: str, image_path: str = None):
    """Ядро обработки: Текст + Контекст + Зрение"""
    user_id = update.effective_user.id
    user_tariff = sheets_mgr.get_user_tariff(user_id)
    if not user_tariff: return await send_paywall(update)

    await context.bot.send_chat_action(chat_id=user_id, action=ChatAction.TYPING)
    session_id = db.get_active_session(user_id)
    
    # Автоматическое именование сессии
    history = db.get_history(session_id, limit=1)
    if not history:
        clean_title = input_text.replace("[Audio Input]: ", "")[:30]
        db.update_session_title(session_id, clean_title)
    
    db.add_message(session_id, "user", input_text)
    history_depth = config.LIMITS.get(user_tariff, 10)
    full_context = db.get_history(session_id, limit=history_depth)
    model = USER_MODELS.get(user_id, config.DEFAULT_MODEL)

    try:
        # Запрос к AI Engine
        ai_response, tokens_spent = await ai_engine.get_response(full_context, model, image_path=image_path)
        
        db.add_message(session_id, "assistant", ai_response, model=model)
        db.update_tokens(user_id, tokens_spent)
        
        model_name = model.split('/')[-1].replace(":free", "")
        total_acc = db.get_total_tokens(user_id)
        
        final_text = (f"{ai_response}\n\n"
                     f"<blockquote>⚙️ {model_name} | 🎫 {tokens_spent} | ∑ {total_acc}</blockquote>")
        
        await update.message.reply_text(final_text, parse_mode='HTML')
    except Exception as e:
        logger.error(f"AI Error: {e}")
        await update.message.reply_text("⚠️ Ошибка нейро-интерфейса. Сигнал потерян.")
    finally:
        # Безопасная очистка временных файлов
        if image_path and os.path.exists(image_path):
            try: os.remove(image_path)
            except: pass

# --- МУЛЬТИМЕДИА ХЕНДЛЕРЫ ---

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """👁 Vision Module: Анализ фото"""
    user_id = update.effective_user.id
    user_tariff = sheets_mgr.get_user_tariff(user_id)
    
    if user_tariff not in ['PRO', 'NEO']:
        return await update.message.reply_text(
            "🧬 <b>VISION MODULE</b>\n\nАнализ доступен только на уровнях <b>PRO</b> и <b>NEO</b>.", 
            parse_mode='HTML'
        )

    caption = update.message.caption or "Проанализируй это изображение."
    photo = update.message.photo[-1]
    
    try:
        photo_file = await context.bot.get_file(photo.file_id)
        # Уникальное имя файла через UUID
        file_name = f"vision_{user_id}_{uuid.uuid4().hex[:8]}.jpg"
        temp_path = os.path.join(DOWNLOADS_DIR, file_name)
        
        await photo_file.download_to_drive(temp_path)
        await process_ai_request(update, context, caption, image_path=temp_path)
    except Exception as e:
        logger.error(f"Vision Error: {e}")
        await update.message.reply_text("⚠️ Не удалось загрузить образ.")

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🎤 Whisper Module: STT"""
    user_id = update.effective_user.id
    if not sheets_mgr.get_user_tariff(user_id): return await send_paywall(update)
    
    await context.bot.send_chat_action(chat_id=user_id, action=ChatAction.TYPING)
    try:
        voice_file = await context.bot.get_file(update.message.voice.file_id)
        file_name = f"v_{user_id}_{uuid.uuid4().hex[:8]}.ogg"
        file_path = os.path.join(DOWNLOADS_DIR, file_name)
        
        await voice_file.download_to_drive(file_path)
        transcript = await ai_engine.transcribe_audio(file_path)
        
        if os.path.exists(file_path): os.remove(file_path)
        
        if transcript:
            await update.message.reply_text(f"🎤 <i>Распознано:</i> \"{transcript}\"", parse_mode='HTML')
            await process_ai_request(update, context, f"[Audio Input]: {transcript}")
    except Exception as e:
        logger.error(f"Voice Error: {e}")

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🗄 The Vault: Архивация документов/видео"""
    if config.ARCHIVE_CHANNEL_ID:
        try:
            await context.bot.forward_message(
                chat_id=config.ARCHIVE_CHANNEL_ID, 
                from_chat_id=update.effective_chat.id, 
                message_id=update.message.message_id
            )
            await update.message.reply_text("✅ <b>Объект сохранен в Хранилище.</b>", parse_mode='HTML')
        except: pass

# --- ОСНОВНЫЕ КОМАНДЫ ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    user_id = update.effective_user.id
    tariff = sheets_mgr.get_user_tariff(user_id)
    
    if not tariff:
        await update.message.reply_text(config.MSG_WELCOME, parse_mode='HTML')
        await update.message.reply_text(config.MSG_NO_SUB, reply_markup=keyboards.get_subscription_keyboard(), parse_mode='HTML')
        return
    
    db.create_session(user_id, title="Новый чат")
    await update.message.reply_text(
        f"👁 <b>vnxORACLE: ONLINE</b>\nВаш уровень: <b>{tariff}</b>", 
        reply_markup=keyboards.get_main_keyboard(), 
        parse_mode='HTML'
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    user_tariff = sheets_mgr.get_user_tariff(user_id)

    # Режимы ожидания
    mode = context.user_data.get('mode')
    if mode == 'tts_wait':
        await handle_tts_request(update, context, text)
        return
    if mode == 'sfx_wait':
        await handle_sfx_request(update, context, text)
        context.user_data['mode'] = None 
        return

    # Системные кнопки (Reply Keyboard)
    if text == config.BTN_TARIFFS:
        msg = (
            "💳 <b>ТАРИФНЫЕ ПЛАНЫ vnxMATRIX</b>\n\n"
            "💠 <b>START:</b> 190₽ / 1 месяц\n"
            "⚡️ <b>PRO:</b> 590₽ / 1 месяц\n"
            "🧬 <b>NEO:</b> 990₽ / 1 месяц\n\n"
            "<i>Все тарифы предоставляют доступ к мощностям нейросетей на 30 дней.</i>"
        )
        await update.message.reply_text(msg, reply_markup=keyboards.get_subscription_keyboard(), parse_mode='HTML')
        return

    if text == config.BTN_NEW_DIALOG:
        db.create_session(user_id, title="Новый диалог")
        await update.message.reply_text("♻️ <b>Новый диалог создан.</b>", parse_mode='HTML')
        return

    if text == config.BTN_HISTORY:
        markup = keyboards.get_history_keyboard(user_id)
        if not markup: await update.message.reply_text("📂 Архив пуст.")
        else: await update.message.reply_text("💾 <b>ИСТОРИЯ ЧАТОВ:</b>", reply_markup=markup, parse_mode='HTML')
        return

    if text == config.BTN_CHANGE_MODEL:
        await update.message.reply_text("🧩 <b>МЕНЮ ВОЗМОЖНОСТЕЙ:</b>", reply_markup=keyboards.get_features_keyboard(), parse_mode='HTML')
        return

    if text.startswith("/img "):
        if not user_tariff: return await send_paywall(update)
        await generate_image(update, context, text[5:])
        return

    await process_ai_request(update, context, text)

# --- CALLBACK HANDLING ---

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    user_id = query.from_user.id

    if data.startswith("buy_"):
        plan = data.split("_")[1]
        await query.edit_message_text(
            f"💳 <b>Подключение тарифа {plan}</b>\n\n{config.PAYMENT_INFO}", 
            parse_mode='HTML'
        )
    
    elif data == "feature_text":
        curr = USER_MODELS.get(user_id, config.DEFAULT_MODEL)
        await query.edit_message_text("💡 <b>ВЫБОР МОДЕЛИ:</b>", reply_markup=keyboards.get_models_keyboard(curr), parse_mode='HTML')
    
    elif data.startswith("setmodel_"):
        new_m = data.split("setmodel_")[1]
        USER_MODELS[user_id] = new_m
        await query.answer(f"🧠 Нейропрофиль обновлен")
        await query.edit_message_text(f"✅ <b>Модель изменена.</b>", parse_mode='HTML')

    elif data == "feature_audio":
        await query.edit_message_text("🎤 <b>АУДИО СЕРВИСЫ:</b>", reply_markup=keyboards.get_audio_keyboard(), parse_mode='HTML')

    elif data == "feature_vision":
        await query.edit_message_text(
            "👁 <b>VISION (ЗРЕНИЕ)</b>\n\nПросто отправьте мне фото или скриншот, и я проанализирую его.\n"
            "Модуль GPT-4o Vision активен.", 
            parse_mode='HTML'
        )

    elif data == "feature_video":
        await query.edit_message_text(
            "🎬 <b>ВИДЕО ИИ (BETA)</b>\n\nГенерация видео доступна на уровне <b>NEO</b>.\n"
            "Интеграция с Luma Dream Machine в процессе.", 
            parse_mode='HTML'
        )

    elif data == "audio_tts":
        curr_v = context.user_data.get('voice_id')
        await query.edit_message_text("🗣 <b>ВЫБЕРИТЕ ГОЛОС:</b>", reply_markup=keyboards.get_voice_selection_keyboard(curr_v), parse_mode='HTML')

    elif data.startswith("setvoice_"):
        v_id = data.split("setvoice_")[1]
        context.user_data['voice_id'] = v_id
        context.user_data['mode'] = 'tts_wait'
        await query.answer("🎙 Голос зафиксирован")
        await query.message.reply_text("🗣 <b>Режим диктора активен.</b>\nПришлите текст:", parse_mode='HTML')

    elif data == "audio_tts_again":
        context.user_data['mode'] = 'tts_wait'
        await query.message.reply_text("🎤 Жду следующий фрагмент текста:", parse_mode='HTML')

    elif data == "mode_chat_reset":
        context.user_data['mode'] = None
        db.create_session(user_id, title="Новый диалог")
        await query.message.reply_text("♻️ <b>Новый диалог создан.</b>", parse_mode='HTML')

    elif data == "audio_sfx":
        context.user_data['mode'] = 'sfx_wait'
        await query.message.reply_text("🔊 <b>Опишите желаемый звук:</b>", parse_mode='HTML')

    elif data.startswith("session_"):
        s_id = int(data.split("_")[1])
        db.activate_session(user_id, s_id)
        await query.answer("📂 Чат загружен")
        await query.message.reply_text("📂 <b>Память восстановлена.</b>", parse_mode='HTML')

    elif data == "history_manage":
        await query.edit_message_reply_markup(
            reply_markup=keyboards.get_history_keyboard(user_id, mode="delete")
        )
    
    elif data == "history_back":
        await query.edit_message_reply_markup(
            reply_markup=keyboards.get_history_keyboard(user_id, mode="view")
        )

    elif data.startswith("del_"):
        s_id = int(data.split("_")[1])
        db.delete_session(user_id, s_id)
        await query.answer("🗑 Сессия удалена")
        await query.edit_message_reply_markup(
            reply_markup=keyboards.get_history_keyboard(user_id, mode="delete")
        )

    elif data == "back_to_features":
        await query.edit_message_text("🧩 <b>ВОЗМОЖНОСТИ:</b>", reply_markup=keyboards.get_features_keyboard(), parse_mode='HTML')

    await query.answer()

# --- Внутренние вызовы TTS / SFX ---

async def handle_tts_request(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    user_id = update.effective_user.id
    voice = context.user_data.get('voice_id', config.DEFAULT_VOICE)
    await context.bot.send_chat_action(chat_id=user_id, action=ChatAction.RECORD_VOICE)
    
    # Генерация аудио
    audio_data, engine, is_fallback = await audio_studio.text_to_speech(text, voice)
    
    if audio_data:
        warn = "⚠️ <i>Резервный ИИ (OpenAI)</i>\n" if is_fallback else ""
        caption = f"🎙 <b>Голос синтезирован!</b>\n\n{warn}<blockquote>⚙️ {engine} | 🎫 {len(text)} Chars</blockquote>"
        
        # ВЕРТИКАЛЬНАЯ раскладка кнопок (для мобильных)
        keyboard = [
            [InlineKeyboardButton("🎤 Озвучить еще", callback_data="audio_tts_again")],
            [InlineKeyboardButton("💬 В новый чат", callback_data="mode_chat_reset")]
        ]
        
        # Отправляем как АУДИОФАЙЛ (с filename=...mp3), чтобы включился плеер и "3 точки"
        await update.message.reply_audio(
            audio=audio_data, 
            filename=f"vnxORACLE_Voice_{int(time.time())}.mp3",
            title=f"Voice Message",
            performer="vnxORACLE AI",
            caption=caption, 
            parse_mode='HTML', 
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        db.update_tokens(user_id, len(text))
    else:
        await update.message.reply_text("❌ Сбой синтеза. API недоступен.")

async def handle_sfx_request(update: Update, context: ContextTypes.DEFAULT_TYPE, desc: str):
    user_id = update.effective_user.id
    await context.bot.send_chat_action(chat_id=user_id, action=ChatAction.RECORD_VOICE)
    sfx = await audio_studio.generate_sfx(desc)
    if sfx:
        await update.message.reply_audio(audio=sfx, caption=f"🔊 <b>SFX: {desc}</b>", parse_mode='HTML')
    else:
        await update.message.reply_text("⚠️ Ошибка генерации звука.")
