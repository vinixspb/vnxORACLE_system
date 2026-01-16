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

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

try:
    sheets_mgr = GoogleSheetsManager()
    ai_engine = AIEngine()
    db = Database()
    logger.info("✅ Services OK")
except Exception as e:
    logger.critical(f"❌ Init Error: {e}")

# --- UI: ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---

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
    """Генерирует кнопки истории с крестиками удаления"""
    sessions = db.get_user_sessions(user_id, limit=10)
    if not sessions:
        return None
    
    keyboard = []
    for s in sessions:
        date_short = s['created_at'][5:16]
        title_text = f"{s['title']} ({date_short})"
        
        # ДВЕ КНОПКИ В СТРОКУ: [ Загрузить ] [ ❌ ]
        btn_load = InlineKeyboardButton(text=title_text, callback_data=f"session_{s['id']}")
        btn_del = InlineKeyboardButton(text="❌", callback_data=f"del_{s['id']}")
        
        keyboard.append([btn_load, btn_del])
        
    return InlineKeyboardMarkup(keyboard)

# --- ЛОГИКА ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.info(f"👤 Start: {user.id}")

    tariff = sheets_mgr.get_user_tariff(user.id)

    if not tariff:
        await update.message.reply_text(config.MSG_WELCOME, parse_mode='HTML')
        await update.message.reply_text(config.MSG_NO_SUB, reply_markup=get_subscription_keyboard(), parse_mode='HTML')
        return

    db.create_session(user.id, title="Новая сессия")
    # Строго твой текст
    await update.message.reply_text(
        f"👁 <b>Доступ разрешен.</b>\nВаш уровень: <b>{tariff}</b>\n\nДобро пожаловать в систему.",
        reply_markup=get_main_keyboard(),
        parse_mode='HTML'
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text
    user_id = user.id
    user_tariff = sheets_mgr.get_user_tariff(user_id)

    # --- КНОПКИ ---

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
            await update.message.reply_text("💾 <b>ИСТОРИЯ ЧАТОВ:</b>\n<i>Нажмите на название для загрузки или ❌ для удаления.</i>", reply_markup=markup, parse_mode='HTML')
        return

    if text == config.BTN_PROFILE:
        status = f"✅ {user_tariff}" if user_tariff else "❌ NO ACCESS"
        limit = config.LIMITS.get(user_tariff, 0) if user_tariff else 0
        total_tokens = db.get_total_tokens(user_id)
        
        await update.message.reply_text(
            f"👤 <b>ПРОФИЛЬ</b>\n"
            f"ID: <code>{user_id}</code>\n"
            f"Status: <b>{status}</b>\n"
            f"Memory: {limit} msg\n"
            f"Spent Tokens: <b>{total_tokens}</b>\n"
            f"Current Model: {config.DEFAULT_MODEL}", 
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

    if text == config.BTN_HELP:
        # Используем текст из конфига
        await update.message.reply_text(config.MSG_SUPPORT, parse_mode='HTML')
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
        ai_response, tokens_spent = await ai_engine.get_response(full_context, config.DEFAULT_MODEL)
        db.add_message(session_id, "assistant", ai_response, model=config.DEFAULT_MODEL)
        db.update_tokens(user_id, tokens_spent)
        total_spent = db.get_total_tokens(user_id)

        # Красивый вывод с цитатой для технички
        final_text = (
            f"{ai_response}\n\n"
            f"<blockquote>⚙️ {config.DEFAULT_MODEL} | 🎫 {tokens_spent} tok | ∑ {total_spent}</blockquote>"
        )
        
        try:
            await update.message.reply_text(final_text, parse_mode='HTML')
        except:
            await update.message.reply_text(f"{ai_response}\n\n(Tokens: {tokens_spent})")
            
    except Exception as e:
        logger.error(f"AI Error: {e}")
        await update.message.reply_text("⚠️ Ошибка связи.")

async def send_paywall(update: Update):
    await update.message.reply_text(config.MSG_NO_SUB, reply_markup=get_subscription_keyboard(), parse_mode='HTML')

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    
    # Не делаем query.answer() сразу, так как при удалении может быть алерт
    
    data = query.data
    
    # --- УДАЛЕНИЕ СЕССИИ ---
    if data.startswith("del_"):
        session_id = int(data.split("_")[1])
        if db.delete_session(user_id, session_id):
            await query.answer("🗑 Чат удален")
            # Обновляем список кнопок прямо в сообщении
            new_markup = get_history_keyboard(user_id)
            if new_markup:
                await query.edit_message_reply_markup(reply_markup=new_markup)
            else:
                await query.edit_message_text("📂 Архив пуст.")
        else:
            await query.answer("⚠️ Ошибка удаления", show_alert=True)
        return

    await query.answer()

    # --- ОПЛАТА ---
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
        await query.edit_message_text(
            "💳 <b>ВЫБОР УРОВНЯ ДОСТУПА</b>",
            reply_markup=get_subscription_keyboard(),
            parse_mode='HTML'
        )
        return

    # --- ЗАГРУЗКА СЕССИИ ---
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
