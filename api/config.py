import os
from dotenv import load_dotenv

load_dotenv()

# =========================================================
# 🔐 API KEYS
# =========================================================
OPENROUTER_API_KEY_START = os.getenv("OPENROUTER_API_KEY_START")
OPENROUTER_API_KEY_PRO = os.getenv("OPENROUTER_API_KEY_PRO")
OPENROUTER_API_KEY_NEO = os.getenv("OPENROUTER_API_KEY_NEO")

# Для обратной совместимости
OPENROUTER_API_KEY = OPENROUTER_API_KEY_START or os.getenv("OPENROUTER_API_KEY")

# =========================================================
# 🗄️ GOOGLE SHEETS CRM
# =========================================================
GOOGLE_CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS_JSON")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")

# =========================================================
# 📱 TELEGRAM NOTIFICATIONS
# =========================================================
BOT_TOKEN_ORACLE = os.getenv("BOT_TOKEN_ORACLE")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

# =========================================================
# 🌐 SERVER CONFIG
# =========================================================
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

# =========================================================
# 🧠 AI ENGINE
# =========================================================
TEXT_BASE_URL = os.getenv("TEXT_BASE_URL", "https://openrouter.ai/api/v1")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "openai/gpt-4o-mini")
AI_TEMPERATURE = float(os.getenv("AI_TEMPERATURE", "0.7"))

# =========================================================
# 🛡️ RATE LIMITING / ЗАЩИТА
# =========================================================
# Максимум запросов к /api/chat с одного IP за окно
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "20"))
# Длина окна в секундах
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))
# Максимум сообщений на одну сессию (0 = без лимита)
MAX_MESSAGES_PER_SESSION = int(os.getenv("MAX_MESSAGES_PER_SESSION", "40"))
# Максимальная длина одного сообщения в символах
MAX_MESSAGE_LENGTH = int(os.getenv("MAX_MESSAGE_LENGTH", "2000"))
# IP, от которых принимаем X-Forwarded-For. Заголовок подделывается любым
# клиентом, поэтому доверяем ему только от своего reverse-proxy (Caddy).
TRUSTED_PROXIES = {
    ip.strip()
    for ip in os.getenv("TRUSTED_PROXIES", "127.0.0.1,::1").split(",")
    if ip.strip()
}

# =========================================================
# 📋 SYSTEM PROMPTS
# =========================================================
PROMPTS_DIR = os.path.join(os.path.dirname(__file__), "prompts")

def load_prompt(filename: str) -> str:
    """Загрузить system prompt из файла"""
    path = os.path.join(PROMPTS_DIR, filename)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

SALES_CONSULTANT_PROMPT = load_prompt("sales_consultant.txt")
