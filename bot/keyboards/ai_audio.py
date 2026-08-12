from telegram import InlineKeyboardMarkup, InlineKeyboardButton
import config

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

def get_voice_selection_keyboard(current_voice=None):
    voices = [
        ("👨‍💼 Adam (Deep Male)", config.VOICE_ADAM),
        ("👩‍💼 Rachel (Calm Female)", config.VOICE_RACHEL),
        ("🧔 Fin (Energetic)", config.VOICE_FIN),
        ("👧 Mimi (Cute)", config.VOICE_MIMI)
    ]
    
    keyboard = []
    row = []
    for name, v_id in voices:
        prefix = "✅ " if v_id == current_voice else ""
        # Кнопка устанавливает голос
        row.append(InlineKeyboardButton(f"{prefix}{name}", callback_data=f"setvoice_{v_id}"))
        
        if len(row) == 1: # По одному в ряд для длинных названий (или сделай 2, если влезают)
            keyboard.append(row)
            row = []
            
    if row: keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="feature_audio")])
    return InlineKeyboardMarkup(keyboard)
