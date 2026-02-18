import os
from dotenv import load_dotenv

load_dotenv()

# =========================================================
# 🔐 СИСТЕМНЫЕ НАСТРОЙКИ & ДОСТУПЫ
# =========================================================
BOT_TOKEN_ORACLE = os.getenv("BOT_TOKEN_ORACLE")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
ADMIN_CONTACT = "@vinixspb"

# --- GOOGLE SHEETS ---
# Алиас для обратной совместимости с services/sheets_manager.py
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID") or os.getenv("GOOGLE_SHEET_ID")
GOOGLE_SHEET_ID = SPREADSHEET_ID 
GOOGLE_CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS_JSON")

# --- ARCHIVE ---
# Конвертация в int обязательна для Telegram API
archive_id_str = os.getenv("ARCHIVE_CHANNEL_ID")
ARCHIVE_CHANNEL_ID = int(archive_id_str) if archive_id_str else 0

# --- PAYMENT INFO ---
PAYMENT_INFO = (
    "💳 <b>USDT (TRC20):</b>\n<code>T...........................</code>\n\n"
    "💳 <b>Карта (РФ):</b>\n<code>0000 0000 0000 0000</code>\n\n"
    "⚠️ После транзакции отправьте хэш или скриншот Архитектору: @vinixspb"
)

# =========================================================
# 🧠 AI ENGINE (MULTI-KEY ROUTING)
# =========================================================

# 1. Текстовые ключи (Разные кошельки для разных тарифов)
# Загружаем из .env
KEY_START = os.getenv("OPENROUTER_API_KEY_START")
KEY_PRO   = os.getenv("OPENROUTER_API_KEY_PRO")
KEY_NEO   = os.getenv("OPENROUTER_API_KEY_NEO")

# Для обратной совместимости, если старая переменная еще используется где-то
OPENROUTER_API_KEY = KEY_START or os.getenv("OPENROUTER_API_KEY")

# Базовый URL для текста (Всегда OpenRouter)
TEXT_BASE_URL = "https://openrouter.ai/api/v1"
AI_PROVIDER = "OpenRouter" # Маркер провайдера

# 2. Графический ключ (KIE.AI)
KIE_API_KEY = os.getenv("KIE_API_KEY") 

# --- ТЕКСТОВЫЕ МОДЕЛИ (LLM) ---
MODEL_BASIC = "google/gemini-2.0-flash:free"
MODEL_PRO = "microsoft/phi-3-medium-128k-instruct:free"
MODEL_NEO = "google/gemini-2.0-pro-exp-02-05:free"
MODEL_DEVSTRAL = "mistralai/mistral-7b-instruct:free"
MODEL_CHIMERA = "deepseek/deepseek-r1:free"
MODEL_LIQUID = "liquid/lfm-40b:free"

DEFAULT_MODEL = MODEL_BASIC

# Список для меню
MODELS_LIST = [
    ("Gemini 2.0 Flash (Free)", MODEL_BASIC),
    ("Phi-3 Medium (Free)", MODEL_PRO),
    ("Gemini 2.0 Pro (Free)", MODEL_NEO),
    ("Mistral 7B (Free)", MODEL_DEVSTRAL),
    ("DeepSeek R1 (Free)", MODEL_CHIMERA),
    ("Liquid LFM (Free)", MODEL_LIQUID)
]

# --- ПАРАМЕТРЫ ---
AI_TEMPERATURE = 0.7

# --- SYSTEM PROMPT ---
SYSTEM_PROMPT = (
    "Ты — vnxORACLE, цифровой разум системы vnxMATRIX. "
    "Твоя цель — помогать пользователям, отвечать на вопросы и писать код. "
    "Отвечай кратко, точно и в стиле киберпанк/профессионал. "
    "Ты вежлив, но не эмоционален. Ты — Система.\n\n"
    "ВАЖНО: Ты обладаешь модулем распознавания речи. "
    "Если запрос начинается с метки [Audio Input], знай, что это транскрипция голоса пользователя."
)

# =========================================================
# 🎨 МОДЕЛИ ГЕНЕРАЦИИ (ИЗОБРАЖЕНИЯ)
# =========================================================
# --- START TIER (Free / Cheap) ---
IMG_POLLINATIONS = "pollinations"          # Бесплатно
IMG_FLUX_SCHNELL = "black-forest-labs/flux-1-schnell"
IMG_SDXL = "stabilityai/stable-diffusion-xl-base-1.0"
IMG_PLAYGROUND = "playgroundai/playground-v2.5-1024px-aesthetic"

# --- PRO/NEO TIER (Premium) ---
IMG_FLUX_DEV = "black-forest-labs/flux-1-dev"
IMG_RECRAFT = "recraft-ai/recraft-v3"
IMG_DALLE3 = "dall-e-3"
IMG_SD3_LARGE = "stabilityai/stable-diffusion-3.5-large"

DEFAULT_IMG_MODEL = IMG_FLUX_SCHNELL

# =========================================================
# 🎙 ГОЛОСОВЫЕ ТЕХНОЛОГИИ
# =========================================================
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") # Для Whisper STT

VOICE_ADAM = "pNInz6obpgDQGcFmaJgB"
VOICE_RACHEL = "21m00Tcm4TlvDq8ikWAM"
VOICE_FIN = "D38z5RcWu1voky8WSVqt"
VOICE_MIMI = "zrHiDhphv9ZnVXBqCLjz"
DEFAULT_VOICE = VOICE_ADAM

# =========================================================
# 💰 ЭКОНОМИКА И ТАРИФЫ
# =========================================================
LIMITS = {"START": 10, "PRO": 30, "NEO": 60}

TARIFF_INFO = {
    "START": (
        "💠 <b>TARIFF: START</b>\n<i>(Базовый доступ)</i>\n"
        "├ LLM: GPT-4o Mini\n├ Память: 10 msg\n├ Art: Basic (4 модели)\n└ Цена: 190₽ / мес"
    ),
    "PRO": (
        "⚡️ <b>TARIFF: PRO</b>\n<i>(Профессиональный)</i>\n"
        "├ LLM: GPT-4o (Flagship)\n├ Память: 30 msg\n├ Vision: ✅\n├ Art: Premium (8 моделей)\n└ Цена: 590₽ / мес"
    ),
    "NEO": (
        "🧬 <b>TARIFF: NEO (EVOLUTION)</b>\n<i>(Максимальный)</i>\n"
        "├ LLM: Claude 3.5 Sonnet\n├ Память: 60 msg\n├ Vision: ✅\n├ Video: ✅ (Beta)\n└ Цена: 990₽ / мес"
    )
}

# =========================================================
# 🎹 ИНТЕРФЕЙС (UI)
# =========================================================
# Верхний ряд (Caps Lock)
BTN_NEW_DIALOG = "♻️ НОВЫЙ ЧАТ"
BTN_HISTORY = "💾 ИСТОРИЯ ЧАТОВ"

# Нижний ряд (Capitalize)
BTN_CHANGE_MODEL = "🧠 Выбор модели"
BTN_PROFILE = "👤 Мой профиль"

# Системные (Для проверок)
BTN_TARIFFS = "💳 Тарифные планы"
BTN_HELP = "🆘 Поддержка"

# =========================================================
# 💬 СООБЩЕНИЯ
# =========================================================
MSG_WELCOME = (
    "👁 <b>vnxORACLE SYSTEM: ONLINE</b>\n\n"
    "Добро пожаловать. Я — интерфейс чистого знания.\n"
    "Готов к обработке данных: Текст, Голос, Изображения, Код.\n"
)
MSG_NO_SUB = "⛔️ <b>ДОСТУП ОГРАНИЧЕН</b>\n\nВаш нейро-линк не активен.\nДля подключения выберите тариф:"
MSG_SUPPORT = "🆘 <b>ПОДДЕРЖКА АРХИТЕКТОРА</b>\n\nСбои в Матрице? Связь: @vinixspb"
