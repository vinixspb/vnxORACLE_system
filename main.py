import logging
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, BotCommand
import config
from handlers import start, handle_text, handle_voice, handle_callback

# Логгер уже настроен в loader.py, но main тоже хочет писать логи
logger = logging.getLogger(__name__)

async def post_init(application: Application):
    await application.bot.set_my_commands([BotCommand("start", "Главное Меню")])

def main():
    if not config.BOT_TOKEN_ORACLE:
        logger.error("❌ Token not found")
        return

    logger.info("👁 vnxORACLE: ONLINE")
    
    app = Application.builder().token(config.BOT_TOKEN_ORACLE).post_init(post_init).build()
    
    # Регистрируем обработчики из файла handlers.py
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.add_handler(CallbackQueryHandler(handle_callback))
    
    app.run_polling()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
