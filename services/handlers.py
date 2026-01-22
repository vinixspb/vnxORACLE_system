import os
import logging
from telegram import Update, BotCommand
from telegram.ext import ContextTypes, Application
from telegram.constants import ChatAction

import config
from loader import sheets_mgr, ai_engine, db, USER_MODELS
import keyboards

logger = logging.getLogger(__name__)

# --- ВСПОМОГАТЕЛЬНЫЕ ---
async def send_paywall(update: Update):
    await update.message.reply_text(config.MSG_NO_SUB, reply_markup=keyboards.get_subscription_keyboard(), parse_mode='HTML')

async def process_ai_request(update: Update, context: ContextTypes.DEFAULT_TYPE, input_text: str):
    user_id = update.effective_user.id
    user_tariff = sheets_mgr.get_user_tariff(user_id)
    if not user_tariff: return await send_paywall(update)

    await context.bot.send_chat_action(chat_id=user_id, action=ChatAction.TYPING)

    session_id = db.get_active_session(user_id)
    history = db.get_history(session_id, limit=5)
    if not history:
        db.update_session_title(session_id, input_text)
    
    db.add_message(session_id, "user", input_text)

    history_depth = config.LIMITS.get(user_tariff, 10)
    full_context = db.get_history(session_id, limit=history_depth)
    model = USER_MODELS.get(user_id, config.DEFAULT_MODEL)

    try:
        ai_response, tokens_spent = await ai_engine.get_response(full_context, model)
        db.add_message(session_id, "assistant", ai_response, model=model)
        db.update_tokens(user_id, tokens_spent)
        total_spent = db.get_total_tokens(user_id)
        
        model_name = model.split('/')[-1]
        final_text = (
            f"{ai_response}\n\n"
            f"<blockquote>⚙️ {model_name} | 🎫 {tokens_spent} | ∑ {total_spent}</blockquote>"
        )
        try:
            await update.message.reply_text(final_text, parse_mode='HTML')
        except:
            await update.message.reply_text(f"{ai_response}")
    except Exception as e:
        logger.error(f"AI Error: {e}")
        await update.message.reply_text("⚠️ Ошибка связи.")

# --- ОСНОВНЫЕ ОБРАБОТЧИКИ ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    tariff = sheets_mgr.get_user_tariff(user.id)
    if not tariff:
        await update.message.reply_text(config.MSG_WELCOME, parse_mode='HTML')
        await update.message.reply_text(config.MSG_NO_SUB, reply_markup=keyboards.get_subscription_keyboard(), parse_mode='HTML')
        return
    db.create_session(user.id, title="Новая сессия")
    await update.message.reply_text(
        f"👁 <b>Доступ разрешен.</b>\nВаш уровень: <b>{tariff}</b>\n\nДобро пожаловать в систему.",
        reply_markup=keyboards.get_main_keyboard(),
        parse_mode='HTML'
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text
    user_id = user.id
    user_tariff = sheets_mgr.get_user_tariff(user_id)

    if text == config.BTN_NEW_DIALOG:
        if not user_tariff: return await send_paywall(update)
        db.create_session(user_id, title="Новый диалог")
        await update.message.reply_text("♻️ <b>Новый чат создан.</b>", parse_mode='HTML')
        return

    if text == config.BTN_HISTORY:
        if not user_tariff: return await send_paywall(update)
        markup = keyboards.get_history_keyboard(user_id)
        if not markup:
            await update.message.reply_text("📂 Архив пуст.")
        else:
            await update.message.reply_text("💾 <b>ИСТОРИЯ ЧАТОВ:</b>\nНажмите на название для загрузки или ❌ для удаления.", reply_markup=markup, parse_mode='HTML')
        return

    if text == config.BTN_PROFILE:
        status = f"✅ {user_tariff}" if user_tariff else "❌ NO ACCESS"
        limit = config.LIMITS.get(user_tariff, 0) if user_tariff else 0
        total_tokens = db.get_total_tokens(user_id)
        current_model = USER_MODELS.get(user_id, config.DEFAULT_MODEL)
        await update.message.reply_text(
            f"👤 <b>ПРОФИЛЬ</b>\nID: <code>{user_id}</code>\nStatus: <b>{status}</b>\nMemory: {limit} msg\nSpent Tokens: <b>{total_tokens}</b>\nActive Model: {current_model}", 
            parse_mode='HTML'
        )
        return
    
    if text == config.BTN_TARIFFS:
        await update.message.reply_text("💳 <b>ВЫБОР УРОВНЯ ДОСТУПА</b>", reply_markup=keyboards.get_subscription_keyboard(), parse_mode='HTML')
        return

    if text == config.BTN_HELP:
        await update.message.reply_text(config.MSG_SUPPORT, parse_mode='HTML')
        return

    if text == config.BTN_CHANGE_MODEL:
        if not user_tariff: return await send_paywall(update)
        if user_tariff == "START":
            await update.message.reply_text("🔒 На тарифе START доступна только GPT-4o Mini.\nДля смены модели обновитесь до тарифа PRO или NEO.", parse_mode='HTML')
        else:
            await update.message.reply_text("🧩 <b>МЕНЮ ВОЗМОЖНОСТЕЙ</b>\nВыберите нужный раздел:", reply_markup=keyboards.get_features_keyboard(), parse_mode='HTML')
        return

    await process_ai_request(update, context, text)

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    if not sheets_mgr.get_user_tariff(user_id): return await send_paywall(update)

    await context.bot.send_chat_action(chat_id=user_id, action=ChatAction.TYPING)
    try:
        voice_file = await context.bot.get_file(update.message.voice.file_id)
        file_path = f"voice_{user_id}.ogg"
        await voice_file.download_to_drive(file_path)
        transcript = await ai_engine.transcribe_audio(file_path)
        if os.path.exists(file_path): os.remove(file_path)

        if not transcript:
            await update.message.reply_text("⚠️ Не удалось распознать голос.")
            return

        await update.message.reply_text(f"🎤 <i>Вы сказали:</i> \"{transcript}\"", parse_mode='HTML')
        await process_ai_request(update, context, transcript)
    except Exception as e:
        logger.error(f"Voice Error: {e}")
        await update.message.reply_text("⚠️ Ошибка обработки голоса.")

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data
    
    if data == "back_to_features":
        await query.edit_message_text("🧩 <b>МЕНЮ ВОЗМОЖНОСТЕЙ</b>", reply_markup=keyboards.get_features_keyboard(), parse_mode='HTML')
        return

    if data == "feature_text":
        curr = USER_MODELS.get(user_id, config.DEFAULT_MODEL)
        await query.edit_message_text("💡 <b>ВЫБЕРИТЕ ТЕКСТОВУЮ НЕЙРОСЕТЬ:</b>", reply_markup=keyboards.get_models_keyboard(curr), parse_mode='HTML')
        return
    
    if data == "feature_audio":
        await query.answer("🎤 Голосовой режим активен")
        await query.message.reply_text("🎤 <b>АУДИО РЕЖИМ</b>\nПросто отправьте голосовое сообщение.", parse_mode='HTML')
        return

    if data in ["feature_design", "feature_video", "feature_keeper"]:
        await query.answer("🚧 В разработке", show_alert=True)
        return
    
    if data == "feature_help":
        await query.message.reply_text(config.MSG_SUPPORT, parse_mode='HTML')
        return
    
    if data == "feature_knowledge":
        await query.answer("📚 База знаний наполняется...")
        return

    if data.startswith("setmodel_"):
        new_model = data.split("setmodel_")[1]
        USER_MODELS[user_id] = new_model
        await query.answer(f"🧠 Модель изменена на {new_model}")
        await query.edit_message_text(f"✅ <b>Модель активирована:</b> {new_model}\nМожно продолжать общение.", parse_mode='HTML')
        return

    if data.startswith("del_"):
        session_id = int(data.split("_")[1])
        if db.delete_session(user_id, session_id):
            await query.answer("🗑 Чат удален")
            new_markup = keyboards.get_history_keyboard(user_id)
            if new_markup:
                await query.edit_message_reply_markup(reply_markup=new_markup)
            else:
                await query.edit_message_text("📂 Архив пуст.")
        else:
            await query.answer("⚠️ Ошибка", show_alert=True)
        return

    await query.answer()

    if data.startswith("buy_"):
        plan = data.split("_")[1]
        info = config.TARIFF_INFO.get(plan, "Error")
        invoice_text = (
            f"{info}\n\n"
            "💳 <b>РЕКВИЗИТЫ ДЛЯ ОПЛАТЫ:</b>\n"
            "<code>(Настройка платежного модуля...)</code>\n"
            "<code>USDT / CARD</code>\n\n"
            "Для активации перешлите скриншот Архитектору:"
        )
        from telegram import InlineKeyboardMarkup
        pay_btn = InlineKeyboardMarkup([
            [InlineKeyboardButton("📨 Отправить чек Архитектору", url="https://t.me/vinixspb")],
            [InlineKeyboardButton("🔙 Назад", callback_data="back_to_tariffs")]
        ])
        await query.edit_message_text(invoice_text, reply_markup=pay_btn, parse_mode='HTML')
        return

    if data == "back_to_tariffs":
        await query.edit_message_text("💳 <b>ВЫБОР УРОВНЯ ДОСТУПА</b>", reply_markup=keyboards.get_subscription_keyboard(), parse_mode='HTML')
        return

    if data.startswith("session_"):
        session_id = int(data.split("_")[1])
        if db.activate_session(user_id, session_id):
            title = db.get_session_title(session_id)
            await query.message.reply_text(f"📂 <b>Чат загружен:</b> {title}", parse_mode='HTML')
        else:
            await query.message.reply_text("⚠️ Ошибка.")
