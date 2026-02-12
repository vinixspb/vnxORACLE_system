from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import config

# --- ГЛАВНОЕ МЕНЮ (REPLY - 4 КНОПКИ) ---
def get_main_keyboard():
    keyboard = [
        [KeyboardButton(config.BTN_NEW_DIALOG), KeyboardButton(config.BTN_CHANGE_MODEL)],
        [KeyboardButton(config.BTN_HISTORY), KeyboardButton(config.BTN_PROFILE)]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# --- МЕНЮ ПРОФИЛЯ ---
def get_profile_keyboard():
    keyboard = [
        [InlineKeyboardButton("💳 Тарифные планы", callback_data="profile_tariffs")],
        [InlineKeyboardButton("👨‍💻 Техподдержка", callback_data="profile_support")],
        [InlineKeyboardButton("🔙 Назад в меню", callback_data="back_to_features")]
    ]
    return InlineKeyboardMarkup(keyboard)

# --- МЕНЮ ТАРИФОВ ---
def get_subscription_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("💳 Подключить START", callback_data="buy_START"),
            InlineKeyboardButton("💳 Подключить PRO", callback_data="buy_PRO")
        ],
        [InlineKeyboardButton("💳 Подключить NEO", callback_data="buy_NEO")],
        [InlineKeyboardButton("👨‍💻 Связь с Архитектором", url="https://t.me/vinixspb")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back_to_profile")]
    ]
    return InlineKeyboardMarkup(keyboard)

# --- 🧩 МЕНЮ ВОЗМОЖНОСТЕЙ (ГЛАВНЫЙ ХАБ) ---
def get_features_keyboard():
    keyboard = [
        # Ряд 1: Основное общение и Аудио
        [
            InlineKeyboardButton("💬 Общение AI", callback_data="feature_text"),
            InlineKeyboardButton("🎤 Аудио AI", callback_data="feature_audio")
        ],
        # Ряд 2: Генерация медиа
        [
            InlineKeyboardButton("🎨 Изображения AI", callback_data="feature_design"),
            InlineKeyboardButton("🎬 Видео AI (Beta)", callback_data="feature_video")
        ],
        # Ряд 3: Знания и Память
        [
            InlineKeyboardButton("🗄 Архив (Память)", callback_data="feature_keeper"),
            InlineKeyboardButton("📚 База знаний", callback_data="feature_knowledge")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)
