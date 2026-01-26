import logging
from services.sheets_manager import GoogleSheetsManager
from services.ai_engine import AIEngine
from services.database import Database
from services.audio_studio import audio_studio 

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING) 
logger = logging.getLogger(__name__)

try:
    # Инициализация сервисов
    sheets_mgr = GoogleSheetsManager()
    ai_engine = AIEngine()
    db = Database()
    
    if audio_studio:
        logger.info("✅ vnxORACLE: Все системы (Sheets, AI, DB, Audio) активны.")
    else:
        logger.warning("⚠️ vnxORACLE: Audio Studio не загружена.")

except Exception as e:
    logger.critical(f"❌ Critical Init Error: {e}")
    raise e

# Оперативная память для выбора моделей пользователями
USER_MODELS = {}
