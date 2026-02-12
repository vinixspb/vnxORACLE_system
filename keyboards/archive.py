from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from loader import db

def get_history_keyboard(user_id, mode="view"):
    """
    Генерация списка сессий.
    mode="view" - для восстановления чата
    mode="delete" - для удаления
    """
    sessions = db.get_user_sessions(user_id, limit=10)
    
    # Если сессий нет, возвращаем None (хендлер скажет "Архив пуст")
    if not sessions:
        return None
    
    keyboard = []
    for s in sessions:
        # Обрезаем длинные заголовки
        title = s['title'][:20] + "..." if len(s['title']) > 20 else s['title']
        date_short = s['created_at'][5:16]
        
        if mode == "view":
            btn_text = f"📂 {title} ({date_short})"
            callback = f"session_{s['id']}"
        else:
            btn_text = f"❌ Удалить: {title}"
            callback = f"del_{s['id']}"
            
        keyboard.append([InlineKeyboardButton(text=btn_text, callback_data=callback)])
    
    # Кнопки управления внизу списка
    if mode == "view":
        keyboard.append([InlineKeyboardButton("🗑 УПРАВЛЕНИЕ АРХИВОМ", callback_data="history_manage")])
    else:
        keyboard.append([InlineKeyboardButton("🔙 НАЗАД", callback_data="history_back")])
        
    return InlineKeyboardMarkup(keyboard)
