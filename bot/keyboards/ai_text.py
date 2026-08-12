from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from loader import sheets_mgr # Нам нужен менеджер таблиц для проверки тарифа
import config
import config_models # Импортируем наш реестр

def get_models_keyboard(user_id, current_model):
    """Генерирует меню моделей, доступных конкретному пользователю"""
    
    # 1. Узнаем тариф
    user_tariff = sheets_mgr.get_user_tariff(user_id)
    if not user_tariff: user_tariff = "START" # Fallback
    
    # 2. Получаем список моделей для этого тарифа
    available_models = config_models.get_available_models(user_tariff)
    
    keyboard = []
    row = []
    
    for name, code in available_models:
        # Индикация выбранной модели
        prefix = "✅ " if code == current_model else "⚪️ "
        row.append(InlineKeyboardButton(prefix + name, callback_data=f"setmodel_{code}"))
        
        # Разбивка по 2 в ряд (или по 1 если название длинное)
        if len(row) == 2:
            keyboard.append(row)
            row = []
            
    if row: keyboard.append(row)
    
    # Если тариф START или PRO, предлагаем апгрейд
    if user_tariff == "START":
        keyboard.append([InlineKeyboardButton("🔒 Открыть PRO-модели", callback_data="buy_PRO")])
    elif user_tariff == "PRO":
        keyboard.append([InlineKeyboardButton("🔒 Открыть NEO-модели", callback_data="buy_NEO")])
        
    keyboard.append([InlineKeyboardButton("🔙 Назад в меню", callback_data="back_to_features")])
    
    return InlineKeyboardMarkup(keyboard)
