import os
from dotenv import load_dotenv

load_dotenv()

# =========================================================
# 🔐 СИСТЕМНЫЕ НАСТРОЙКИ
# =========================================================
BOT_TOKEN_ORACLE = os.getenv("BOT_TOKEN_ORACLE")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY") 
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID") 
GOOGLE_CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS_JSON")

# =========================================================
# ⚙️ МОЗГ И ТАРИФЫ (LIMITS)
# =========================================================
# Модели
MODEL_BASIC = "openai/gpt-3.5-turbo"
MODEL_PRO = "openai/gpt-4o-mini"
MODEL_NEO = "anthropic/claude-3.5-sonnet"

# По умолчанию (для старта)
DEFAULT_MODEL = MODEL_BASIC

# Настройки контекста (Сколько сообщений помнить)
LIMITS = {
    "START": 10,  # Дешевый тариф
    "PRO": 30,    # Средний
    "NEO": 60     # Топ (Matrix Style)
}

SYSTEM_PROMPT = (
    "Ты — vnxORACLE, цифровой разум системы vnxMATRIX. "
    "Твоя цель — помогать пользователям, отвечать на вопросы и писать код. "
    "Отвечай кратко, точно и в стиле киберпанк/профессионал. "
    "Ты вежлив, но не эмоционален. Ты — Система."
)

AI_TEMPERATURE = 0.7

# =========================================================
# 🎹 КНОПКИ (UI)
# =========================================================
BTN_NEW_DIALOG = "♻️ НОВЫЙ ЧАТ"    # <-- Обновили
BTN_HISTORY = "💾 ИСТОРИЯ"        # <-- Обновили
BTN_PROFILE = "👤 МОЙ ПРОФИЛЬ"
BTN_HELP = "🆘 ПОМОЩЬ"
BTN_CHANGE_MODEL = "🧠 СМЕНИТЬ МОДЕЛЬ"

# =========================================================
# 💬 СООБЩЕНИЯ
# =========================================================
MSG_WELCOME = (
    "👁 <b>vnxORACLE SYSTEM v1.0</b>\n\n"
    "Добро пожаловать в систему.\n"
    "Я — интерфейс чистого знания.\n\n"
    "Доступ открыт через шлюз: @vnxMATRIX_Gateway_bot\n"
    "<i>Ожидание команды...</i>"
)
