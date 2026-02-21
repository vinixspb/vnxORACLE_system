from telegram import InlineKeyboardMarkup, InlineKeyboardButton
import config

def get_image_models_keyboard(user_id: int, current_model: str) -> InlineKeyboardMarkup:
    """
    Клавиатура выбора нейросетей для генерации изображений.
    Показывает базовые модели из тарифа START.
    """
    
    # Обновленный список с актуальными названиями моделей
    start_models = {
        "⚡️ Flux Pro (Kontext)": config.IMG_FLUX_SCHNELL,
        "🍌 Nano Banana (Google)": config.IMG_SD3_TURBO,
        "🌌 Seedream Art": config.IMG_PLAYGROUND,
        "🆓 Pollinations (Free)": config.IMG_POLLINATIONS
    }

    keyboard = []
    
    # Формируем кнопки с нейросетями
    for name, code in start_models.items():
        display_text = f"✅ {name}" if code == current_model else name
        keyboard.append([InlineKeyboardButton(display_text, callback_data=f"setimg_{code}")])
        
    # Кнопка возврата в главное меню возможностей
    keyboard.append([InlineKeyboardButton("🔙 Назад в меню", callback_data="back_to_features")])
    
    return InlineKeyboardMarkup(keyboard)
