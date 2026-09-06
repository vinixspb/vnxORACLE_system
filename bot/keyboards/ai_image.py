from telegram import InlineKeyboardMarkup, InlineKeyboardButton
import config

def get_image_models_keyboard(user_id: int, current_model: str) -> InlineKeyboardMarkup:
    """
    Клавиатура выбора нейросетей для генерации изображений.
    Красивые, продающие названия для пользователей.
    """
    
    start_models = {
        "🔥 Flux 2 Ultra (Топ 2026)": config.IMG_FLUX_PRO,
        "🎨 Midjourney v7 (Фотореализм)": config.IMG_MIDJOURNEY_7,
        "🖌 Qwen VL (Текст на артах)": config.IMG_QWEN_VL,
        "🌟 DALL-E 4 (Креатив)": config.IMG_DALLE_4,
        "⚡️ Ideogram 3 (Типографика)": config.IMG_IDEOGRAM_3,
        "🆓 Pollinations (Бесплатно)": config.IMG_POLLINATIONS
    }

    keyboard = []
    
    # Формируем кнопки с нейросетями
    for name, code in start_models.items():
        display_text = f"✅ {name}" if code == current_model else name
        keyboard.append([InlineKeyboardButton(display_text, callback_data=f"setimg_{code}")])
        
    # Кнопка возврата в главное меню возможностей
    keyboard.append([InlineKeyboardButton("🔙 Назад в меню", callback_data="back_to_features")])
    
    return InlineKeyboardMarkup(keyboard)

def get_ratio_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура выбора пропорций изображения.
    """
    keyboard = [
        [InlineKeyboardButton("📱 Вертикальное (9:16)", callback_data="img_ratio_vertical")],
        [InlineKeyboardButton("⏹ Квадратное (1:1)", callback_data="img_ratio_square")],
        [InlineKeyboardButton("🖥 Горизонтальное (16:9)", callback_data="img_ratio_horizontal")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_post_generation_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура, которая прикрепляется под готовым сгенерированным изображением.
    """
    keyboard = [
        [InlineKeyboardButton("🪄 Редактировать", callback_data="photo_edit"),
         InlineKeyboardButton("✨ Улучшить", callback_data="photo_upscale")],
        [InlineKeyboardButton("🔄 Новая генерация", callback_data="feature_design")],
        [InlineKeyboardButton("🔙 Главное меню", callback_data="back_to_features")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_photo_action_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура умного перехвата при загрузке фото.
    """
    keyboard = [
        [InlineKeyboardButton("👁 Распознать (Vision)", callback_data="photo_vision")],
        [InlineKeyboardButton("🪄 Редактировать (Img2Img)", callback_data="photo_edit")],
        [InlineKeyboardButton("✨ Улучшить (Upscale)", callback_data="photo_upscale")]
    ]
    return InlineKeyboardMarkup(keyboard)
