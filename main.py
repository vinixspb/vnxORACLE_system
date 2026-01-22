import logging
import asyncio
import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from telegram.constants import ChatAction

# --- МОДУЛИ ---
import config
from services.sheets_manager import GoogleSheetsManager
from services.ai_engine import AIEngine
from services.database import Database

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# --- ОПЕРАТИВНАЯ ПАМЯТЬ ДЛЯ НАСТРОЕК ---
# Храним выбранную модель юзера: {user_id: "model_name"}
USER_MODELS = {} 

try:
    sheets_mgr = GoogleSheetsManager()
    ai_engine = AIEngine()
    db = Database()
    logger.info("✅ Services OK")
except Exception as e:
    logger.critical(f"❌ Init Error: {e}")

# --- UI: КЛАВИАТУРЫ ---

def get_main_keyboard():
    keyboard = [
        [KeyboardButton(config.BTN_NEW_DIALOG), KeyboardButton(config.BTN_HISTORY)],
        [KeyboardButton(config.BTN_PROFILE), KeyboardButton(config.BTN_TARIFFS)],
        [KeyboardButton(config.BTN_CHANGE_MODEL), KeyboardButton(config.BTN_HELP)]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_subscription_keyboard():
    keyboard = [
        [InlineKeyboardButton("💠 START (390₽)", callback_data="buy_START")],
        [InlineKeyboardButton("⚡️ PRO (990₽)", callback_data="buy_PRO")],
        [InlineKeyboardButton("🧬 NEO (1490₽)", callback_data="buy_NEO")],
        [InlineKeyboardButton("👨‍💻 Связь с Архитектором", url="https://t.me/vinixspb")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_history_keyboard(user_id):
    """ИСТОРИЯ: [Название] [❌] в одну строку"""
    sessions = db.get_user_sessions(user_id, limit=10)
    if not sessions: return None
    
    keyboard = []
    for s in sessions:
        date_short = s['created_at'][5:16]
        title_text = f"{s['title']} ({date_short})"
        # Одна строка - две кнопки
        btn_load = InlineKeyboardButton(text=title_text, callback_data=f"session_{s['id']}")
        btn_del = InlineKeyboardButton(text="❌", callback_data=f"del_{s['id']}")
        keyboard.append([btn_load, btn_del])
        
    return InlineKeyboardMarkup(keyboard)

def get_models_keyboard(current_model):
    """Выбор модели"""
    models = [
        ("GPT-4o Mini (Basic)", config.MODEL_BASIC),
        ("GPT-4o (Smart)", config.MODEL_PRO),
        ("Claude 3.5 Sonnet (Code)", config.MODEL_NEO)
    ]
    keyboard = []
    for name, code in models:
        prefix = "✅ " if code == current_model else "⚪️ "
        keyboard.append([InlineKeyboardButton(prefix + name, callback_data=f"setmodel_{code}")])
    return InlineKeyboardMarkup(keyboard)

# --- ЛОГИКА ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    tariff = sheets_mgr.get_user_tariff(user.id)

    if not tariff:
        await update.message.reply_text(config.MSG_WELCOME, parse_mode='HTML')
        await update.message.reply_text(config.MSG_NO_SUB, reply_markup=get_subscription_keyboard(), parse_mode='HTML')
        return

    db.create_session(user.id, title="Новая сессия")
    await update.message.reply_text(
        f"👁 <b>Доступ разрешен.</b>\nВаш уровень: <b>{tariff}</b>\n\nДобро пожаловать в систему.",
        reply_markup=get_main_keyboard(),
        parse_mode='HTML'
    )

# --- ГЛАВНЫЙ ОБРАБОТЧИК (ТЕКСТ) ---
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text
    user_id = user.id
    user_tariff = sheets_mgr.get_user_tariff(user_id)

    # 1. СИСТЕМНЫЕ КОМАНДЫ
    if text == config.BTN_NEW_DIALOG:
        if not user_tariff: return await send_paywall(update)
        db.create_session(user_id, title="Новый диалог")
        await update.message.reply_text("♻️ <b>Новый чат создан.</b>", parse_mode='HTML')
        return

    if text == config.BTN_HISTORY:
        if not user_tariff: return await send_paywall(update)
        markup = get_history_keyboard(user_id)
        if not markup:
            await update.message.reply_text("📂 Архив пуст.")
        else:
            await update.message.reply_text("💾 <b>ИСТОРИЯ ЧАТОВ:</b>", reply_markup=markup, parse_mode='HTML')
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
        await update.message.reply_text("💳 <b>ВЫБОР УРОВНЯ ДОСТУПА</b>", reply_markup=get_subscription_keyboard(), parse_mode='HTML')
        return

    if text == config.BTN_HELP:
        await update.message.reply_text(config.MSG_SUPPORT, parse_mode='HTML')
        return

    if text == config.BTN_CHANGE_MODEL:
        if not user_tariff: return await send_paywall(update)
        if user_tariff == "START":
            await update.message.reply_text(f"🔒 На тарифе <b>START</b> доступна только GPT-4o Mini.\nДля смены модели обновитесь до <b>PRO</b>.", parse_mode='HTML')
        else:
            curr = USER_MODELS.get(user_id, config.DEFAULT_MODEL)
            await update.message.reply_text("🧠 <b>ВЫБЕРИТЕ НЕЙРОСЕТЬ:</b>", reply_markup=get_models_keyboard(curr), parse_mode='HTML')
        return

    # 2. ОБРАБОТКА ТЕКСТА (AI)
    await process_ai_request(update, context, text)

# --- ОБРАБОТЧИК ГОЛОСА ---
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    user_tariff = sheets_mgr.get_user_tariff(user_id)

    if not user_tariff: return await send_paywall(update)
    
    # Голосовые доступны только от PRO? Или всем? Пока сделаем всем.
    # if user_tariff == "START":
    #     await update.message.reply_text("🔒 Голосовой ввод доступен на тарифе PRO.")
    #     return

    await context.bot.send_chat_action(chat_id=user_id, action=ChatAction.TYPING)

    try:
        # 1. Скачиваем файл
        voice_file = await context.bot.get_file(update.message.voice.file_id)
        file_path = f"voice_{user_id}.ogg"
        await voice_file.download_to_drive(file_path)

        # 2. Транскрибация
        transcript = await ai_engine.transcribe_audio(file_path)
        
        # Удаляем файл
        if os.path.exists(file_path):
            os.remove(file_path)

        if not transcript:
            await update.message.reply_text("⚠️ Не удалось распознать голос.")
            return

        # 3. Отправляем пользователю, что мы услышали
        await update.message.reply_text(f"🎤 <i>Вы сказали:</i> \"{transcript}\"", parse_mode='HTML')

        # 4. Отправляем текст в ИИ как обычное сообщение
        await process_ai_request(update, context, transcript)

    except Exception as e:
        logger.error(f"Voice Error: {e}")
        await update.message.reply_text("⚠️ Ошибка обработки голоса.")

# --- ФУНКЦИЯ ЗАПРОСА К ИИ ---
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

    # Определяем модель (Юзерская или Дефолтная)
    model = USER_MODELS.get(user_id, config.DEFAULT_MODEL)

    try:
        ai_response, tokens_spent = await ai_engine.get_response(full_context, model)
        db.add_message(session_id, "assistant", ai_response, model=model)
        db.update_tokens(user_id, tokens_spent)
        total_spent = db.get_total_tokens(user_id)

        # Если модель не базовая, покажем её в футере
        model_name = model.split('/')[-1] # openai/gpt-4o -> gpt-4o
        
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

# --- CALLBACKS ---
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data
    
    # 1. СМЕНА МОДЕЛИ
    if data.startswith("setmodel_"):
        new_model = data.split("setmodel_")[1]
        USER_MODELS[user_id] = new_model
        await query.answer(f"🧠 Модель изменена на {new_model}")
        await query.edit_message_text(f"✅ <b>Модель активирована:</b> {new_model}", parse_mode='HTML')
        return

    # 2. УДАЛЕНИЕ
    if data.startswith("del_"):
        session_id = int(data.split("_")[1])
        if db.delete_session(user_id, session_id):
            await query.answer("🗑 Чат удален")
            new_markup = get_history_keyboard(user_id)
            if new_markup:
                await query.edit_message_reply_markup(reply_markup=new_markup)
            else:
                await query.edit_message_text("📂 Архив пуст.")
        else:
            await query.answer("⚠️ Ошибка", show_alert=True)
        return

    await query.answer()

    # 3. ОПЛАТА
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
        pay_btn = InlineKeyboardMarkup([
            [InlineKeyboardButton("📨 Отправить чек Архитектору", url="https://t.me/vinixspb")],
            [InlineKeyboardButton("🔙 Назад", callback_data="back_to_tariffs")]
        ])
        await query.edit_message_text(invoice_text, reply_markup=pay_btn, parse_mode='HTML')
        return

    if data == "back_to_tariffs":
        await query.edit_message_text("💳 <b>ВЫБОР УРОВНЯ ДОСТУПА</b>", reply_markup=get_subscription_keyboard(), parse_mode='HTML')
        return

    # 4. ЗАГРУЗКА
    if data.startswith("session_"):
        session_id = int(data.split("_")[1])
        if db.activate_session(user_id, session_id):
            title = db.get_session_title(session_id)
            await query.message.reply_text(f"📂 <b>Чат загружен:</b> {title}", parse_mode='HTML')
        else:
            await query.message.reply_text("⚠️ Ошибка.")

async def send_paywall(update: Update):
    await update.message.reply_text(config.MSG_NO_SUB, reply_markup=get_subscription_keyboard(), parse_mode='HTML')

async def post_init(application: Application):
    await application.bot.set_my_commands([BotCommand("start", "Главное Меню")])

def main():
    if not config.BOT_TOKEN_ORACLE: return
    logger.info("👁 vnxORACLE: ONLINE")
    app = Application.builder().token(config.BOT_TOKEN_ORACLE).post_init(post_init).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    # Добавляем обработчик ГОЛОСА
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.add_handler(CallbackQueryHandler(handle_callback))
    
    app.run_polling()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
