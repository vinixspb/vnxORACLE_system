import logging
import config

# Импорт всех системных модулей
from services.database import Database
from services.ai_engine import AIEngine
from services.audio_studio import AudioStudio
from services.video_studio import VideoStudio
from services.sheets_manager import GoogleSheetsManager

# Настройка глобального логгера для всей системы
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
# Уменьшаем шум от базовых библиотек, чтобы видеть только суть vnxORACLE
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("python-telegram-bot").setLevel(logging.ERROR)

logger = logging.getLogger(__name__)

try:
    logger.info("👁 vnxORACLE: Инициализация нейронных узлов...")

    # 1. Память (Database)
    db = Database()

    # 2. Матрица Доступов (Google Sheets)
    sheets_mgr = GoogleSheetsManager()

    # 3. Текстовый Разум и Зрение (AI Engine)
    ai_engine = AIEngine()

    # 4. Аудио-Студия (ElevenLabs + Fallback)
    audio_studio = AudioStudio()

    # 5. Кинематографический модуль (Video Studio Beta)
    video_studio = VideoStudio()

    logger.info("✅ vnxORACLE: Все системы синхронизированы и активны.")

except Exception as e:
    logger.critical(f"🆘 КРИТИЧЕСКИЙ СБОЙ ПРИ ЗАГРУЗКЕ: {e}")
    # В Матрице нельзя допускать работу неисправных узлов
    raise SystemExit("System failed to initialize. Check .env and services.")

# --- ОПЕРАТИВНАЯ ПАМЯТЬ (RUNTIME STATE) ---

# Хранилище текущих моделей пользователей {user_id: "model_id"}
# Позволяет не дергать БД при каждом сообщении
USER_MODELS = {}

# Хранилище временных состояний для мультимодальных запросов
# Например, для связки "Картинка + Текст"
USER_DATA_CACHE = {}
