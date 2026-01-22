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
MODEL_BASIC = "openai/gpt-4o-mini"
MODEL_PRO = "openai/gpt-4o"
MODEL_NEO = "anthropic/claude-3.5-sonnet"

DEFAULT_MODEL = MODEL_BASIC

LIMITS = {
    "START": 10,
    "PRO": 30,
    "NEO": 60
}

TARIFF_INFO = {
    "START": (
        "💠 <b>TARIFF: START</b>\n"
        "├ Модель: GPT-4o Mini\n"
        "├ Память: 10 сообщений\n"
        "└ Цена: 390₽ / мес"
    ),
    "PRO": (
        "⚡️ <b>TARIFF: PRO</b>\n"
        "├ Модель: GPT-4o (Flagship)\n"
        "├ Память: 30 сообщений\n"
        "└ Цена: 990₽ / мес"
    ),
    "NEO": (
        "🧬 <b>TARIFF: NEO (EVOLUTION)</b>\n"
        "├ Модель: Claude 3.5 Sonnet\n"
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
BTN_NEW_DIALOG = "♻️ Новый чат"
BTN_HISTORY = "💾 История чатов"
BTN_PROFILE = "👤 Мой профиль"
BTN_TARIFFS = "💳 Тарифные планы"
BTN_CHANGE_MODEL = "🧠 Сменить модель" # Кнопка осталась, но функционал новый
BTN_HELP = "🆘 Пподдержка"

# =========================================================
# 💬 СООБЩЕНИЯ
# =========================================================
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

MSG_SUPPORT = (
    "🆘 <b>ПОДДЕРЖКА АРХИТЕКТОРА</b>\n\n"
    "Если возникли сбои в Матрице или вопросы по оплате:\n"
    "👨‍💻 @vinixspb"
)
