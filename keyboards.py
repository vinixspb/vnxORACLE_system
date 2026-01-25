from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import config
from loader import db

def get_main_keyboard():
    keyboard = [
        [KeyboardButton(config.BTN_NEW_DIALOG), KeyboardButton(config.BTN_HISTORY)],
        [KeyboardButton(config.BTN_PROFILE), KeyboardButton(config.BTN_TARIFFS)],
        [KeyboardButton(config.BTN_CHANGE_MODEL), KeyboardButton(config.BTN_HELP)]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_subscription_keyboard():
    keyboard = [
        [InlineKeyboardButton("💠 START (190₽)", callback_data="buy_START")],
        [InlineKeyboardButton("⚡️ PRO (590₽)", callback_data="buy_PRO")],
        [InlineKeyboardButton("🧬 NEO (990₽)", callback_data="buy_NEO")],
        [InlineKeyboardButton("👨‍💻 Связь с Архитектором", url="https://t.me/vinixspb")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_features_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("💡 GPTs/Claude/Gemini", callback_data="feature_text"),
            InlineKeyboardButton("🎤 Аудио с ИИ", callback_data="feature_audio")
        ],
        [
            InlineKeyboardButton("🎨 Дизайн с ИИ", callback_data="feature_design"),
            InlineKeyboardButton("📹 Видео будущего", callback_data="feature_video")
        ],
        [InlineKeyboardButton("🗄 Хранитель (Архив)", callback_data="feature_keeper")],
        [
            InlineKeyboardButton("❓ Помощь", callback_data="feature_help"),
            InlineKeyboardButton("📚 База знаний", callback_data="feature_knowledge")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_models_keyboard(current_model):
    models = [
        ("GPT-4o Mini", config.MODEL_BASIC),
        ("GPT-4o", config.MODEL_PRO),
        ("Claude 3.5 Sonnet", config.MODEL_NEO)
    ]
    keyboard = []
    for name, code in models:
        prefix = "✅ " if code == current_model else "⚪️ "
        keyboard.append([InlineKeyboardButton(prefix + name, callback_data=f"setmodel_{code}")])
    keyboard.append([InlineKeyboardButton("🔙 Назад в меню", callback_data="back_to_features")])
    return InlineKeyboardMarkup(keyboard)

def get_history_keyboard(user_id, mode="view"):
    """Улучшенная история: длинные кнопки и переключение режимов"""
    sessions = db.get_user_sessions(user_id, limit=10)
    if not sessions: 
        return None
    
    keyboard = []
    
    if mode == "view":
        for s in sessions:
            date_short = s['created_at'][5:16]
            title_text = f"📂 {s['title']} ({date_short})"
            keyboard.append([InlineKeyboardButton(text=title_text, callback_data=f"session_{s['id']}")])
        
        # Кнопка перехода в режим удаления
        keyboard.append([InlineKeyboardButton(text="🗑 УПРАВЛЕНИЕ АРХИВОМ", callback_data="history_manage")])
    
    elif mode == "delete":
        for s in sessions:
            title_text = f"❌ Стереть: {s['title']}"
            keyboard.append([InlineKeyboardButton(text=title_text, callback_data=f"del_{s['id']}")])
        
        # Кнопка возврата к обычному виду
        keyboard.append([InlineKeyboardButton(text="🔙 НАЗАД", callback_data="history_back")])
        
    return InlineKeyboardMarkup(keyboard)
