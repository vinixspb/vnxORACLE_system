from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_video_menu_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура подменю для раздела Видео Ai (Режиссерская)
    """
    keyboard = [
        [InlineKeyboardButton("📝 Создать из текста (Text2Video)", callback_data="video_text")],
        [InlineKeyboardButton("🖼 Оживить картинку (Image2Video)", callback_data="video_image")],
        [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)
