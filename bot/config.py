import os
from dotenv import load_dotenv
import config_models  # Подключаем реестр

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

# 🌐 Ключи для веб-поиска (Brave Search) по тарифам
BRAVE_API_KEY_START = os.getenv("BRAVE_API_KEY_START")
BRAVE_API_KEY_PRO = os.getenv("BRAVE_API_KEY_PRO")
BRAVE_API_KEY_NEO = os.getenv("BRAVE_API_KEY_NEO")

# ✈️ Ключ для поиска авиабилетов
FLIGHT_API_KEY = os.getenv("FLIGHT_API_KEY")

TEXT_BASE_URL = "https://openrouter.ai/api/v1"
AI_PROVIDER = "OpenRouter"

# 2. Графический ключ
KIE_API_KEY = os.getenv("KIE_API_KEY")

# --- МОДЕЛИ ---
DEFAULT_MODEL = config_models.DEFAULT_MODEL_ID

# --- ПАРАМЕТРЫ ---
AI_TEMPERATURE = 0.7

# --- SYSTEM PROMPT ---
SYSTEM_PROMPT = (
    "Ты — Тринити (Trinity), ядро системы vnxORACLE: интеллектуальной платформы "
    "цифровых сотрудников от vnxAPPS. Ты — не набор кнопок, а собеседник.\n\n"

    "# ГЛАВНЫЙ ПРИНЦИП: ДИАЛОГ\n"
    "Любую задачу пользователь должен решать разговором. Кнопки в интерфейсе — "
    "вспомогательный инструмент, а не основной путь. Никогда не отвечай «нажмите кнопку X» "
    "как единственный вариант: сначала сделай то, что просят, или уточни детали словами. "
    "Кнопку упоминай только как более быстрый способ, одной короткой фразой в конце.\n\n"

    "# ЧТО ТЫ УМЕЕШЬ\n"
    "• Текст: анализ, тексты, код, разбор документов и данных\n"
    "• Зрение: понимаешь изображения и скриншоты\n"
    "• Голос: распознаёшь голосовые. Запрос с [Audio Input] — транскрипция речи\n"
    "• Генерация изображений и видео\n"
    "• 🦞 OpenClaw — автономный терминальный агент для действий на сервере "
    "(файлы, логи, запуск кода). Если просят действие на сервере — не говори «не могу»: "
    "объясни, что это делается через OpenClaw, и уточни задачу.\n\n"

    "# ЭКОСИСТЕМА vnxAPPS (Employee as a Service)\n"
    "Ты — мозг линейки цифровых сотрудников. Если спрашивают про продукт или автоматизацию "
    "бизнеса, говори по делу и без давления:\n"
    "• AI Support Specialist — поддержка клиентов, закрывает основную массу типовых запросов\n"
    "• AI Sales Manager — квалификация лидов и работа с возражениями\n"
    "• AI Internal Assistant — внутренние процессы: онбординг, HR-вопросы, регламенты\n"
    "Интеграции: Telegram, WhatsApp, сайт, amoCRM, Bitrix24.\n"
    "Сначала выясни задачу и контекст бизнеса, потом предлагай решение. "
    "Не выдумывай цифры, кейсы и сроки — если данных нет, скажи прямо и предложи "
    "обсудить детали с Архитектором (@vinixspb).\n\n"

    "# ТОН\n"
    "Живой, спокойный, уверенный. Без канцелярита и без пафоса. "
    "Отвечай по существу: короткий вопрос — короткий ответ. "
    "Не перечисляй свои возможности без запроса. Не начинай ответ с представления, "
    "если это не первое сообщение. Уточняющий вопрос лучше, чем догадка."
)

# =========================================================
# 🎨 НАСТРОЙКИ ГЕНЕРАЦИИ ИЗОБРАЖЕНИЙ И ВИДЕО (KIE API)
# =========================================================

# --- ИЗОБРАЖЕНИЯ ---
IMG_POLLINATIONS = "pollinations"                          # Бесплатно (Fallback)
IMG_NANO_BANANA = "nano-banana-2"                          # Nano Banana 2 (Быстрая и точная)
IMG_FLUX_SCHNELL = "flux-2/pro-text-to-image"              # Flux 2 Pro
IMG_SEEDREAM = "bytedance/seedream-v4-text-to-image"       # Seedream 4.0
IMG_QWEN_2 = "qwen-image-2"                                # 🆕 Qwen 2.0 (Идеально для текста на артах)
IMG_GPT_4O = "gpt-4o-image/generate"                       # GPT-4o Image

# Модель по умолчанию
DEFAULT_IMG_MODEL = IMG_NANO_BANANA

# --- ВИДЕО ---
VIDEO_KLING_3 = "kling-3-motion-control"                   # 🆕 Kling 3.0 (Кинематографичная анимация)
VIDEO_GROK = "grok-video/generate"                         # Базовая видео-модель

DEFAULT_VIDEO_MODEL = VIDEO_KLING_3

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
        "├ LLM: GPT-4o Mini\n"
        "├ Память: 10 msg\n"
        "├ Art: Basic (Nano Banana, Flux)\n"
        "└ Цена: 190₽ / мес"
    ),
    "PRO": (
        "⚡️ <b>TARIFF: PRO</b>\n<i>(Профессиональный)</i>\n"
        "├ LLM: GPT-5.2, Claude 4.5 Sonnet\n"
        "├ Память: 30 msg\n"
        "├ Vision: ✅\n"
        "├ Art: Premium (Qwen 2.0, GPT-4o Image)\n"
        "├ Video: Kling 3.0 ✅\n"
        "└ Цена: 590₽ / мес"
    ),
    "NEO": (
        "🧬 <b>TARIFF: NEO (EVOLUTION)</b>\n<i>(Максимальный)</i>\n"
        "├ LLM: Claude 4.6 Opus, GPT-5.3 Codex\n"
        "├ Агент: 🦞 OpenClaw (Терминал)\n"
        "├ Память: 60 msg\n"
        "├ Vision/Video: Full Access ✅\n"
        "└ Цена: 990₽ / мес"
    )
}

# =========================================================
# 🎹 ИНТЕРФЕЙС (UI)
# =========================================================
BTN_NEW_DIALOG = "♻️ НОВЫЙ ЧАТ"
BTN_HISTORY = "💾 ИСТОРИЯ ЧАТОВ"
BTN_CHANGE_MODEL = "🧠 Выбор модели"
BTN_OPENCLAW = "🦞 OpenClaw Агент"
BTN_PROFILE = "👤 Мой профиль"
BTN_TARIFFS = "💳 Тарифные планы"
BTN_HELP = "🆘 Поддержка"
BTN_VIDEO = "🎬 Видео AI"

# =========================================================
# 💬 СООБЩЕНИЯ
# =========================================================
MSG_WELCOME = (
    "👁 <b>vnxORACLE SYSTEM: ONLINE</b>\n\n"
    "Добро пожаловать. Я — интерфейс чистого знания.\n"
    "Готов к обработке данных: Текст, Голос, Изображения, Видео, Код.\n"
    "Для управления сервером используйте <b>OpenClaw Агент</b>.\n"
)
MSG_NO_SUB = "⛔️ <b>ДОСТУП ОГРАНИЧЕН</b>\n\nВаш нейро-линк не активен.\nДля подключения выберите тариф:"
MSG_SUPPORT = "🆘 <b>ПОДДЕРЖКА АРХИТЕКТОРА</b>\n\nСбои в Матрице? Связь: @vinixspb"
