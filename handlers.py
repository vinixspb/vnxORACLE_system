import os
import logging
import random
import aiohttp
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
    await update.message.reply_text(config.MSG_NO_SUB, reply_markup=keyboards.get_subscription_keyboard(), parse_mode='HTML')

async def generate_image(update: Update, context: ContextTypes.DEFAULT_TYPE, prompt: str):
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
    
    # Авто-заголовок для новой сессии
    history = db.get_history(session_id, limit=1)
    if not history:
        clean_title = input_text.replace("[Audio Input]: ", "")[:30]
        db.update_session_title(session_id, clean_title)
    
    db.add_message(session_id, "user", input_text)
    history_depth = config.LIMITS.get(user_tariff, 10)
    full_context = db.get_history(session_id, limit=history_depth)
    model = USER_MODELS.get(user_id, config.DEFAULT_MODEL)

    try:
        # Отправляем в AI Engine (поддерживает Vision внутри)
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
        # Всегда удаляем временное изображение после обработки
        if image_path and os.path.exists(image_path):
            os.remove(image_path)

# --- МУЛЬТИМЕДИА ХЕНДЛЕРЫ ---

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка изображений (Vision Module)"""
    user_id = update.effective_user.id
    user_tariff = sheets_mgr.get_user_tariff(user_id)
    
    if user_tariff not in ['PRO', 'NEO']:
        return await update.message.reply_text("🧬 <b>VISION MODULE</b>\n\nАнализ доступен на тарифах <b>PRO</b> и <b>NEO</b>.", parse_mode='HTML')

    caption = update.message.caption or "Что на этом изображении?"
    photo = update.message.photo[-1] # Самое высокое разрешение
    
    try:
        photo_file = await context.bot.get_file(photo.file_id)
        temp_path = os.path.join(DOWNLOADS_DIR, f"vision_{user_id}.jpg")
        await photo_file.download_to_drive(temp_path)
        
        await process_ai_request(update, context, caption, image_path=temp_path)
    except Exception as e:
        logger.error(f"Vision Error: {e}")
        await update.message.reply_text("⚠️ Ошибка при чтении изображения.")

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка голосовых сообщений (Whisper)"""
    user_id = update.effective_user.id
    if not sheets_mgr.get_user_tariff(user_id): return await send_paywall(update)
    
    await context.bot.send_chat_action(chat_id=user_id, action=ChatAction.TYPING)
    try:
        voice_file = await context.bot.get_file(update.message.voice.file_id)
        file_path = os.path.join(DOWNLOADS_DIR, f"v_{user_id}.ogg")
        await voice_file.download_to_drive(file_path)
        
        transcript = await ai_engine.transcribe_audio(file_path)
        if os.path.exists(file_path): os.remove(file_path)
        
        if transcript:
            await update.message.reply_text(f"🎤 <i>Распознано:</i> \"{transcript}\"", parse_mode='HTML')
            await process_ai_request(update, context, f"[Audio Input]: {transcript}")
    except Exception as e:
        logger.error(f"Voice Error: {e}")

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
    await update.message.reply_text(f"👁 <b>vnxORACLE: ONLINE</b>\nВаш уровень: <b>{tariff}</b>", reply_markup=keyboards.get_main_keyboard(), parse_mode='HTML')

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    user_tariff = sheets_mgr.get_user_tariff(user_id)

    # Режимы ожидания (TTS / SFX)
    mode = context.user_data.get('mode')
    if mode == 'tts_wait':
        await handle_tts_request(update, context, text)
        return
    if mode == 'sfx_wait':
        await handle_sfx_request(update, context, text)
        context.user_data['mode'] = None # Сброс режима для звуков
        return

    # Обработка системных кнопок из конфига
    if text == config.BTN_TARIFFS:
        msg = "💳 <b>ТАРИФНЫЕ ПЛАНЫ</b>\n\n💠 <b>START:</b> 190₽\n⚡️ <b>PRO:</b> 590₽\n🧬 <b>NEO:</b> 990₽"
        await update.message.reply_text(msg, reply_markup=keyboards.get_subscription_keyboard(), parse_mode='HTML')
        return

    if text == config.BTN_NEW_DIALOG:
        db.create_session(user_id, title="Новый диалог")
        await update.message.reply_text("♻️ <b>Контекст очищен. Начата новая сессия.</b>", parse_mode='HTML')
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
        await generate_image(update, context, text[5:])
        return

    # Обычный запрос к ИИ
    await process_ai_request(update, context, text)

# --- CALLBACK HANDLING ---

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    user_id = query.from_user.id

    if data.startswith("buy_"):
        plan = data.split("_")[1]
        await query.edit_message_text(f"💳 <b>Оплата тарифа {plan}</b>\n\n{config.PAYMENT_INFO}", parse_mode='HTML')
    
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

    elif data == "audio_tts":
        await query.edit_message_text("🗣 <b>ВЫБЕРИТЕ ГОЛОС:</b>", reply_markup=keyboards.get_voice_selection_keyboard(), parse_mode='HTML')

    elif data.startswith("setvoice_"):
        context.user_data['voice_id'] = data.split("setvoice_")[1]
        context.user_data['mode'] = 'tts_wait'
        await query.answer("🎙 Голос выбран")
        await query.message.reply_text("🗣 <b>Режим диктора активен.</b>\nПришлите текст для озвучки:", parse_mode='HTML')

    elif data == "audio_tts_again":
        context.user_data['mode'] = 'tts_wait'
        await query.message.reply_text("🎤 Жду следующий текст для озвучки:", parse_mode='HTML')

    elif data == "mode_chat_reset":
        context.user_data['mode'] = None
        db.create_session(user_id, title="Новый диалог")
        await query.message.reply_text("💬 <b>Текстовый чат (Новая сессия)</b>\nПишите ваш запрос:", parse_mode='HTML')

    elif data == "audio_sfx":
        context.user_data['mode'] = 'sfx_wait'
        await query.message.reply_text("🔊 <b>Опишите желаемый звук (на английском):</b>", parse_mode='HTML')

    elif data.startswith("session_"):
        s_id = int(data.split("_")[1])
        db.activate_session(user_id, s_id)
        await query.answer("📂 Чат загружен")
        await query.message.reply_text("📂 <b>История диалога восстановлена.</b>", parse_mode='HTML')

    elif data == "back_to_features":
        await query.edit_message_text("🧩 <b>ВОЗМОЖНОСТИ:</b>", reply_markup=keyboards.get_features_keyboard(), parse_mode='HTML')

    await query.answer()

# --- Внутренние вызовы TTS / SFX ---

async def handle_tts_request(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    user_id = update.effective_user.id
    voice = context.user_data.get('voice_id', config.DEFAULT_VOICE)
    await context.bot.send_chat_action(chat_id=user_id, action=ChatAction.RECORD_VOICE)
    
    # Вызов гибридной студии
    audio_data, engine, is_fallback = await audio_studio.text_to_speech(text, voice)
    
    if audio_data:
        warn = "⚠️ <i>Резервный ИИ (OpenAI)</i>\n" if is_fallback else ""
        caption = f"🎙 <b>Голос синтезирован!</b>\n\n{warn}<blockquote>⚙️ {engine} | 🎫 {len(text)} Chars | ∑ {db.get_total_tokens(user_id)}</blockquote>"
        
        # Навигация после озвучки
        keyboard = [[
            InlineKeyboardButton("🎤 Озвучить еще", callback_data="audio_tts_again"),
            InlineKeyboardButton("💬 В новый чат", callback_data="mode_chat_reset")
        ]]
        
        await update.message.reply_audio(
            audio=audio_data, 
            title=f"Oracle_Voice_{engine}",
            performer="vnxORACLE",
            caption=caption, 
            parse_mode='HTML', 
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        db.update_tokens(user_id, len(text))
    else:
        await update.message.reply_text("❌ Ошибка синтеза речи. Попробуйте позже.")

async def handle_sfx_request(update: Update, context: ContextTypes.DEFAULT_TYPE, desc: str):
    user_id = update.effective_user.id
    await context.bot.send_chat_action(chat_id=user_id, action=ChatAction.RECORD_VOICE)
    sfx = await audio_studio.generate_sfx(desc)
    if sfx:
        await update.message.reply_audio(audio=sfx, caption=f"🔊 <b>SFX: {desc}</b>", parse_mode='HTML')
    else:
        await update.message.reply_text("⚠️ Ошибка генерации звука.")
