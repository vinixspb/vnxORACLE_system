import logging
from services.sheets_manager import GoogleSheetsManager
from services.ai_engine import AIEngine
from services.database import Database

# Настройка логгера
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# Инициализация сервисов (Синглтоны)
try:
    sheets_mgr = GoogleSheetsManager()
    ai_engine = AIEngine()
    db = Database()
    logger.info("✅ Services Initialized: Sheets, AI, DB")
except Exception as e:
    logger.critical(f"❌ Critical Init Error: {e}")
    raise e

# Оперативная память для моделей {user_id: "model_name"}
USER_MODELS = {}
