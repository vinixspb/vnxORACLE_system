import logging
import asyncio
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from telegram.constants import ChatAction

# --- МОДУЛИ ---
import config
from services.sheets_manager import GoogleSheetsManager
from services.ai_engine import AIEngine
from services.database import Database

# --- ЛОГИ ---
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("apscheduler").setLevel(logging.WARNING)
logging.getLogger("googleapiclient").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# --- ИНИЦИАЛИЗАЦИЯ ---
try:
    sheets_mgr = GoogleSheetsManager()
    ai_engine = AIEngine()
    db = Database()
    logger.info("✅ Services OK")
except Exception as e:
    logger.critical(f"❌ Init Error: {e}")

# --- UI: ГЛАВНАЯ КЛАВИАТУРА ---
def get_main_keyboard():
    keyboard = [
        [KeyboardButton(config.BTN_NEW_DIALOG), KeyboardButton(config.BTN_HISTORY)],
        [KeyboardButton(config.BTN_PROFILE), KeyboardButton(config.BTN_TARIFFS)],
        [KeyboardButton(config.BTN_CHANGE_MODEL), KeyboardButton(config.BTN_HELP)] # <-- Добавили Поддержку сюда
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# --- UI: МЕНЮ ПОКУПКИ (Цены обновлены) ---
def get_subscription_keyboard():
    keyboard = [
        [InlineKeyboardButton("🟢 START (390₽)", callback_data="buy_START")],
        [InlineKeyboardButton("🟡 PRO (990₽)", callback_data="buy_PRO")],
        [InlineKeyboardButton("🔴 NEO (1490₽)", callback_data="buy_NEO")],
        [InlineKeyboardButton("👨‍💻 Связь с Архитектором", url="https://t.me/vinixspb")]
    ]
    return InlineKeyboardMarkup(keyboard)

# --- ЛОГИКА ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.info(f"👤 Start: {user.id}")

    # Проверяем тариф
    tariff = sheets_mgr.get_user_tariff(user.id)

    # 1. Если тарифа НЕТ (None)
    if not tariff:
        # Показываем Приветствие (Рекламу) + Меню покупки
        await update.message.reply_text(config.MSG_WELCOME, parse_mode='HTML')
        await update.message.reply_text(config.MSG_NO_SUB, reply_markup=get_subscription_keyboard(), parse_mode='HTML')
        return

    # 2. Если тариф ЕСТЬ -> Строго твой текст
    db.create_session(user.id, title="Новая сессия")
    
    msg_granted = (
        "👁 <b>Доступ разрешен.</b>\n"
        f"Ваш уровень: <b>{tariff}</b>\n\n"
        "Добро пожаловать в систему."
    )
    
    await update.message.reply_text(
        msg_granted,
        reply_markup=get_main_keyboard(),
        parse_mode='HTML'
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text
    user_id = user.id

    user_tariff = sheets_mgr.get_user_tariff(user_id)

    # --- СИСТЕМНЫЕ КНОПКИ ---

    if text == config.BTN_NEW_DIALOG:
        if not user_tariff: return await send_paywall(update)
        db.create_session(user_id, title="Новый диалог")
        await update.message.reply_text("♻️ <b>Новый чат создан.</b>", parse_mode='HTML')
        return

    if text == config.BTN_HISTORY:
        if not user_tariff: return await send_paywall(update)
        sessions = db.get_user_sessions(user_id, limit=10)
        if not sessions:
            await update.message.reply_text("📂 Архив пуст.")
        else:
            keyboard_buttons = []
            for s in sessions:
                date_short = s['created_at'][5:16]
                btn_text = f"{s['title']} ({date_short})"
                keyboard_buttons.append([InlineKeyboardButton(text=btn_text, callback_data=f"session_{s['id']}")])
            markup = InlineKeyboardMarkup(keyboard_buttons)
            await update.message.reply_text("💾 <b>ИСТОРИЯ ЧАТОВ:</b>", reply_markup=markup, parse_mode='HTML')
        return

    if text == config.BTN_PROFILE:
        status = f"✅ {user_tariff}" if user_tariff else "❌ NO ACCESS"
        limit = config.LIMITS.get(user_tariff, 0) if user_tariff else 0
        await update.message.reply_text(
            f"👤 <b>ПРОФИЛЬ</b>\nID: <code>{user_id}</code>\nStatus: <b>{status}</b>\nПамять: {limit} msg\nModel: {config.DEFAULT_MODEL}", 
            parse_mode='HTML'
        )
        return
    
    if text == config.BTN_TARIFFS:
        await update.message.reply_text(
            "💳 <b>ВЫБОР УРОВНЯ ДОСТУПА</b>\nВыберите тариф для подключения или апгрейда:",
            reply_markup=get_subscription_keyboard(),
            parse_mode='HTML'
        )
        return

    # Логика кнопки ПОДДЕРЖКА
    if text == config.BTN_HELP:
        await update.message.reply_text(
            "🆘 <b>ПОДДЕРЖКА АРХИТЕКТОРА</b>\n\n"
            "Если возникли сбои в Матрице или вопросы по оплате:\n"
            "👨‍💻 @vinixspb",
            parse_mode='HTML'
        )
        return

    if text == config.BTN_CHANGE_MODEL:
        if not user_tariff: return await send_paywall(update)
        if user_tariff == "START":
            await update.message.reply_text(f"🔒 Смена моделей доступна на тарифах <b>PRO</b> и <b>NEO</b>.\nУ вас: {user_tariff}", parse_mode='HTML')
        else:
             await update.message.reply_text("🧠 <b>ВЫБОР МОДЕЛИ:</b>\n(Функционал в разработке)", parse_mode='HTML')
        return

    # --- AI ---
    
    if not user_tariff:
        return await send_paywall(update)

    await context.bot.send_chat_action(chat_id=user_id, action=ChatAction.TYPING)

    session_id = db.get_active_session(user_id)
    history = db.get_history(session_id, limit=5)
    if not history:
        db.update_session_title(session_id, text)
    db.add_message(session_id, "user", text)

    history_depth = config.LIMITS.get(user_tariff, 10)
    full_context = db.get_history(session_id, limit=history_depth)

    try:
        ai_response = await ai_engine.get_response(full_context, config.DEFAULT_MODEL)
        db.add_message(session_id, "assistant", ai_response, model=config.DEFAULT_MODEL)
        final_text = f"{ai_response}\n\n⚙️ <i>Model: {config.DEFAULT_MODEL}</i>"
        try:
            await update.message.reply_text(final_text, parse_mode='Markdown')
        except:
            await update.message.reply_text(final_text, parse_mode='HTML')
    except Exception as e:
        logger.error(f"AI Error: {e}")
        await update.message.reply_text("⚠️ Ошибка связи.")

async def send_paywall(update: Update):
    await update.message.reply_text(config.MSG_NO_SUB, reply_markup=get_subscription_keyboard(), parse_mode='HTML')

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    data = query.data
    
    if data.startswith("buy_"):
        plan = data.split("_")[1]
        info = config.TARIFF_INFO.get(plan, "Error")
        
        pay_btn = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"💸 Оплатить {plan}", url=config.LINK_GATEWAY)],
            [InlineKeyboardButton("🔙 Назад", callback_data="back_to_tariffs")]
        ])
        
        await query.edit_message_text(
            f"{info}\n\n<i>Для оплаты вы будете перенаправлены в платежный шлюз.</i>",
            reply_markup=pay_btn,
            parse_mode='HTML'
        )
        return

    if data == "back_to_tariffs":
        await query.edit_message_text(
            "💳 <b>ВЫБОР УРОВНЯ ДОСТУПА</b>",
            reply_markup=get_subscription_keyboard(),
            parse_mode='HTML'
        )
        return

    if data.startswith("session_"):
        session_id = int(data.split("_")[1])
        if db.activate_session(user_id, session_id):
            title = db.get_session_title(session_id)
            await query.message.reply_text(f"📂 <b>Чат загружен:</b> {title}", parse_mode='HTML')
        else:
            await query.message.reply_text("⚠️ Ошибка.")

async def post_init(application: Application):
    await application.bot.set_my_commands([BotCommand("start", "Главное Меню")])

def main():
    if not config.BOT_TOKEN_ORACLE: return
    logger.info("👁 vnxORACLE: ONLINE")
    app = Application.builder().token(config.BOT_TOKEN_ORACLE).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.run_polling()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
