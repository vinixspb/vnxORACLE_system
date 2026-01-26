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
            InlineKeyboardButton("💳 Купить START", callback_data="buy_START"),
            InlineKeyboardButton("💳 Купить PRO", callback_data="buy_PRO")
        ],
        [InlineKeyboardButton("💳 Купить NEO", callback_data="buy_NEO")],
        [InlineKeyboardButton("👨‍💻 Связь с Архитектором", url="https://t.me/vinixspb")]
    ]
    return InlineKeyboardMarkup(keyboard)

# --- МЕНЮ ВОЗМОЖНОСТЕЙ (ХАБ) ---
def get_features_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("💡 Выбор Нейросети", callback_data="feature_text"),
            InlineKeyboardButton("🎤 Аудио ИИ", callback_data="feature_audio")
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

# --- АУДИО-ИНСТРУМЕНТЫ ---
def get_audio_keyboard():
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

# --- ВЫБОР ГОЛОСА (TTS) ---
def get_voice_selection_keyboard(current_voice=None):
    voices = [
        ("Adam (Deep)", config.VOICE_ADAM),
        ("Rachel (Soft)", config.VOICE_RACHEL),
        ("Fin (Energy)", config.VOICE_FIN),
        ("Mimi (High)", config.VOICE_MIMI)
    ]
    keyboard = []
    row = []
    for name, v_id in voices:
        prefix = "✅ " if v_id == current_voice else "🎙 "
        row.append(InlineKeyboardButton(prefix + name, callback_data=f"setvoice_{v_id}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row: keyboard.append(row)
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="feature_audio")])
    return InlineKeyboardMarkup(keyboard)

# --- ВЫБОР МОДЕЛИ (LLM) ---
def get_models_keyboard(current_model):
    models = [
        ("GPT-4o Mini", config.MODEL_BASIC),
        ("GPT-4o (Pro)", config.MODEL_PRO),
        ("Claude 3.5 Sonnet", config.MODEL_NEO),
        ("Mistral Devstral (Free)", config.MODEL_DEVSTRAL),
        ("R1T2 Chimera (Free)", config.MODEL_CHIMERA),
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
    if row: keyboard.append(row)
    keyboard.append([InlineKeyboardButton("🔙 Назад в меню", callback_data="back_to_features")])
    return InlineKeyboardMarkup(keyboard)

# --- УПРАВЛЕНИЕ ИСТОРИЕЙ ---
def get_history_keyboard(user_id, mode="view"):
    sessions = db.get_user_sessions(user_id, limit=10)
    if not sessions:
        return None
    
    keyboard = []
    for s in sessions:
        # Обрезаем длинные заголовки для красоты
        title = s['title'][:20] + "..." if len(s['title']) > 20 else s['title']
        date_short = s['created_at'][5:16]
        
        if mode == "view":
            btn_text = f"📂 {title} ({date_short})"
            callback = f"session_{s['id']}"
        else:
            btn_text = f"❌ Удалить: {title}"
            callback = f"del_{s['id']}"
            
        keyboard.append([InlineKeyboardButton(text=btn_text, callback_data=callback)])
    
    if mode == "view":
        keyboard.append([InlineKeyboardButton("🗑 УПРАВЛЕНИЕ АРХИВОМ", callback_data="history_manage")])
    else:
        keyboard.append([InlineKeyboardButton("🔙 НАЗАД", callback_data="history_back")])
        
    return InlineKeyboardMarkup(keyboard)
