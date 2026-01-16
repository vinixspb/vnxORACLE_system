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

# Реквизиты
PAYMENT_INFO = "USDT (TRC20): T..........................." 
ADMIN_CONTACT = "@vinixspb"

# =========================================================
# ⚙️ МОЗГ И ЛИМИТЫ
# =========================================================
MODEL_BASIC = "openai/gpt-3.5-turbo"
MODEL_PRO = "openai/gpt-4o-mini"
MODEL_NEO = "anthropic/claude-3.5-sonnet"

DEFAULT_MODEL = MODEL_BASIC

LIMITS = {
    "START": 10,
    "PRO": 30,
    "NEO": 60
}

# Исправлено TARIF -> TARIFF
TARIFF_INFO = {
    "START": (
        "💠 <b>TARIFF: START</b>\n"
        "├ Модель: GPT-3.5 Turbo\n"
        "├ Память: 10 сообщений\n"
        "└ Цена: 390₽ / мес"
    ),
    "PRO": (
        "⚡️ <b>TARIFF: PRO</b>\n"
        "├ Модель: GPT-4o Mini (Speed)\n"
        "├ Память: 30 сообщений\n"
        "└ Цена: 990₽ / мес"
    ),
    "NEO": (
        "🧬 <b>TARIFF: NEO (EVOLUTION)</b>\n"
        "├ Модель: Claude 3.5 Sonnet / GPT-4o\n"
        "├ Память: 60 сообщений\n"
        "├ Coding: MAX Level\n"
        "└ Цена: 1490₽ / мес"
    )
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
BTN_NEW_DIALOG = "♻️ НОВЫЙ ЧАТ"
BTN_HISTORY = "💾 ИСТОРИЯ ЧАТОВ"
BTN_PROFILE = "👤 МОЙ ПРОФИЛЬ"
BTN_TARIFFS = "💳 ТАРИФНЫЕ ПЛАНЫ"
BTN_CHANGE_MODEL = "🧠 СМЕНИТЬ МОДЕЛЬ"
BTN_HELP = "🆘 ПОДДЕРЖКА"

# =========================================================
# 💬 СООБЩЕНИЯ
# =========================================================
# ВОЗВРАЩЕНО: Полный текст с рекламой шлюза
MSG_WELCOME = (
    "👁 <b>vnxORACLE SYSTEM</b>\n\n"
    "Добро пожаловать в систему.\n"
    "Я — интерфейс чистого знания.\n\n"
    "Доступ открыт через шлюз: @vnxMATRIX_Gateway_bot\n"
    "<i>Ожидание команды...</i>"
)

MSG_NO_SUB = (
    "⛔️ <b>ДОСТУП ОГРАНИЧЕН</b>\n\n"
    "Ваш нейро-линк не активен.\n"
    "Для подключения к Системе выберите уровень доступа:"
)

# ВОЗВРАЩЕНО: Полный текст поддержки
MSG_SUPPORT = (
    "🆘 <b>ПОДДЕРЖКА АРХИТЕКТОРА</b>\n\n"
    "Если возникли сбои в Матрице или вопросы по оплате:\n"
    "👨‍💻 @vinixspb"
)
