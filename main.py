import logging
import asyncio
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ChatAction

# --- НАШИ МОДУЛИ ---
import config
from services.sheets_manager import GoogleSheetsManager
from services.ai_engine import AIEngine

# =========================================================
# 🔧 НАСТРОЙКА ЛОГИРОВАНИЯ
# =========================================================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("apscheduler").setLevel(logging.WARNING)
logging.getLogger("googleapiclient").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# =========================================================
# 🚀 ИНИЦИАЛИЗАЦИЯ СЕРВИСОВ
# =========================================================
try:
    sheets_mgr = GoogleSheetsManager()
    ai_engine = AIEngine()
    logger.info("✅ Services initialized: Sheets & AI")
except Exception as e:
    logger.critical(f"❌ Critical Error initializing services: {e}")

# ОПЕРАТИВНАЯ ПАМЯТЬ
user_contexts = {}

# =========================================================
# 🎹 ИНТЕРФЕЙС (UI)
# =========================================================
def get_main_keyboard():
    keyboard = [
        [KeyboardButton(config.BTN_NEW_DIALOG), KeyboardButton(config.BTN_CHANGE_MODEL)],
        [KeyboardButton(config.BTN_PROFILE), KeyboardButton(config.BTN_HELP)]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# =========================================================
# 🧠 ЛОГИКА БОТА
# =========================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Приветствие Оракула"""
    user = update.effective_user
    logger.info(f"👤 User {user.id} ({user.username}) initiated session.")

    # 1. Проверка доступа
    if not sheets_mgr.check_ai_access(user.id):
        logger.warning(f"⛔️ Access DENIED for {user.id}")
        await update.message.reply_text(
            "⛔️ <b>ДОСТУП ЗАПРЕЩЕН</b>\n\n"
            "Ваша подписка на Нейро-модуль не активна.\n"
            "Для активации обратитесь к Шлюзу: @vnxMATRIX_Gateway_bot",
            parse_mode='HTML'
        )
        return

    # 2. Сброс памяти
    user_contexts[user.id] = []

    # 3. Приветствие
    await update.message.reply_text(
        config.MSG_WELCOME,
        reply_markup=get_main_keyboard(),
        parse_mode='HTML'
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Главный мозг"""
    user = update.effective_user
    text = update.message.text
    user_id = user.id

    # --- СИСТЕМНЫЕ КНОПКИ ---
    if text == config.BTN_NEW_DIALOG:
        user_contexts[user_id] = []
        await update.message.reply_text("⚡️ <b>Память очищена.</b> Жду новый запрос.", parse_mode='HTML')
        return

    if text == config.BTN_PROFILE:
        access = sheets_mgr.check_ai_access(user_id)
        status_icon = "✅ ACTIVE" if access else "❌ INACTIVE"
        await update.message.reply_text(
            f"👤 <b>ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ</b>\n"
            f"ID: <code>{user_id}</code>\n"
            f"Статус: <b>{status_icon}</b>\n"
            f"Модель: {config.DEFAULT_MODEL}",
            parse_mode='HTML'
        )
        return

    if text == config.BTN_HELP:
        await update.message.reply_text(
            "💾 <b>СПРАВКА</b>\n\n"
            "Я помню контекст последних 20 сообщений.\n"
            "Чтобы сменить тему, нажми <b>НОВЫЙ ДИАЛОГ</b>.",
            parse_mode='HTML'
        )
        return

    if text == config.BTN_CHANGE_MODEL:
        await update.message.reply_text("🧠 Выбор моделей доступен в версии PRO.", parse_mode='HTML')
        return

    # --- ЗАПРОС К НЕЙРОСЕТИ ---

    # Проверка доступа перед ответом
    if not sheets_mgr.check_ai_access(user_id):
        await update.message.reply_text(
            "⛔️ <b>ПОДПИСКА НЕ АКТИВНА</b>\n"
            "Обратитесь в @vnxMATRIX_Gateway_bot",
            parse_mode='HTML'
        )
        return

    await context.bot.send_chat_action(chat_id=user_id, action=ChatAction.TYPING)

    if user_id not in user_contexts:
        user_contexts[user_id] = []
    
    user_contexts[user_id].append({"role": "user", "content": text})

    if len(user_contexts[user_id]) > config.MAX_HISTORY_DEPTH:
        user_contexts[user_id] = user_contexts[user_id][-config.MAX_HISTORY_DEPTH:]

    try:
        ai_response = await ai_engine.get_response(
            messages=user_contexts[user_id],
            model=config.DEFAULT_MODEL
        )

        user_contexts[user_id].append({"role": "assistant", "content": ai_response})

        try:
            await update.message.reply_text(ai_response, parse_mode='Markdown')
        except Exception:
            await update.message.reply_text(ai_response)

    except Exception as e:
        logger.error(f"⚠️ AI Handler Error: {e}")
        await update.message.reply_text("⚠️ Сбой связи. Нажмите 'Новый диалог'.")

# =========================================================
# 🏁 ТОЧКА ВХОДА
# =========================================================
def main():
    if not config.BOT_TOKEN_ORACLE:
        logger.error("❌ Токен бота не найден! Проверьте .env")
        return

    logger.info("👁 vnxORACLE_system: ONLINE. Listening...")
    
    app = Application.builder().token(config.BOT_TOKEN_ORACLE).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    app.run_polling()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
