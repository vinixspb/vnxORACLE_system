import os
import logging
import random
import aiohttp
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ChatAction

import config
from loader import sheets_mgr, ai_engine, db, USER_MODELS
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
        # Очищаем заголовок от технического тега, если это первое сообщение
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
        
        # Убираем суффикс :free для красоты
        model_name = model.split('/')[-1].replace(":free", "")
        
        final_text = (f"{ai_response}\n\n<blockquote>⚙️ {model_name} | 🎫 {tokens_spent} | ∑ {db.get_total_tokens(user_id)}</blockquote>")
        await update.message.reply_text(final_text, parse_mode='HTML')
    except Exception as e:
        logger.error(f"AI Error: {e}")
        await update.message.reply_text("⚠️ Ошибка связи.")

# --- ОСНОВНЫЕ ХЕНДЛЕРЫ ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

    sys_buttons = [config.BTN_NEW_DIALOG, config.BTN_HISTORY, config.BTN_PROFILE, config.BTN_TARIFFS, config.BTN_CHANGE_MODEL, config.BTN_HELP]

    if text.startswith("/img "):
        if not user_tariff: return await send_paywall(update)
        await generate_image(update, context, text[5:])
        return

    if text in sys_buttons:
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
            # Фикс для ИИ, чтобы он не игнорировал аудио-контекст
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
    
    answered = False # Флаг: был ли отправлен ответ API Telegram

    # --- НАВИГАЦИЯ ---
    if data == "back_to_features":
        await query.edit_message_text("🧩 <b>МЕНЮ ВОЗМОЖНОСТЕЙ</b>", reply_markup=keyboards.get_features_keyboard(), parse_mode='HTML')
    
    # --- РАЗДЕЛЫ ---
    elif data == "feature_text":
        curr = USER_MODELS.get(user_id, config.DEFAULT_MODEL)
        await query.edit_message_text("💡 <b>ВЫБЕРИТЕ НЕЙРОСЕТЬ:</b>", reply_markup=keyboards.get_models_keyboard(curr), parse_mode='HTML')
    
    elif data == "feature_audio":
        await query.edit_message_text("🎤 <b>АУДИО-СТУДИЯ (BETA):</b>\nВыберите инструмент:", reply_markup=keyboards.get_audio_keyboard(), parse_mode='HTML')
        
    elif data == "feature_design":
        await query.message.reply_text("🎨 <b>ДИЗАЙН:</b>\nПишите <code>/img [описание]</code>", parse_mode='HTML')

    # --- АУДИО ИНСТРУМЕНТЫ ---
    elif data == "audio_transcribe":
        await query.answer("🎙 Режим активен")
        answered = True
        await query.message.reply_text("📝 <b>ТРАНСКРИБАЦИЯ:</b>\nПросто отправьте голосовое сообщение или перешлите его сюда.\nСистема автоматически переведет его в текст.", parse_mode='HTML')
    
    elif data in ["audio_tts", "audio_suno", "audio_sfx", "audio_clone", "audio_vid2aud", "audio_eleven_music"]:
        await query.answer("🚧 В разработке", show_alert=True)
        answered = True

    # --- ИСТОРИЯ ---
    elif data == "history_manage":
        markup = keyboards.get_history_keyboard(user_id, mode="delete")
        await query.edit_message_text("🗑 <b>РЕЖИМ УДАЛЕНИЯ:</b>", reply_markup=markup, parse_mode='HTML')
    
    elif data == "history_back":
        markup = keyboards.get_history_keyboard(user_id, mode="view")
        await query.edit_message_text("💾 <b>ИСТОРИЯ ЧАТОВ:</b>", reply_markup=markup, parse_mode='HTML')

    # --- ДЕЙСТВИЯ ---
    elif data.startswith("setmodel_"):
        new_model_id = data.split("setmodel_")[1]
        USER_MODELS[user_id] = new_model_id
        model_name = new_model_id.split("/")[-1].replace(":free", "")
        if "devstral" in model_name: model_name = "Mistral Devstral 2"
        if "chimera" in model_name: model_name = "R1T2 Chimera"
        if "lfm" in model_name: model_name = "Liquid LFM 2.5"
        
        await query.answer(f"🧠 {model_name} активирована")
        answered = True
        await query.edit_message_text(f"✅ <b>Модель изменена:</b> {model_name}", parse_mode='HTML')

    elif data.startswith("del_"):
        if db.delete_session(user_id, int(data.split("_")[1])):
            await query.answer("🗑 Удалено")
            answered = True
            markup = keyboards.get_history_keyboard(user_id, mode="delete")
            if markup: await query.edit_message_reply_markup(reply_markup=markup)
            else: await query.edit_message_text("📂 Архив пуст.")
    
    elif data.startswith("session_"):
        if db.activate_session(user_id, int(data.split("_")[1])):
            await query.answer() # Здесь просто гасим "часики"
            answered = True
            await query.message.reply_text(f"📂 <b>Чат загружен.</b>", parse_mode='HTML')
    
    elif data.startswith("buy_"):
        plan = data.split("_")[1]
        await query.edit_message_text(f"{config.TARIFF_INFO[plan]}\n\n💳 <b>Оплата:</b> {config.PAYMENT_INFO}", parse_mode='HTML')
    
    # ФИНАЛЬНАЯ ПРОВЕРКА: Если не ответили ранее, отвечаем сейчас
    if not answered:
        await query.answer()
