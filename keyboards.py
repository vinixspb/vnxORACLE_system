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
            InlineKeyboardButton("💡 Выбор Нейросети", callback_data="feature_text"),
            InlineKeyboardButton("🎤 Аудио-Студия", callback_data="feature_audio")
        ],
        [
            InlineKeyboardButton("🎨 Дизайн с ИИ", callback_data="feature_design"),
            InlineKeyboardButton("📹 Видео (Beta)", callback_data="feature_video")
        ],
        [InlineKeyboardButton("🗄 Хранитель (Архив)", callback_data="feature_keeper")],
        [
            InlineKeyboardButton("❓ Помощь", callback_data="feature_help"),
            InlineKeyboardButton("📚 База знаний", callback_data="feature_knowledge")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_audio_keyboard():
    """Новое меню аудио-инструментов"""
    keyboard = [
        [
            InlineKeyboardButton("🗣 ElevenLabs Voice", callback_data="audio_tts"),
            InlineKeyboardButton("🎵 SUNO Music", callback_data="audio_suno")
        ],
        [
            InlineKeyboardButton("🔊 Генератор звуков", callback_data="audio_sfx"),
            InlineKeyboardButton("🦜 Клонирование голоса", callback_data="audio_clone")
        ],
        [
            InlineKeyboardButton("📹 Видео -> Аудио", callback_data="audio_vid2aud"),
            InlineKeyboardButton("📝 Аудио -> Текст", callback_data="audio_transcribe")
        ],
        [InlineKeyboardButton("🎼 ElevenLabs Music", callback_data="audio_eleven_music")],
        [InlineKeyboardButton("🔙 Назад в меню", callback_data="back_to_features")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_models_keyboard(current_model):
    models = [
        ("GPT-4o Mini", config.MODEL_BASIC),
        ("Mistral Devstral (Free)", config.MODEL_DEVSTRAL),
        
        ("GPT-4o (Pro)", config.MODEL_PRO),
        ("R1T2 Chimera (Free)", config.MODEL_CHIMERA),
        
        ("Claude 3.5 Sonnet", config.MODEL_NEO),
        ("Liquid LFM 2.5 (Free)", config.MODEL_LIQUID)
    ]
    
    keyboard = []
    row = []
    for name, code in models:
        prefix = "✅ " if code == current_model else "⚪️ "
        row.append(InlineKeyboardButton(prefix + name, callback_data=f"setmodel_{code}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
        
    keyboard.append([InlineKeyboardButton("🔙 Назад в меню", callback_data="back_to_features")])
    return InlineKeyboardMarkup(keyboard)

def get_history_keyboard(user_id, mode="view"):
    sessions = db.get_user_sessions(user_id, limit=10)
    if not sessions: 
        return None
    
    keyboard = []
    if mode == "view":
        for s in sessions:
            date_short = s['created_at'][5:16]
            title_text = f"📂 {s['title']} ({date_short})"
            keyboard.append([InlineKeyboardButton(text=title_text, callback_data=f"session_{s['id']}")])
        keyboard.append([InlineKeyboardButton(text="🗑 УПРАВЛЕНИЕ АРХИВОМ", callback_data="history_manage")])
    
    elif mode == "delete":
        for s in sessions:
            title_text = f"❌ Стереть: {s['title']}"
            keyboard.append([InlineKeyboardButton(text=title_text, callback_data=f"del_{s['id']}")])
        keyboard.append([InlineKeyboardButton(text="🔙 НАЗАД", callback_data="history_back")])
        
    return InlineKeyboardMarkup(keyboard)
