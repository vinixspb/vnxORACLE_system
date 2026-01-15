import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import config

# Логирование (без шума)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Приветствие Оракула"""
    user = update.effective_user
    logger.info(f"User {user.id} accessed vnxORACLE.")
    await update.message.reply_text(config.MSG_WELCOME, parse_mode='HTML')

def main():
    if not config.BOT_TOKEN_ORACLE:
        logger.error("❌ Токен бота не найден! Проверьте .env")
        return

    logger.info("👁 vnxORACLE_system: ONLINE. Listening...")
    
    app = Application.builder().token(config.BOT_TOKEN_ORACLE).build()
    app.add_handler(CommandHandler("start", start))
    
    app.run_polling()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
