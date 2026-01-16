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

# --- UI: ГЛАВНАЯ КЛАВИАТУРА (5 кнопок) ---
def get_main_keyboard():
    keyboard = [
        [KeyboardButton(config.BTN_NEW_DIALOG), KeyboardButton(config.BTN_HISTORY)],
        [KeyboardButton(config.BTN_PROFILE), KeyboardButton(config.BTN_HELP)],
        [KeyboardButton(config.BTN_CHANGE_MODEL)] # Пятая кнопка внизу
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# --- ЛОГИКА ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.info(f"👤 Start: {user.id}")

    if not sheets_mgr.check_ai_access(user.id):
        await update.message.reply_text("⛔️ <b>ДОСТУП ЗАПРЕЩЕН</b>\nНет активной подписки.", parse_mode='HTML')
        return

    # При старте создаем новую сессию
    db.create_session(user.id, title="Новая сессия")
    
    await update.message.reply_text(config.MSG_WELCOME, reply_markup=get_main_keyboard(), parse_mode='HTML')

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text
    user_id = user.id

    # --- 1. СИСТЕМНЫЕ КНОПКИ ---

    if text == config.BTN_NEW_DIALOG:
        db.create_session(user_id, title="Новый диалог")
        await update.message.reply_text("♻️ <b>Новый чат создан.</b>\nКонтекст сброшен. О чем поговорим?", parse_mode='HTML')
        return

    if text == config.BTN_HISTORY:
        # Достаем последние 10 сессий
        sessions = db.get_user_sessions(user_id, limit=10)
        
        if not sessions:
            await update.message.reply_text("📂 Архив пуст.")
        else:
            # СОЗДАЕМ ИНЛАЙН КНОПКИ
            keyboard_buttons = []
            for s in sessions:
                # Дата: 2024-01-01 12:00
                date_short = s['created_at'][5:16] # mm-dd HH:MM
                btn_text = f"{s['title']} ({date_short})"
                # callback_data: 'session_123'
                keyboard_buttons.append([InlineKeyboardButton(text=btn_text, callback_data=f"session_{s['id']}")])
            
            markup = InlineKeyboardMarkup(keyboard_buttons)
            await update.message.reply_text("💾 <b>ИСТОРИЯ ЧАТОВ:</b>\nНажми, чтобы продолжить диалог:", reply_markup=markup, parse_mode='HTML')
        return

    if text == config.BTN_PROFILE:
        access = sheets_mgr.check_ai_access(user_id)
        status = "✅ ACTIVE" if access else "❌ INACTIVE"
        await update.message.reply_text(
            f"👤 <b>ПРОФИЛЬ</b>\nID: <code>{user_id}</code>\nStatus: <b>{status}</b>\nModel: {config.DEFAULT_MODEL}", 
            parse_mode='HTML'
        )
        return
    
    if text == config.BTN_CHANGE_MODEL:
        await update.message.reply_text("🧠 Выбор моделей доступен в версии PRO.", parse_mode='HTML')
        return

    if text == config.BTN_HELP:
        await update.message.reply_text("🆘 <b>ПОМОЩЬ</b>\n\nЯ помню контекст. Чтобы сменить тему, нажми 'НОВЫЙ ЧАТ'.\nЧтобы вернуться к старой теме, нажми 'ИСТОРИЯ ЧАТОВ'.", parse_mode='HTML')
        return

    # --- 2. ОБЩЕНИЕ С ИИ ---
    
    if not sheets_mgr.check_ai_access(user_id):
        await update.message.reply_text("⛔️ Подписка не активна.")
        return

    await context.bot.send_chat_action(chat_id=user_id, action=ChatAction.TYPING)

    # 1. Получаем ID АКТИВНОЙ сессии (это и решает проблему потери контекста)
    session_id = db.get_active_session(user_id)

    # 2. Если чат новый, называем его по первому сообщению
    history = db.get_history(session_id, limit=5)
    if not history:
        db.update_session_title(session_id, text)

    # 3. Пишем в базу
    db.add_message(session_id, "user", text)

    # 4. Формируем контекст
    full_context = db.get_history(session_id, limit=config.LIMITS["START"])

    try:
        ai_response = await ai_engine.get_response(full_context, config.DEFAULT_MODEL)
        
        # 5. Сохраняем ответ
        db.add_message(session_id, "assistant", ai_response, model=config.DEFAULT_MODEL)

        # 6. Отправляем
        final_text = f"{ai_response}\n\n⚙️ <i>Model: {config.DEFAULT_MODEL}</i>"
        try:
            await update.message.reply_text(final_text, parse_mode='Markdown')
        except:
            await update.message.reply_text(final_text, parse_mode='HTML')

    except Exception as e:
        logger.error(f"AI Error: {e}")
        await update.message.reply_text("⚠️ Ошибка связи.")

# --- ОБРАБОТЧИК НАЖАТИЙ НА ИСТОРИЮ (INLINE) ---

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer() # Чтобы кружок загрузки пропал

    data = query.data
    if data.startswith("session_"):
        # Извлекаем ID: session_5 -> 5
        session_id = int(data.split("_")[1])
        
        # Переключаем активную сессию в базе
        success = db.activate_session(user_id, session_id)
        
        if success:
            title = db.get_session_title(session_id)
            await query.message.reply_text(f"📂 <b>Чат загружен:</b> {title}\nКонтекст восстановлен. Можете продолжать.", parse_mode='HTML')
        else:
            await query.message.reply_text("⚠️ Ошибка восстановления чата.")

# --- УСТАНОВКА МЕНЮ (СЛЕВА) ---
async def post_init(application: Application):
    """Устанавливает кнопку Menu"""
    await application.bot.set_my_commands([
        BotCommand("start", "Главное Меню")
    ])

# --- ЗАПУСК ---
def main():
    if not config.BOT_TOKEN_ORACLE:
        return
    logger.info("👁 vnxORACLE: ONLINE")
    
    # post_init нужен для установки кнопки Меню
    app = Application.builder().token(config.BOT_TOKEN_ORACLE).post_init(post_init).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    # Добавляем обработчик для Инлайн-кнопок
    app.add_handler(CallbackQueryHandler(handle_callback))
    
    app.run_polling()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
