from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import config

# --- ГЛАВНОЕ МЕНЮ (REPLY - 4 КНОПКИ) ---
def get_main_keyboard():
    keyboard = [
        # Ряд 1: НОВЫЙ ЧАТ и ИСТОРИЯ (Обе кнопки вверху)
        [KeyboardButton(config.BTN_NEW_DIALOG), KeyboardButton(config.BTN_HISTORY)],
        
        # Ряд 2: Выбор модели и Профиль (Внизу)
        [KeyboardButton(config.BTN_CHANGE_MODEL), KeyboardButton(config.BTN_PROFILE)]
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
            InlineKeyboardButton("💬 Диалог Ai", callback_data="feature_text"),
            InlineKeyboardButton("🎤 Аудио Ai", callback_data="feature_audio")
        ],
        # Ряд 2: Генерация медиа
        [
            InlineKeyboardButton("🎨 Изображения Ai", callback_data="feature_design"),
            InlineKeyboardButton("🎬 Видео Ai (Beta)", callback_data="feature_video")
        ],
        # Ряд 3: НОВЫЙ МОДУЛЬ OPENCLAW (на всю ширину)
        [
            InlineKeyboardButton("🦞 OpenClaw", callback_data="feature_openclaw")
        ],
        # Ряд 4: Знания и Память
        [
            InlineKeyboardButton("🗄 Архив (Память)", callback_data="feature_keeper"),
            InlineKeyboardButton("📚 База знаний", callback_data="feature_knowledge")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)
