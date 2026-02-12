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
# Поддержка старого и нового именования переменной в .env
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID") or os.getenv("GOOGLE_SHEET_ID")
GOOGLE_CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS_JSON")
GOOGLE_SHEET_ID = SPREADSHEET_ID

# --- ARCHIVE (FIXED TYPE) ---
# Критическое исправление: конвертация в int, иначе телеграм не примет ID
archive_id_str = os.getenv("ARCHIVE_CHANNEL_ID")
ARCHIVE_CHANNEL_ID = int(archive_id_str) if archive_id_str else 0

# --- PAYMENT INFO (CYBERPUNK STYLE) ---
PAYMENT_INFO = (
    "💳 <b>USDT (TRC20):</b>\n<code>T...........................</code>\n\n"
    "💳 <b>Карта (РФ):</b>\n<code>0000 0000 0000 0000</code>\n\n"
    "⚠️ После транзакции отправьте хэш или скриншот Архитектору: @vinixspb"
)

# =========================================================
# 🧠 AI ENGINE (MULTI-PROVIDER SETUP)
# =========================================================

# 1. РЕЗЕРВ (OPENROUTER) - Оставляем для совместимости
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# 2. АКТИВНЫЙ ПРОВАЙДЕР (KIA.AI)
KIA_API_KEY = os.getenv("KIA_API_KEY") # Добавь этот ключ в .env!

# ЛОГИКА ВЫБОРА ПРОВАЙДЕРА
# Сейчас активен KIA. Чтобы вернуть OpenRouter, закомментируй блок KIA и раскомментируй OpenRouter.
AI_PROVIDER = "KIA" 

if AI_PROVIDER == "KIA":
    AI_API_KEY = KIA_API_KEY
    AI_BASE_URL = "https://api.kia.ai/v1" 
else:
    AI_API_KEY = OPENROUTER_API_KEY
    AI_BASE_URL = "https://openrouter.ai/api/v1"

# --- МОДЕЛИ (ID моделей для KIA.AI / OPENAI COMPATIBLE) ---
# Убедись, что эти имена поддерживаются в KIA. Если нет - замени на их аналоги.
MODEL_BASIC = "gpt-4o-mini"
MODEL_PRO = "gpt-4o"
MODEL_NEO = "claude-3-5-sonnet-20240620"
MODEL_DEVSTRAL = "mistral-large-latest"      # Проверь доступность в KIA
MODEL_CHIMERA = "llama-3.1-70b-instruct"     # Проверь доступность в KIA
MODEL_LIQUID = "liquid-lfm-2.5"              # Проверь доступность в KIA

DEFAULT_MODEL = MODEL_BASIC

# --- ПАРАМЕТРЫ ГЕНЕРАЦИИ ---
AI_TEMPERATURE = 0.7

# --- SYSTEM PROMPTS (RESTORED ATMOSPHERE) ---
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
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") # Для Whisper STT и Fallback TTS

# ID голосов (Возвращены оригинальные значения из твоего старого файла)
VOICE_ADAM = "pNInz6obpgDQGcFmaJgB"    # Глубокий мужской (Deep)
VOICE_RACHEL = "21m00Tcm4TlvDq8ikWAM"  # Женский (American, Calm)
VOICE_FIN = "D38z5RcWu1voky8WSVqt"     # Энергичный мужской (Irish) - (Исправлен ID на Vqt)
VOICE_MIMI = "zrHiDhphv9ZnVXBqCLjz"    # Детский / Милый (Australian) - (Исправлен ID на z)

DEFAULT_VOICE = VOICE_ADAM

# =========================================================
# 💰 ЭКОНОМИКА И ТАРИФЫ
# =========================================================
LIMITS = {"START": 10, "PRO": 30, "NEO": 60}

# Возвращаем красивое описание тарифов для меню
TARIFF_INFO = {
    "START": (
        "💠 <b>TARIFF: START</b>\n"
        "<i>(Базовый доступ)</i>\n"
        "├ Модель: GPT-4o Mini\n"
        "├ Память: 10 сообщений\n"
        "├ Vision: ❌\n"
        "└ Цена: 190₽ / мес"
    ),
    "PRO": (
        "⚡️ <b>TARIFF: PRO</b>\n"
        "<i>(Профессиональный)</i>\n"
        "├ Модель: GPT-4o (Flagship)\n"
        "├ Память: 30 сообщений\n"
        "├ Vision: ✅ (Анализ фото)\n"
        "└ Цена: 590₽ / мес"
    ),
    "NEO": (
        "🧬 <b>TARIFF: NEO (EVOLUTION)</b>\n"
        "<i>(Максимальный)</i>\n"
        "├ Модель: Claude 3.5 Sonnet\n"
        "├ Память: 60 сообщений\n"
        "├ Vision: ✅ (Анализ фото)\n"
        "├ Video: ✅ (Beta)\n"
        "└ Цена: 990₽ / мес"
    )
}

# =========================================================
# 🎹 ИНТЕРФЕЙС (UI)
# =========================================================
# Главное меню (4 кнопки)
BTN_NEW_DIALOG = "♻️ НОВЫЙ ЧАТ"
BTN_HISTORY = "💾 ИСТОРИЯ ЧАТОВ"
BTN_CHANGE_MODEL = "🧠 Выбор Ai модели"
BTN_PROFILE = "👤 Мой профиль"


# Системные кнопки (используются в коде для проверок)
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
