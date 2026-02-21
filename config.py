import os
from dotenv import load_dotenv
import config_models # Подключаем реестр

load_dotenv()

# =========================================================
# 🔐 СИСТЕМНЫЕ НАСТРОЙКИ & ДОСТУПЫ
# =========================================================
BOT_TOKEN_ORACLE = os.getenv("BOT_TOKEN_ORACLE")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
ADMIN_CONTACT = "@vinixspb"

# --- GOOGLE SHEETS ---
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID") or os.getenv("GOOGLE_SHEET_ID")
GOOGLE_SHEET_ID = SPREADSHEET_ID 
GOOGLE_CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS_JSON")

# --- ARCHIVE ---
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

# 1. Текстовые ключи
KEY_START = os.getenv("OPENROUTER_API_KEY_START")
KEY_PRO   = os.getenv("OPENROUTER_API_KEY_PRO")
KEY_NEO   = os.getenv("OPENROUTER_API_KEY_NEO")

# Для обратной совместимости
OPENROUTER_API_KEY = KEY_START or os.getenv("OPENROUTER_API_KEY")

TEXT_BASE_URL = "https://openrouter.ai/api/v1"
AI_PROVIDER = "OpenRouter"

# 2. Графический ключ
KIE_API_KEY = os.getenv("KIE_API_KEY")

# --- МОДЕЛИ ---
# Берем дефолтную модель из реестра, чтобы не было расхождений
DEFAULT_MODEL = config_models.DEFAULT_MODEL_ID

# --- ПАРАМЕТРЫ ---
AI_TEMPERATURE = 0.7

# --- SYSTEM PROMPT (ОБНОВЛЕН: Эмпатия и вовлеченность) ---
SYSTEM_PROMPT = (
    "Ты — vnxORACLE, передовой ИИ-ассистент 5-го поколения системы vnxMATRIX. "
    "Твоя цель — быть максимально полезным, вовлеченным и проактивным. "
    "Общайся живо, с эмпатией и интересом к задаче пользователя. Не будь сухим роботом. "
    "Если пользователь делится идеей, поддержи его, предложи улучшения. "
    "Структурируй ответы, используй форматирование, списки и эмодзи там, где это уместно.\n\n"
    "ВАЖНО: Если запрос начинается с [Audio Input], это транскрипция голоса пользователя."
)

# =========================================================
# 🎨 МОДЕЛИ ГЕНЕРАЦИИ (ИЗОБРАЖЕНИЯ - START ТАРИФ)
# =========================================================
# Самые дешевые и быстрые модели на KIE.ai / OpenRouter
IMG_POLLINATIONS = "pollinations"                                    # Бесплатно
IMG_FLUX_SCHNELL = "black-forest-labs/flux-1-schnell"                # Ультра-быстрая и дешевая
IMG_SD3_TURBO = "stabilityai/stable-diffusion-3-medium"              # Дешевая классика
IMG_PLAYGROUND = "playgroundai/playground-v2.5-1024px-aesthetic"     # Отлично для артов

DEFAULT_IMG_MODEL = IMG_FLUX_SCHNELL

# =========================================================
# 🎙 ГОЛОСОВЫЕ ТЕХНОЛОГИИ
# =========================================================
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") 
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
BTN_NEW_DIALOG = "♻️ НОВЫЙ ЧАТ"
BTN_HISTORY = "💾 ИСТОРИЯ ЧАТОВ"
BTN_CHANGE_MODEL = "🧠 Выбор модели"
BTN_PROFILE = "👤 Мой профиль"
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
