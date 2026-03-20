import logging
import config
from handlers.media import handle_document
from telegram import BotCommand
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    CallbackQueryHandler, 
    filters
)

# Импортируем все хендлеры, включая новые модули Vision и Document
from handlers import (
    start, 
    handle_text, 
    handle_voice, 
    handle_photo, 
    handle_document, 
    handle_callback
)

# Логгер инициализируется в loader.py, здесь мы просто подхватываем его
logger = logging.getLogger(__name__)

async def post_init(application: Application):
    """
    Действия при запуске системы:
    1. Установка кнопки Меню (Bot Commands).
    2. Уведомление о готовности нейро-интерфейса.
    """
    await application.bot.set_my_commands([
        BotCommand("start", "👁 Перезагрузить нейро-линк")
    ])
    logger.info("📡 vnxORACLE: Нейро-интерфейс синхронизирован.")

def main():
    """Точка входа в Матрицу"""
    if not config.BOT_TOKEN_ORACLE:
        logger.critical("❌ ОШИБКА: BOT_TOKEN_ORACLE не обнаружен в .env")
        return

    logger.info("👁 vnxORACLE System: Инициализация потоков...")

    # Сборка приложения
    app = Application.builder().token(config.BOT_TOKEN_ORACLE).post_init(post_init).build()

    # --- РЕГИСТРАЦИЯ ОБРАБОТЧИКОВ (HANDLERS) ---

    # 1. Команды управления
    app.add_handler(CommandHandler("start", start))

    # 2. Обработка Кнопки Меню и обычного текста
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # 3. Модуль Зрения (Vision) - принимает фото и сжатые изображения
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    # 4. Модуль Слуха (Whisper STT) - обработка голосовых
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))

    # 5. Модуль Хранителя (The Vault) - обработка файлов, документов и видео
    app.add_handler(MessageHandler(filters.Document.ALL | filters.VIDEO, handle_document))

    # 6. Навигационный интерфейс (Inline Buttons)
    app.add_handler(CallbackQueryHandler(handle_callback))


    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    # Запуск бесконечного цикла (Polling)
    logger.info("👁 vnxORACLE: ONLINE")
    app.run_polling()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.warning("💾 vnxORACLE: Система переходит в режим гибернации...")
    except Exception as e:
        logger.critical(f"🆘 КРИТИЧЕСКИЙ СБОЙ СИСТЕМЫ: {e}")
