from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import config
from loader import db

# --- ГЛАВНОЕ МЕНЮ (REPLY) ---
def get_main_keyboard():
    keyboard = [
        [KeyboardButton(config.BTN_NEW_DIALOG), KeyboardButton(config.BTN_HISTORY)],
        [KeyboardButton(config.BTN_PROFILE), KeyboardButton(config.BTN_TARIFFS)],
        [KeyboardButton(config.BTN_CHANGE_MODEL), KeyboardButton(config.BTN_HELP)]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# --- МЕНЮ ТАРИФОВ (INLINE) ---
def get_subscription_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("💳 Подключить START", callback_data="buy_START"),
            InlineKeyboardButton("💳 Подключить PRO", callback_data="buy_PRO")
        ],
        [InlineKeyboardButton("💳 Подключить NEO", callback_data="buy_NEO")],
        [InlineKeyboardButton("👨‍💻 Связь с Архитектором", url="https://t.me/vinixspb")]
    ]
    return InlineKeyboardMarkup(keyboard)

# --- МЕНЮ ВОЗМОЖНОСТЕЙ (ХАБ) ---
def get_features_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("🧠 Выбор Нейросети", callback_data="feature_text"),
            InlineKeyboardButton("🎤 Аудио ИИ", callback_data="feature_audio")
        ],
        [
            InlineKeyboardButton("👁 Vision (Зрение)", callback_data="feature_vision"),
            InlineKeyboardButton("🎬 Видео ИИ (Beta)", callback_data="feature_video")
        ],
        [
            InlineKeyboardButton("🎨 Дизайн ИИ", callback_data="feature_design"),
            InlineKeyboardButton("🗄 Хранитель (Архив)", callback_data="feature_keeper")
        ],
        [
            InlineKeyboardButton("❓ Помощь", callback_data="feature_help"),
            InlineKeyboardButton("📚 База знаний", callback_data="feature_knowledge")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

# --- ВЫБОР ГОЛОСА (TTS) ---
def get_voice_selection_keyboard(current_voice=None):
    voices = [
        ("👨‍💼 Adam (Deep Male)", config.VOICE_ADAM),
        ("👩‍💼 Rachel (Calm Female)", config.VOICE_RACHEL),
        ("🧔 Fin (Energetic)", config.VOICE_FIN),
        ("👧 Mimi (Cute)", config.VOICE_MIMI)
    ]
    keyboard = []
    for name, v_id in voices:
        prefix = "✅ " if v_id == current_voice else ""
        keyboard.append([InlineKeyboardButton(f"{prefix}{name}", callback_data=f"setvoice_{v_id}")])
    
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="feature_audio")])
    return InlineKeyboardMarkup(keyboard)

# Остальные функции (get_audio_keyboard, get_models_keyboard, get_history_keyboard) остаются без изменений
