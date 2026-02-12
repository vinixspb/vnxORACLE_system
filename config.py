import os
from dotenv import load_dotenv

load_dotenv()

# =========================================================
# 🔐 СИСТЕМНЫЕ НАСТРОЙКИ & ДОСТУПЫ
# =========================================================
BOT_TOKEN_ORACLE = os.getenv("BOT_TOKEN_ORACLE")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
ADMIN_CONTACT = "@vinixspb"

# --- GOOGLE SHEETS (FIXED) ---
# Поддержка старого и нового именования переменной в .env для совместимости
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID") or os.getenv("GOOGLE_SHEET_ID")
GOOGLE_SHEET_ID = SPREADSHEET_ID # Алиас для services/sheets_manager.py
GOOGLE_CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS_JSON")

# --- ARCHIVE ---
# Конвертация в число для Telegram API
archive_id_str = os.getenv("ARCHIVE_CHANNEL_ID")
ARCHIVE_CHANNEL_ID = int(archive_id_str) if archive_id_str else 0

# --- PAYMENT INFO ---
PAYMENT_INFO = (
    "💳 <b>USDT (TRC20):</b>\n<code>T...........................</code>\n\n"
    "💳 <b>Карта (РФ):</b>\n<code>0000 0000 0000 0000</code>\n\n"
    "⚠️ После транзакции отправьте хэш или скриншот Архитектору: @vinixspb"
)

# =========================================================
# 🧠 AI ENGINE (HYBRID CORE)
# =========================================================

# 1. Получаем ключи из .env
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
KIE_API_KEY = os.getenv("KIE_API_KEY") # Твой новый ключ

# 2. Логика автоматического выбора провайдера
# Приоритет: KIE (Новый) -> OpenRouter (Старый/Резерв)

if KIE_API_KEY:
    # --- НАСТРОЙКИ НОВОГО ПРОВАЙДЕРА ---
    AI_PROVIDER = "KIE"
    AI_API_KEY = KIE_API_KEY
    # ⚠️ ВАЖНО: Убедись, что адрес API верный. Обычно это v1.
    AI_BASE_URL = "https://api.kie.ai/v1" 
    print(f"🚀 Config: Active Provider -> KIE.AI ({AI_BASE_URL})")

elif OPENROUTER_API_KEY:
    # --- НАСТРОЙКИ РЕЗЕРВА ---
    AI_PROVIDER = "OpenRouter"
    AI_API_KEY = OPENROUTER_API_KEY
    AI_BASE_URL = "https://openrouter.ai/api/v1"
    print("🔄 Config: Active Provider -> OpenRouter (Fallback)")

else:
    # --- АВАРИЙНЫЙ РЕЖИМ ---
    AI_PROVIDER = "NONE"
    AI_API_KEY = None
    AI_BASE_URL = None
    print("❌ Config: CRITICAL - No AI Keys found!")

# --- МОДЕЛИ (NEURAL MAP) ---
# Если KIE.AI использует стандартные имена OpenAI (gpt-4o), оставляем как есть.
# Если у них свои названия (например 'kie-gpt-4'), измени значения справа.
MODEL_BASIC = "gpt-4o-mini"
MODEL_PRO = "gpt-4o"
MODEL_NEO = "claude-3-5-sonnet-20240620"
MODEL_DEVSTRAL = "mistral-large-latest"
MODEL_CHIMERA = "llama-3.1-70b-instruct"
MODEL_LIQUID = "liquid-lfm-2.5"

DEFAULT_MODEL = MODEL_BASIC

# --- ПАРАМЕТРЫ ГЕНЕРАЦИИ ---
AI_TEMPERATURE = 0.7

# --- SYSTEM PROMPT ---
SYSTEM_PROMPT = (
    "Ты — vnxORACLE, цифровой разум системы vnxMATRIX. "
    "Твоя цель — помогать пользователям, отвечать на вопросы и писать код. "
    "Отвечай кратко, точно и в стиле киберпанк/профессионал. "
    "Ты вежлив, но не эмоционален. Ты — Система.\n\n"
    "ВАЖНО: Ты обладаешь модулем распознавания речи. "
    "Если запрос начинается с метки [Audio Input], знай, что это транскрипция голоса пользователя. "
    "Отвечай на суть вопроса, игнорируя факт того, что это было аудио, если пользователь сам об этом не спросит."
)

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
    "START": ("💠 <b>TARIFF: START</b>\n<i>(Базовый доступ)</i>\n├ Модель: GPT-4o Mini\n├ Память: 10 сообщений\n└ Цена: 190₽ / мес"),
    "PRO": ("⚡️ <b>TARIFF: PRO</b>\n<i>(Профессиональный)</i>\n├ Модель: GPT-4o (Flagship)\n├ Память: 30 сообщений\n├ Vision: ✅\n└ Цена: 590₽ / мес"),
    "NEO": ("🧬 <b>TARIFF: NEO (EVOLUTION)</b>\n<i>(Максимальный)</i>\n├ Модель: Claude 3.5 Sonnet\n├ Память: 60 сообщений\n├ Vision: ✅\n├ Video: ✅ (Beta)\n└ Цена: 990₽ / мес")
}

# =========================================================
# 🎹 ИНТЕРФЕЙС (UI)
# =========================================================
# Верхний ряд (Капслок - важные действия)
BTN_NEW_DIALOG = "♻️ НОВЫЙ ЧАТ"
BTN_HISTORY = "💾 ИСТОРИЯ ЧАТОВ"

# Нижний ряд (Обычный текст - настройки)
BTN_CHANGE_MODEL = "🧠 Выбор модели"
BTN_PROFILE = "👤 Мой профиль"

# Системные кнопки (для внутренней логики)
BTN_TARIFFS = "💳 Тарифные планы"
BTN_HELP = "🆘 Поддержка"

# =========================================================
# 💬 СООБЩЕНИЯ
# =========================================================
MSG_WELCOME = (
    "👁 <b>vnxORACLE SYSTEM: ONLINE</b>\n\n"
    "Добро пожаловать. Я — интерфейс чистого знания.\n"
    "Готов к обработке данных: Текст, Голос, Изображения, Код.\n\n"
    "👇 <b>Выберите модуль для начала работы:</b>"
)

MSG_NO_SUB = (
    "⛔️ <b>ДОСТУП ОГРАНИЧЕН</b>\n\n"
    "Ваш нейро-линк не активен или исчерпан лимит.\n"
    "Для подключения к Системе выберите уровень доступа:"
)

MSG_SUPPORT = (
    "🆘 <b>ПОДДЕРЖКА АРХИТЕКТОРА</b>\n\n"
    "Сбои в Матрице? Вопросы по интеграции?\n"
    "Связь напрямую: @vinixspb"
)
