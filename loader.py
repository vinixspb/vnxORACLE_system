import logging
from services.sheets_manager import GoogleSheetsManager
from services.ai_engine import AIEngine
from services.database import Database
# 👇 Импортируем готовый объект аудио-студии
from services.audio_studio import audio_studio 

# Настройка логгера
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
# Убираем шум от библиотек http-запросов
logging.getLogger("httpx").setLevel(logging.WARNING) 

logger = logging.getLogger(__name__)

# Инициализация сервисов
try:
    # Эти сервисы инициализируются здесь
    sheets_mgr = GoogleSheetsManager()
    ai_engine = AIEngine()
    db = Database()
    
    # audio_studio инициализируется внутри своего файла при импорте,
    # но мы проверяем, что он загрузился
    if audio_studio:
        logger.info("✅ Services Initialized: Sheets, AI, DB, Audio Studio")
    else:
        logger.warning("⚠️ Services: Audio Studio failed to load")

except Exception as e:
    logger.critical(f"❌ Critical Init Error: {e}")
    raise e

# Оперативная память для выбора моделей пользователями
# {user_id: "model_name"}
USER_MODELS = {}
