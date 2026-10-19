"""
🎬 КЛАВИАТУРЫ ДЛЯ ВИДЕО AI
Интерфейс выбора моделей с группировкой по цене и качеству
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config_video_models import VIDEO_MODELS, RECOMMENDED_MODELS, PRICE_TIERS

def get_video_menu_keyboard() -> InlineKeyboardMarkup:
    """
    Главное меню Видео AI - 5 моделей для фильма
    """
    keyboard = [
        [InlineKeyboardButton("⭐️ Seedance 2.0 — Основная ($1.21)", callback_data="video_model_seedance-2.0")],
        [InlineKeyboardButton("🪙 Seedance Mini — Тесты ($0.60)", callback_data="video_model_seedance-2.0-mini")],
        [InlineKeyboardButton("⚡️ Seedance Fast — Черновики ($0.73)", callback_data="video_model_seedance-2.0-fast")],
        [InlineKeyboardButton("💎 Kling Pro — Качество ($0.90)", callback_data="video_model_kling-3.0-pro")],
        [InlineKeyboardButton("🎬 Veo Fast — Альтернатива ($0.64)", callback_data="video_model_veo-3.1-fast")],
        [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_video_models_menu_keyboard() -> InlineKeyboardMarkup:
    """
    Меню выбора категории моделей
    """
    keyboard = [
        [InlineKeyboardButton("⭐️ Рекомендуемые модели", callback_data="video_models_recommended")],
        [InlineKeyboardButton("💰 По цене (дешевле → дороже)", callback_data="video_models_by_price")],
        [InlineKeyboardButton("💎 По качеству (лучшие)", callback_data="video_models_by_quality")],
        [InlineKeyboardButton("🎬 Все модели (17 штук)", callback_data="video_models_all")],
        [InlineKeyboardButton("🔙 Назад", callback_data="feature_video")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_recommended_models_keyboard() -> InlineKeyboardMarkup:
    """
    Топ-3 рекомендуемые модели для начала работы
    """
    keyboard = [
        [InlineKeyboardButton(
            "⭐️ Seedance 2.0 — Лучший баланс ($0.54/8сек)",
            callback_data="video_model_seedance-2.0"
        )],
        [InlineKeyboardButton(
            "🎥 Kling 3.0 Pro — Сохранение лица ($1.34/8сек)",
            callback_data="video_model_kling-3.0-pro"
        )],
        [InlineKeyboardButton(
            "⚡️ Seedance 2.0 Fast — Быстрые тесты ($0.32/8сек)",
            callback_data="video_model_seedance-2.0-fast"
        )],
        [InlineKeyboardButton("🔙 Назад", callback_data="video_models_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_models_by_price_keyboard() -> InlineKeyboardMarkup:
    """
    Все модели, отсортированные по цене (от дешёвых к дорогим)
    """
    # Сортируем все модели по цене
    sorted_models = sorted(
        VIDEO_MODELS.items(),
        key=lambda x: x[1]["price_per_second"]
    )

    keyboard = []

    # Группируем по ценовым категориям
    keyboard.append([InlineKeyboardButton("💸 БЮДЖЕТНЫЕ (до $0.05/сек)", callback_data="noop")])
    for model_key, model_data in sorted_models:
        if model_data["price_per_second"] <= 0.05:
            price_8s = model_data["price_per_second"] * 8
            btn_text = f"{model_data['emoji']} {model_data['name']} — ${price_8s:.2f}"
            keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"video_model_{model_key}")])

    keyboard.append([InlineKeyboardButton("⚖️ СРЕДНИЕ ($0.05-$0.15/сек)", callback_data="noop")])
    for model_key, model_data in sorted_models:
        if 0.05 < model_data["price_per_second"] <= 0.15:
            price_8s = model_data["price_per_second"] * 8
            btn_text = f"{model_data['emoji']} {model_data['name']} — ${price_8s:.2f}"
            keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"video_model_{model_key}")])

    keyboard.append([InlineKeyboardButton("💎 ПРЕМИУМ (>$0.15/сек)", callback_data="noop")])
    for model_key, model_data in sorted_models:
        if model_data["price_per_second"] > 0.15:
            price_8s = model_data["price_per_second"] * 8
            btn_text = f"{model_data['emoji']} {model_data['name']} — ${price_8s:.2f}"
            keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"video_model_{model_key}")])

    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="video_models_menu")])

    return InlineKeyboardMarkup(keyboard)

def get_models_by_quality_keyboard() -> InlineKeyboardMarkup:
    """
    Модели по качеству (от лучших к бюджетным)
    """
    keyboard = []

    # Premium tier
    keyboard.append([InlineKeyboardButton("💎 ПРЕМИУМ КАЧЕСТВО", callback_data="noop")])
    for model_key in PRICE_TIERS["premium"]:
        model_data = VIDEO_MODELS[model_key]
        price_8s = model_data["price_per_second"] * 8
        btn_text = f"{model_data['emoji']} {model_data['name']} — ${price_8s:.2f}"
        keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"video_model_{model_key}")])

    # High quality
    keyboard.append([InlineKeyboardButton("⚡️ ВЫСОКОЕ КАЧЕСТВО", callback_data="noop")])
    for model_key in PRICE_TIERS["high"][:4]:  # Показываем первые 4
        model_data = VIDEO_MODELS[model_key]
        price_8s = model_data["price_per_second"] * 8
        btn_text = f"{model_data['emoji']} {model_data['name']} — ${price_8s:.2f}"
        keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"video_model_{model_key}")])

    keyboard.append([InlineKeyboardButton("➕ Показать ещё", callback_data="video_models_all")])
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="video_models_menu")])

    return InlineKeyboardMarkup(keyboard)

def get_all_models_keyboard(page: int = 0) -> InlineKeyboardMarkup:
    """
    Все 17 моделей с пагинацией (по 8 на странице)
    """
    models_per_page = 8
    all_models = list(VIDEO_MODELS.keys())
    total_pages = (len(all_models) + models_per_page - 1) // models_per_page

    start_idx = page * models_per_page
    end_idx = min(start_idx + models_per_page, len(all_models))
    page_models = all_models[start_idx:end_idx]

    keyboard = []

    for model_key in page_models:
        model_data = VIDEO_MODELS[model_key]
        price_8s = model_data["price_per_second"] * 8
        btn_text = f"{model_data['emoji']} {model_data['name']} — ${price_8s:.2f}"
        keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"video_model_{model_key}")])

    # Пагинация
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"video_models_page_{page-1}"))
    nav_buttons.append(InlineKeyboardButton(f"{page+1}/{total_pages}", callback_data="noop"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("➡️ Далее", callback_data=f"video_models_page_{page+1}"))

    if nav_buttons:
        keyboard.append(nav_buttons)

    keyboard.append([InlineKeyboardButton("🔙 К категориям", callback_data="video_models_menu")])

    return InlineKeyboardMarkup(keyboard)

def get_video_generation_keyboard(model_key: str) -> InlineKeyboardMarkup:
    """
    Клавиатура выбора режима генерации после выбора модели
    """
    model_data = VIDEO_MODELS.get(model_key)

    keyboard = []

    # Text-to-Video
    if "text2video" in model_data["capabilities"]:
        keyboard.append([InlineKeyboardButton(
            "📝 Создать из текста (Text2Video)",
            callback_data=f"video_text_{model_key}"
        )])

    # Image-to-Video
    if "image2video" in model_data["capabilities"]:
        keyboard.append([InlineKeyboardButton(
            "🖼 Оживить картинку (Image2Video)",
            callback_data=f"video_image_{model_key}"
        )])

    keyboard.append([InlineKeyboardButton("🔙 Выбрать другую модель", callback_data="video_models_menu")])

    return InlineKeyboardMarkup(keyboard)

def get_model_info_text(model_key: str) -> str:
    """
    Форматированное описание модели для отображения пользователю
    """
    model_data = VIDEO_MODELS.get(model_key)

    if not model_data:
        return "❌ Модель не найдена"

    price_8s = model_data["price_per_second"] * 8
    capabilities = ", ".join(model_data["capabilities"])

    text = (
        f"{model_data['emoji']} <b>{model_data['name']}</b>\n"
        f"<i>{model_data['provider']}</i>\n\n"
        f"💰 Цена: <b>${price_8s:.2f}</b> за 8 секунд\n"
        f"🎯 Возможности: {capabilities}\n\n"
        f"📋 <i>{model_data['description']}</i>\n\n"
        f"✨ <b>Лучше всего для:</b>\n{model_data['best_for']}\n\n"
        f"Выберите режим генерации:"
    )

    return text

def get_video_image_action_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура выбора действия после загрузки фотографии для Image-to-Video
    """
    keyboard = [
        [InlineKeyboardButton("🎲 Случайная генерация", callback_data="video_image_random")],
        [InlineKeyboardButton("✍️ По моему заданию", callback_data="video_image_custom")],
        [InlineKeyboardButton("🔙 Отмена / назад", callback_data="video_image_cancel")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_video_format_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура выбора формата видео (аналог get_ratio_keyboard из блока изображений)
    """
    keyboard = [
        [InlineKeyboardButton("🖥 16:9 — горизонтальное", callback_data="video_format_16_9")],
        [InlineKeyboardButton("📱 9:16 — вертикальное", callback_data="video_format_9_16")],
        [InlineKeyboardButton("🔙 Назад", callback_data="video_format_back")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_post_video_generation_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура под готовым видео (аналог get_post_generation_keyboard из блока изображений)
    """
    keyboard = [
        [InlineKeyboardButton("🔄 Новое видео", callback_data="feature_video")],
        [InlineKeyboardButton("🔙 Главное меню", callback_data="back_to_features")]
    ]
    return InlineKeyboardMarkup(keyboard)
