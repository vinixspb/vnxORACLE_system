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

# --- ОБРАБОТЧИКИ СООБЩЕНИЙ ---

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    
    # 🛡 1. ПРИОРИТЕТ СИСТЕМНЫХ КНОПОК (Сброс режимов)
    sys_buttons = [
        config.BTN_NEW_DIALOG, config.BTN_HISTORY, 
        config.BTN_PROFILE, config.BTN_TARIFFS, 
        config.BTN_CHANGE_MODEL, config.BTN_HELP
    ]
    
    if text in sys_buttons:
        context.user_data['mode'] = None # Сброс режима при нажатии кнопки
        
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
            
        return # Остальные кнопки (Profile, Help) обрабатываются здесь, не идя в AI

    # 🛡 2. ОБРАБОТКА РЕЖИМОВ
    mode = context.user_data.get('mode')
    
    if mode == 'tts_wait':
        await handle_tts_request(update, context, text)
        return
        
    if mode == 'sfx_wait':
        await handle_sfx_request(update, context, text)
        context.user_data['mode'] = None
        return

    if text.startswith("/img "):
        await generate_image(update, context, text[5:])
        return

    # Обычный запрос
    await process_ai_request(update, context, text)

# --- МУЛЬТИМЕДИА ---

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if sheets_mgr.get_user_tariff(user_id) not in ['PRO', 'NEO']:
        return await update.message.reply_text("🧬 <b>VISION MODULE</b>\nДоступен на уровнях PRO и NEO.", parse_mode='HTML')
    
    photo = update.message.photo[-1]
    caption = update.message.caption or "Что на этом фото?"
    
    try:
        file = await context.bot.get_file(photo.file_id)
        # Уникальное имя + UUID
        path = os.path.join(DOWNLOADS_DIR, f"v_{user_id}_{uuid.uuid4().hex[:8]}.jpg")
        await file.download_to_drive(path)
        await process_ai_request(update, context, caption, image_path=path)
    except Exception as e: 
        logger.error(f"Vision Error: {e}")
        await update.message.reply_text("⚠️ Ошибка загрузки изображения.")

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка голосовых сообщений (Whisper) с гарантированной очисткой"""
    user_id = update.effective_user.id
    if not sheets_mgr.get_user_tariff(user_id): return await send_paywall(update)
    
    await context.bot.send_chat_action(chat_id=user_id, action=ChatAction.TYPING)
    
    # Генерируем путь с UUID во избежание коллизий
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
            # FIX 1: Сообщаем пользователю о неудаче
            await update.message.reply_text("🎤 <b>Не удалось распознать голос.</b>\nПопробуйте ещё раз или отправьте текстом.", parse_mode='HTML')
            
    except Exception as e:
        logger.error(f"Voice Error: {e}")
        await update.message.reply_text("⚠️ Ошибка обработки голоса.")
    finally:
        # FIX 2: Гарантированное удаление файла
        if os.path.exists(file_path):
            try: os.remove(file_path)
            except: pass

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Хранитель (Архив)"""
    if config.ARCHIVE_CHANNEL_ID:
        try:
            await context.bot.forward_message(chat_id=config.ARCHIVE_CHANNEL_ID, from_chat_id=update.effective_chat.id, message_id=update.message.message_id)
            await update.message.reply_text("✅ <b>Объект сохранен.</b>", parse_mode='HTML')
        except: pass

# --- CALLBACKS & ВНУТРЕННИЕ ФУНКЦИИ ---

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    user_id = query.from_user.id

    # Навигация Архива
    if data == "history_manage":
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
    
    # Навигация Меню и Моделей
    elif data == "feature_text":
        context.user_data['mode'] = None
        curr = USER_MODELS.get(user_id, config.DEFAULT_MODEL)
        await query.edit_message_text("💡 <b>ВЫБОР МОДЕЛИ:</b>", reply_markup=keyboards.get_models_keyboard(curr), parse_mode='HTML')
    
    elif data.startswith("setmodel_"):
        context.user_data['mode'] = None
        USER_MODELS[user_id] = data.split("setmodel_")[1]
        await query.answer(f"🧠 Модель активна")
        await query.edit_message_text(f"✅ <b>Модель изменена.</b>", parse_mode='HTML')

    # Аудио и Голос
    elif data == "feature_audio":
        await query.edit_message_text("🎤 <b>АУДИО СЕРВИСЫ:</b>", reply_markup=keyboards.get_audio_keyboard(), parse_mode='HTML')
    
    elif data.startswith("setvoice_"):
        context.user_data['voice_id'] = data.split("setvoice_")[1]
        context.user_data['mode'] = 'tts_wait'
        await query.answer("🎙 Голос выбран")
        await query.message.reply_text("🗣 <b>Режим диктора активен.</b>\nПришлите текст для озвучки:", parse_mode='HTML')
    
    elif data == "audio_tts_again":
        context.user_data['mode'] = 'tts_wait'
        await query.message.reply_text("🎤 Жду текст:", parse_mode='HTML')

    elif data == "mode_chat_reset":
        context.user_data['mode'] = None
        db.create_session(user_id, title="Новый диалог")
        await query.message.reply_text("💬 <b>Текстовый режим.</b>", parse_mode='HTML')

    elif data == "audio_sfx":
        context.user_data['mode'] = 'sfx_wait'
        await query.message.reply_text("🔊 <b>Опишите звук (на англ):</b>", parse_mode='HTML')
    
    elif data.startswith("buy_"):
        plan = data.split("_")[1]
        await query.edit_message_text(f"💳 <b>Оплата {plan}</b>\n\n{config.PAYMENT_INFO}", parse_mode='HTML')

    elif data == "back_to_features":
        await query.edit_message_text("🧩 <b>ВОЗМОЖНОСТИ:</b>", reply_markup=keyboards.get_features_keyboard(), parse_mode='HTML')
    
    await query.answer()

async def handle_tts_request(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    user_id = update.effective_user.id
    voice = context.user_data.get('voice_id', config.DEFAULT_VOICE)
    await context.bot.send_chat_action(chat_id=user_id, action=ChatAction.RECORD_VOICE)
    
    audio_data, engine, is_fallback = await audio_studio.text_to_speech(text, voice)
    
    # Сбрасываем режим, чтобы не застревать
    context.user_data['mode'] = None 
    
    if audio_data:
        warn = "⚠️ <i>Резервный ИИ</i>\n" if is_fallback else ""
        caption = f"🎙 <b>Готово!</b>\n\n{warn}<blockquote>⚙️ {engine} | 🎫 {len(text)}</blockquote>"
        
        keyboard = [[
            InlineKeyboardButton("🎤 Озвучить еще", callback_data="audio_tts_again"),
            InlineKeyboardButton("💬 Вернуться в чат", callback_data="mode_chat_reset")
        ]]
        
        await update.message.reply_audio(
            audio=audio_data, 
            caption=caption, 
            parse_mode='HTML', 
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
    user_id = update.effective_user.id
    tariff = sheets_mgr.get_user_tariff(user_id)
    if not tariff:
        await update.message.reply_text(config.MSG_WELCOME, parse_mode='HTML')
        await update.message.reply_text(config.MSG_NO_SUB, reply_markup=keyboards.get_subscription_keyboard(), parse_mode='HTML')
        return
    db.create_session(user_id, title="Новый чат")
    await update.message.reply_text(f"👁 <b>vnxORACLE: ONLINE</b>\nВаш уровень: <b>{tariff}</b>", reply_markup=keyboards.get_main_keyboard(), parse_mode='HTML')
