import os
from dotenv import load_dotenv

load_dotenv()

# =========================================================
# 🔐 СИСТЕМНЫЕ НАСТРОЙКИ
# =========================================================
BOT_TOKEN_ORACLE = os.getenv("BOT_TOKEN_ORACLE")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY") 
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") 
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID") 
GOOGLE_CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS_JSON")
archive_id_str = os.getenv("ARCHIVE_CHANNEL_ID")
ARCHIVE_CHANNEL_ID = int(archive_id_str) if archive_id_str else 0
PAYMENT_INFO = "USDT (TRC20): T..........................." 
ADMIN_CONTACT = "@vinixspb"

# =========================================================
# ⚙️ МОЗГ И МОДЕЛИ
# =========================================================
MODEL_BASIC = "openai/gpt-4o-mini"
MODEL_PRO = "openai/gpt-4o"
MODEL_NEO = "anthropic/claude-3.5-sonnet"
MODEL_DEVSTRAL = "mistralai/devstral-2512:free"
MODEL_CHIMERA = "tngtech/deepseek-r1t2-chimera:free"
MODEL_LIQUID = "liquid/lfm-2.5-1.2b-instruct:free"

DEFAULT_MODEL = MODEL_BASIC

LIMITS = {"START": 10, "PRO": 30, "NEO": 60}

# 👇 НАСТРОЙКИ ГОЛОСА (ELEVENLABS)
VOICE_ADAM = "pNInz6obpgDQGcFmaJgB"    # Глубокий мужской (Deep)
VOICE_RACHEL = "21m00Tcm4TlvDq8ikWAM"  # Женский (American, Calm)
VOICE_FIN = "D38z5RcWu1voky8WSVqt"     # Энергичный мужской (Irish)
VOICE_MIMI = "zrHiDhphv9ZnVXBqCLjz"    # Детский / Милый (Australian)

DEFAULT_VOICE = VOICE_ADAM

# --- ОПИСАНИЯ ТАРИФОВ ---
TARIFF_INFO = {
    "START": ("💠 <b>TARIFF: START</b>\n<i>(Первые 2 месяца — БЕСПЛАТНО)</i>\n├ Модель: GPT-4o Mini\n├ Память: 10 сообщений\n├ Лимит: 100,000 токенов/мес\n└ Цена: 190₽ / мес"),
    "PRO": ("⚡️ <b>TARIFF: PRO</b>\n├ Модель: GPT-4o (Flagship)\n├ Память: 30 сообщений\n├ Лимит: 500,000 токенов/мес\n└ Цена: 590₽ / мес"),
    "NEO": ("🧬 <b>TARIFF: NEO (EVOLUTION)</b>\n├ Модель: Claude 3.5 Sonnet\n├ Память: 60 сообщений\n├ Coding: MAX Level\n├ Лимит: 1,000,000 токенов/мес\n└ Цена: 990₽ / мес")
}

SYSTEM_PROMPT = (
    "Ты — vnxORACLE, цифровой разум системы vnxMATRIX. "
    "Твоя цель — помогать пользователям, отвечать на вопросы и писать код. "
    "Отвечай кратко, точно и в стиле киберпанк/профессионал. "
    "Ты вежлив, но не эмоционален. Ты — Система.\n\n"
    "ВАЖНО: Ты обладаешь модулем распознавания речи. "
    "Если запрос начинается с метки [Audio Input], знай, что это транскрипция голоса пользователя. "
    "Отвечай на суть вопроса, игнорируя факт того, что это было аудио."
)

AI_TEMPERATURE = 0.7

# =========================================================
# 🎹 КНОПКИ (UI)
# =========================================================
BTN_NEW_DIALOG = "♻️ НОВЫЙ ЧАТ"
BTN_HISTORY = "💾 ИСТОРИЯ ЧАТОВ"
BTN_PROFILE = "👤 Мой профиль"
BTN_TARIFFS = "💳 Тарифные планы"
BTN_CHANGE_MODEL = "🧠 Сменить модель"
BTN_HELP = "🆘 Поддержка"

# =========================================================
# 💬 СООБЩЕНИЯ
# =========================================================
MSG_WELCOME = "👁 <b>vnxORACLE SYSTEM</b>\n\nДобро пожаловать в систему.\nЯ — интерфейс чистого знания.\n\nДоступ открыт через шлюз: @vnxMATRIX_Gateway_bot\n<i>Ожидание команды...</i>"
MSG_NO_SUB = "⛔️ <b>ДОСТУП ОГРАНИЧЕН</b>\n\nВаш нейро-линк не активен.\nДля подключения к Системе выберите уровень доступа:"
MSG_SUPPORT = "🆘 <b>ПОДДЕРЖКА АРХИТЕКТОРА</b>\n\nЕсли возникли сбои в Матрице или вопросы по оплате:\n👨‍💻 @vinixspb"
