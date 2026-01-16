import logging
import asyncio
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
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
    logger.info("✅ Services: Sheets, AI, Database (Sessions) - OK")
except Exception as e:
    logger.critical(f"❌ Init Error: {e}")

# --- UI ---
def get_main_keyboard():
    keyboard = [
        [KeyboardButton(config.BTN_NEW_DIALOG), KeyboardButton(config.BTN_HISTORY)],
        [KeyboardButton(config.BTN_PROFILE), KeyboardButton(config.BTN_HELP)]
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

    # --- 1. КНОПКИ МЕНЮ ---

    if text == config.BTN_NEW_DIALOG:
        # Создаем новую сессию в БД
        db.create_session(user_id, title="Новый диалог")
        await update.message.reply_text("♻️ <b>Новый чат создан.</b>\nПамять очищена. О чем поговорим?", parse_mode='HTML')
        return

    if text == config.BTN_HISTORY:
        # Берем список сессий (пока лимит 10 для всех)
        sessions = db.get_user_sessions(user_id, limit=10)
        
        if not sessions:
            await update.message.reply_text("📂 Архив пуст.")
        else:
            msg_text = "<b>💾 АРХИВ ПОСЛЕДНИХ ЧАТОВ:</b>\n\n"
            for s in sessions:
                # s['created_at'] это строка времени, можно обрезать до даты
                date_str = s['created_at'][:16] 
                msg_text += f"🔹 <b>{s['title']}</b>\n   └ <i>{date_str}</i>\n\n"
            
            msg_text += "<i>Чтобы продолжить старую тему, пока нужно начинать новый диалог. (Функция загрузки в разработке)</i>"
            await update.message.reply_text(msg_text, parse_mode='HTML')
        return

    if text == config.BTN_PROFILE:
        access = sheets_mgr.check_ai_access(user_id)
        status = "✅ ACTIVE" if access else "❌ INACTIVE"
        await update.message.reply_text(
            f"👤 <b>ПРОФИЛЬ</b>\nID: <code>{user_id}</code>\nStatus: <b>{status}</b>\nModel: {config.DEFAULT_MODEL}", 
            parse_mode='HTML'
        )
        return

    if text == config.BTN_HELP:
        await update.message.reply_text("🆘 <b>ПОМОЩЬ</b>\n\nЯ помню контекст внутри текущего чата.\nНажми 'НОВЫЙ ЧАТ', чтобы сменить тему.", parse_mode='HTML')
        return
    
    if text == config.BTN_CHANGE_MODEL:
        await update.message.reply_text("🧠 Выбор моделей доступен в версии PRO.", parse_mode='HTML')
        return

    # --- 2. ОБРАБОТКА ЗАПРОСА К ИИ ---
    
    if not sheets_mgr.check_ai_access(user_id):
        await update.message.reply_text("⛔️ Подписка не активна.")
        return

    await context.bot.send_chat_action(chat_id=user_id, action=ChatAction.TYPING)

    # 1. Получаем ID текущей сессии
    session_id = db.get_active_session(user_id)

    # 2. Если это первое сообщение в сессии — переименовываем сессию
    history = db.get_history(session_id, limit=5)
    if not history:
        db.update_session_title(session_id, text)

    # 3. Сохраняем сообщение юзера
    db.add_message(session_id, "user", text)

    # 4. Достаем полный контекст для нейросети
    full_context = db.get_history(session_id, limit=config.LIMITS["START"])

    try:
        # 5. Запрос к ИИ
        ai_response = await ai_engine.get_response(full_context, config.DEFAULT_MODEL)

        # 6. Сохраняем ответ
        db.add_message(session_id, "assistant", ai_response, model=config.DEFAULT_MODEL)

        # 7. Формируем красивый ответ с подписью
        final_text = f"{ai_response}\n\n⚙️ <i>Model: {config.DEFAULT_MODEL}</i>"

        try:
            await update.message.reply_text(final_text, parse_mode='Markdown')
        except:
            await update.message.reply_text(final_text, parse_mode='HTML')

    except Exception as e:
        logger.error(f"AI Error: {e}")
        await update.message.reply_text("⚠️ Ошибка связи. Попробуйте еще раз.")

# --- ЗАПУСК ---
def main():
    if not config.BOT_TOKEN_ORACLE:
        return
    logger.info("👁 vnxORACLE: ONLINE")
    app = Application.builder().token(config.BOT_TOKEN_ORACLE).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.run_polling()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
