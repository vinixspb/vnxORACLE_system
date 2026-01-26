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

# --- ВСПОМОГАТЕЛЬНЫЕ ---
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

async def process_ai_request(update: Update, context: ContextTypes.DEFAULT_TYPE, input_text: str):
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
        ai_response, tokens_spent = await ai_engine.get_response(full_context, model)
        db.add_message(session_id, "assistant", ai_response, model=model)
        db.update_tokens(user_id, tokens_spent)
        
        model_name = model.split('/')[-1].replace(":free", "")
        final_text = (f"{ai_response}\n\n<blockquote>⚙️ {model_name} | 🎫 {tokens_spent} | ∑ {db.get_total_tokens(user_id)}</blockquote>")
        await update.message.reply_text(final_text, parse_mode='HTML')
    except Exception as e:
        logger.error(f"AI Error: {e}")
        await update.message.reply_text("⚠️ Ошибка связи.")

# --- АУДИО ИНСТРУМЕНТЫ С ПОДВАЛОМ И НАВИГАЦИЕЙ ---

async def handle_tts_request(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    user_id = update.effective_user.id
    selected_voice = context.user_data.get('voice_id', config.DEFAULT_VOICE)
    
    await update.message.reply_text(f"🗣 <b>Генерирую голос...</b>", parse_mode='HTML')
    await context.bot.send_chat_action(chat_id=user_id, action=ChatAction.RECORD_VOICE)
    
    audio_data = await audio_studio.text_to_speech(text, voice_id=selected_voice)
    
    if audio_data:
        # Формируем подвал
        chars_count = len(text)
        footer = f"\n\n<blockquote>⚙️ Audio Engine | 🎫 {chars_count} Chars | ∑ {db.get_total_tokens(user_id)}</blockquote>"
        
        # Кнопки навигации
        keyboard = [
            [
                InlineKeyboardButton("🎤 Озвучить еще", callback_data="audio_tts_again"),
                InlineKeyboardButton("💬 В обычный чат", callback_data="mode_chat_reset")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        try:
            await update.message.reply_voice(
                voice=audio_data, 
                caption=f"🎙 <b>Голос синтезирован!</b>{footer}", 
                parse_mode='HTML',
                reply_markup=reply_markup
            )
        except BadRequest as e:
            if "Voice_messages_forbidden" in str(e):
                await update.message.reply_audio(
                    audio=audio_data, 
                    title="vnxORACLE_Voice",
                    caption=f"⚠️ <i>Голосовые запрещены, отправляю файлом.</i>{footer}",
                    parse_mode='HTML',
                    reply_markup=reply_markup
                )
        
        # Обновляем статистику (считаем символы как токены для аудио)
        db.update_tokens(user_id, chars_count)
    else:
        await update.message.reply_text("⚠️ Ошибка генерации голоса (API Error).")

async def handle_sfx_request(update: Update, context: ContextTypes.DEFAULT_TYPE, description: str):
    user_id = update.effective_user.id
    await update.message.reply_text(f"🔊 <b>Синтезирую звук...</b>", parse_mode='HTML')
    await context.bot.send_chat_action(chat_id=user_id, action=ChatAction.UPLOAD_VOICE)
    
    sfx_data = await audio_studio.generate_sfx(description)
    
    if sfx_data:
        footer = f"\n\n<blockquote>⚙️ SFX Gen | 🎫 1 Unit | ∑ {db.get_total_tokens(user_id)}</blockquote>"
        await update.message.reply_audio(
            audio=sfx_data, 
            title="SFX Generated", 
            performer="vnxORACLE", 
            caption=f"🔊 {description}{footer}",
            parse_mode='HTML'
        )
    else:
        await update.message.reply_text("⚠️ Ошибка генерации звука.")


# --- ОСНОВНЫЕ ХЕНДЛЕРЫ ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    user = update.effective_user
    tariff = sheets_mgr.get_user_tariff(user.id)
    if not tariff:
        await update.message.reply_text(config.MSG_WELCOME, parse_mode='HTML')
        await update.message.reply_text(config.MSG_NO_SUB, reply_markup=keyboards.get_subscription_keyboard(), parse_mode='HTML')
        return
    db.create_session(user.id, title="Новый чат")
    await update.message.reply_text(f"👁 <b>Доступ разрешен.</b>\nВаш уровень: <b>{tariff}</b>", reply_markup=keyboards.get_main_keyboard(), parse_mode='HTML')

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    user_tariff = sheets_mgr.get_user_tariff(user_id)

    current_mode = context.user_data.get('mode')
    
    if current_mode == 'tts_wait':
        if not user_tariff: return await send_paywall(update)
        await handle_tts_request(update, context, text)
        # Мы НЕ сбрасываем режим здесь, чтобы можно было слать текст один за другим
        # Режим сбросится только кнопкой "В обычный чат" или системной кнопкой
        return

    if current_mode == 'sfx_wait':
        if not user_tariff: return await send_paywall(update)
        await handle_sfx_request(update, context, text)
        context.user_data['mode'] = None
        return

    sys_buttons = [config.BTN_NEW_DIALOG, config.BTN_HISTORY, config.BTN_PROFILE, config.BTN_TARIFFS, config.BTN_CHANGE_MODEL, config.BTN_HELP]

    if text.startswith("/img "):
        if not user_tariff: return await send_paywall(update)
        await generate_image(update, context, text[5:])
        return

    if text in sys_buttons:
        context.user_data['mode'] = None 
        if not user_tariff: return await send_paywall(update)
        
        if text == config.BTN_HISTORY:
            markup = keyboards.get_history_keyboard(user_id, mode="view")
            if not markup: await update.message.reply_text("📂 Архив пуст.")
            else: await update.message.reply_text("💾 <b>ИСТОРИЯ ЧАТОВ:</b>", reply_markup=markup, parse_mode='HTML')
            return

        if text == config.BTN_NEW_DIALOG:
            db.create_session(user_id, title="Новый диалог")
            await update.message.reply_text("♻️ <b>Новый диалог создан.</b>", parse_mode='HTML')
            return

        if text == config.BTN_PROFILE:
            curr = USER_MODELS.get(user_id, config.DEFAULT_MODEL).split('/')[-1]
            await update.message.reply_text(f"👤 <b>ПРОФИЛЬ</b>\nСтатус: {user_tariff}\nМодель: <code>{curr}</code>", parse_mode='HTML')
            return

        if text == config.BTN_TARIFFS:
            await update.message.reply_text("💳 <b>ТАРИФНЫЕ ПЛАНЫ:</b>", reply_markup=keyboards.get_subscription_keyboard(), parse_mode='HTML')
            return

        if text == config.BTN_CHANGE_MODEL:
            await update.message.reply_text("🧩 <b>МЕНЮ ВОЗМОЖНОСТЕЙ:</b>", reply_markup=keyboards.get_features_keyboard(), parse_mode='HTML')
            return

        if text == config.BTN_HELP:
            await update.message.reply_text(config.MSG_SUPPORT, parse_mode='HTML')
            return
        return

    await process_ai_request(update, context, text)

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not sheets_mgr.get_user_tariff(user_id): return await send_paywall(update)
    await context.bot.send_chat_action(chat_id=user_id, action=ChatAction.TYPING)
    try:
        voice_file = await context.bot.get_file(update.message.voice.file_id)
        file_path = f"voice_{user_id}.ogg"
        await voice_file.download_to_drive(file_path)
        transcript = await ai_engine.transcribe_audio(file_path)
        if os.path.exists(file_path): os.remove(file_path)
        if transcript:
            await update.message.reply_text(f"🎤 <i>Распознано:</i> \"{transcript}\"", parse_mode='HTML')
            ai_input = f"[Audio Input]: {transcript}"
            await process_ai_request(update, context, ai_input)
    except Exception as e:
        logger.error(f"Voice Error: {e}")

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if config.ARCHIVE_CHANNEL_ID:
        try:
            await context.bot.forward_message(chat_id=config.ARCHIVE_CHANNEL_ID, from_chat_id=update.effective_user.id, message_id=update.message.message_id)
            await update.message.reply_text("✅ <b>Объект сохранен.</b>", parse_mode='HTML')
        except: pass

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data
    answered = False

    # --- НАВИГАЦИЯ ПОСЛЕ ОЗВУЧКИ ---
    if data == "audio_tts_again":
        context.user_data['mode'] = 'tts_wait'
        await query.message.reply_text("🎤 <b>Режим озвучки продлен.</b>\nПришлите следующий текст:", parse_mode='HTML')
        answered = True

    elif data == "mode_chat_reset":
        context.user_data['mode'] = None
        await query.message.reply_text("💬 <b>Режим чата восстановлен.</b>", parse_mode='HTML')
        answered = True

    # --- СТАНДАРТНАЯ НАВИГАЦИЯ ---
    elif data == "back_to_features":
        await query.edit_message_text("🧩 <b>МЕНЮ ВОЗМОЖНОСТЕЙ</b>", reply_markup=keyboards.get_features_keyboard(), parse_mode='HTML')
        context.user_data['mode'] = None
    
    elif data == "feature_text":
        curr = USER_MODELS.get(user_id, config.DEFAULT_MODEL)
        await query.edit_message_text("💡 <b>ВЫБЕРИТЕ НЕЙРОСЕТЬ:</b>", reply_markup=keyboards.get_models_keyboard(curr), parse_mode='HTML')
    
    elif data == "feature_audio":
        await query.edit_message_text("🎤 <b>АУДИО И
