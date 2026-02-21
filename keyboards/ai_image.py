from telegram import InlineKeyboardMarkup, InlineKeyboardButton
import config

def get_image_models_keyboard(user_id: int, current_model: str) -> InlineKeyboardMarkup:
    """
    Клавиатура выбора нейросетей для генерации изображений.
    Показывает базовые модели из тарифа START.
    """
    
    # Список моделей из config.py для тарифа START
    start_models = {
        "⚡️ Flux 1 Schnell": config.IMG_FLUX_SCHNELL,
        "🎨 SD 3 Medium": config.IMG_SD3_TURBO,
        "🌌 Playground v2.5": config.IMG_PLAYGROUND,
        "🆓 Pollinations (Free)": config.IMG_POLLINATIONS
    }

    keyboard = []
    
    # Формируем кнопки с нейросетями (по одной в ряд для удобства чтения)
    for name, code in start_models.items():
        # Если модель текущая, ставим зеленую галочку
        display_text = f"✅ {name}" if code == current_model else name
        keyboard.append([InlineKeyboardButton(display_text, callback_data=f"setimg_{code}")])
        
    # Кнопка возврата в главное меню возможностей
    keyboard.append([InlineKeyboardButton("🔙 Назад в меню", callback_data="back_to_features")])
    
    return InlineKeyboardMarkup(keyboard)
