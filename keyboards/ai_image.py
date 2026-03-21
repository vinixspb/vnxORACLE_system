from telegram import InlineKeyboardMarkup, InlineKeyboardButton
import config

def get_image_models_keyboard(user_id: int, current_model: str) -> InlineKeyboardMarkup:
    """
    Клавиатура выбора нейросетей для генерации изображений.
    Обновлено: Март 2026 (Добавлены Qwen 2.0, GPT-4o Image)
    """
    
    # 🎨 Модели START (Базовый тариф)
    start_models = {
        "⚡️ Flux Pro (Текст и Логотипы)": config.IMG_FLUX_SCHNELL,
        "🍌 Nano Banana (Яркий Арт)": config.IMG_NANO_BANANA,
        "🌌 Seedream (Фэнтези и Магия)": config.IMG_SEEDREAM,
        "🆓 Pollinations (Быстрый старт)": config.IMG_POLLINATIONS
    }
    
    # 🎨 Модели PRO (расширенные)
    pro_models = {
        "🎯 Qwen 2.0 (Текст на картинках)": config.IMG_QWEN_2,
        "🧠 GPT-4o Image (Фотореализм)": config.IMG_GPT_4O
    }
    
    keyboard = []
    
    # 1. Добавляем базовые модели
    for name, code in start_models.items():
        display_text = f"✅ {name}" if code == current_model else name
        keyboard.append([InlineKeyboardButton(display_text, callback_data=f"setimg_{code}")])
    
    # 2. Добавляем PRO модели (если пользователь имеет доступ)
    # TODO: Добавить проверку тарифа пользователя
    # Пока показываем всем, но можно ограничить:
    # from loader import sheets_mgr
    # user_tariff = sheets_mgr.get_user_tariff(user_id)
    # if user_tariff in ['PRO', 'NEO']:
    
    for name, code in pro_models.items():
        display_text = f"✅ {name}" if code == current_model else name
        keyboard.append([InlineKeyboardButton(display_text, callback_data=f"setimg_{code}")])
    
    # 3. Кнопка возврата
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
    Клавиатура под готовым изображением.
    Обновлено: добавлена кнопка сохранения в архив.
    """
    keyboard = [
        [
            InlineKeyboardButton("🔄 Новая генерация", callback_data="feature_design"),
            InlineKeyboardButton("📐 Изменить размер", callback_data="img_change_ratio")
        ],
        [
            InlineKeyboardButton("✨ Улучшить качество", callback_data="img_upscale"),
            InlineKeyboardButton("🎨 Другая модель", callback_data="feature_text")
        ],
        [InlineKeyboardButton("🔙 Главное меню", callback_data="back_to_features")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_photo_action_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура умного перехвата при загрузке фото.
    Используется для Vision, Upscale, Img2Img.
    """
    keyboard = [
        [
            InlineKeyboardButton("👁 Распознать (Vision)", callback_data="photo_vision"),
            InlineKeyboardButton("✨ Улучшить (Upscale)", callback_data="photo_upscale")
        ],
        [
            InlineKeyboardButton("🪄 Редактировать (Img2Img)", callback_data="photo_edit"),
            InlineKeyboardButton("🔄 Новая вариация", callback_data="photo_variation")
        ],
        [InlineKeyboardButton("❌ Отмена", callback_data="back_to_features")]
    ]
    return InlineKeyboardMarkup(keyboard)
