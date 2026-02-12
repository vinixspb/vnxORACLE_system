from telegram import InlineKeyboardMarkup, InlineKeyboardButton
import config

def get_models_keyboard(current_model):
    """Клавиатура выбора LLM моделей с индикацией текущей"""
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
        # Ставим галочку, если модель активна
        prefix = "✅ " if code == current_model else "⚪️ "
        row.append(InlineKeyboardButton(prefix + name, callback_data=f"setmodel_{code}"))
        
        # Разбиваем по 2 кнопки в ряд
        if len(row) == 2:
            keyboard.append(row)
            row = []
            
    if row: keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton("🔙 Назад в меню", callback_data="back_to_features")])
    return InlineKeyboardMarkup(keyboard)
