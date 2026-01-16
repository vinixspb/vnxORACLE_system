import logging
import asyncio
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ChatAction

# --- МОДУЛИ ---
import config
from services.sheets_manager import GoogleSheetsManager
from services.ai_engine import AIEngine
from services.database import Database  # <-- Добавили базу

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
    db = Database()  # <-- Запускаем базу
    logger.info("✅ System Modules Loaded")
except Exception as e:
    logger.critical(f"❌ Init Error: {e}")

# (Переменную user_contexts удалили, она больше не нужна!)

# --- UI ---
def get_main_keyboard():
    keyboard = [
        [KeyboardButton(config.BTN_NEW_DIALOG), KeyboardButton(config.BTN_HISTORY)], # <-- Новые кнопки
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

    # При старте можно очистить старую историю или оставить - на твой выбор.
    # Пока оставим, чтобы он помнил юзера.
    
    await update.message.reply_text(config.MSG_WELCOME, reply_markup=get_main_keyboard(), parse_mode='HTML')

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text
    user_id = user.id

    # --- КНОПКИ ---

    if text == config.BTN_NEW_DIALOG: # "♻️ НОВЫЙ ЧАТ"
        db.clear_history(user_id)
        await update.message.reply_text("♻️ <b>Память очищена.</b> Начинаем с чистого листа.", parse_mode='HTML')
        return

    if text == config.BTN_HISTORY: # "💾 ИСТОРИЯ"
        # Просто покажем последние 5 сообщений для теста
        history = db.get_history(user_id, limit=5)
        if not history:
            await update.message.reply_text("📂 Архив пуст.")
        else:
            msg_text = "<b>📂 ПОСЛЕДНИЕ ЗАПИСИ:</b>\n\n"
            for h in history:
                role_icon = "👤" if h['role'] == 'user' else "👁"
                # Обрезаем длинные сообщения для превью
                preview = (h['content'][:50] + '..') if len(h['content']) > 50 else h['content']
                msg_text += f"{role_icon} {preview}\n"
            await update.message.reply_text(msg_text, parse_mode='HTML')
        return

    if text == config.BTN_PROFILE:
        access = sheets_mgr.check_ai_access(user_id)
        status = "✅ ACTIVE" if access else "❌ INACTIVE"
        # Тут в будущем будем брать тариф из базы
        tariff = "START (Limit: 10)" 
        await update.message.reply_text(
            f"👤 <b>ПРОФИЛЬ</b>\nID: <code>{user_id}</code>\nStatus: <b>{status}</b>\nPlan: {tariff}", 
            parse_mode='HTML'
        )
        return

    if text == config.BTN_HELP:
        await update.message.reply_text("🆘 <b>ПОМОЩЬ</b>\n\nЯ помню контекст диалога.\nНажми 'НОВЫЙ ЧАТ', чтобы сбросить тему.", parse_mode='HTML')
        return

    # --- ИНТЕЛЛЕКТ ---
    
    if not sheets_mgr.check_ai_access(user_id):
        await update.message.reply_text("⛔️ Подписка не активна.")
        return

    await context.bot.send_chat_action(chat_id=user_id, action=ChatAction.TYPING)

    # 1. Сохраняем вопрос юзера в БД
    db.add_message(user_id, "user", text)

    # 2. Достаем историю (Лимит пока берем для тарифа START = 10)
    # В будущем сделаем: limit = config.LIMITS[user_tariff]
    history = db.get_history(user_id, limit=config.LIMITS["START"])

    try:
        # 3. Отправляем в ИИ
        ai_response = await ai_engine.get_response(history, config.DEFAULT_MODEL)

        # 4. Сохраняем ответ ИИ в БД
        db.add_message(user_id, "assistant", ai_response)

        # 5. Отправляем юзеру
        try:
            await update.message.reply_text(ai_response, parse_mode='Markdown')
        except:
            await update.message.reply_text(ai_response)

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
