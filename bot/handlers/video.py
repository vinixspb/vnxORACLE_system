"""
🎬 ОБРАБОТЧИКИ ВИДЕО AI
Полная поддержка всех 17 моделей OpenRouter + KIE fallback
"""

import logging
import os
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes
from services.video_router import video_router
from services.kie_client import kie_studio
from loader import sheets_mgr
from services.prompt_censor import is_prompt_safe, clean_prompt
from services.messages import get_wait_message, DynamicWaitMessage
from keyboards.ai_video import (
    get_video_generation_keyboard,
    get_model_info_text,
    get_post_video_generation_keyboard,
    get_video_image_action_keyboard,
    get_video_format_keyboard
)
import config
from config_video_models import VIDEO_MODELS, get_model_info

logger = logging.getLogger(__name__)

async def ask_video_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE, video_type: str, model_key: str = None):
    """
    Запрос промпта или изображения для генерации видео.

    Args:
        video_type: "text" или "image"
        model_key: Ключ выбранной модели из config_video_models
    """
    query = update.callback_query
    await query.answer()

    # Сохраняем выбранную модель
    if model_key:
        context.user_data['video_model'] = model_key
        model_info = get_model_info(model_key)
        model_name = model_info['name'] if model_info else "Unknown"
    else:
        context.user_data['video_model'] = None
        model_name = "Seedance 2.0 (по умолчанию)"

    if video_type == "text":
        context.user_data['mode'] = 'video_text_wait'
        text = (
            f"📝 <b>Text-to-Video: {model_name}</b>\n\n"
            f"Опишите сцену максимально подробно. Нейросеть лучше всего понимает запросы на <b>английском языке</b>.\n\n"
            f"<i>Пример: A cinematic drone shot of a futuristic cyberpunk city at night, neon lights reflecting on wet streets, flying cars in the distance...</i>\n\n"
            f"💡 <b>Советы для лучшего результата:</b>\n"
            f"• Укажите стиль: cinematic, documentary, anime, etc.\n"
            f"• Опишите движение: slow motion, tracking shot, zoom in\n"
            f"• Добавьте детали: lighting, weather, mood\n"
            f"• Длительность: обычно 4-8 секунд"
        )
    elif video_type == "image":
        context.user_data['mode'] = 'video_image_wait'
        text = (
            f"🖼 <b>Image-to-Video: {model_name}</b>\n\n"
            f"Отправьте фотографию или изображение, которое вы хотите «оживить».\n\n"
            f"💡 <b>Советы:</b>\n"
            f"• Лучше всего работают портреты с чётким лицом\n"
            f"• Избегайте слишком сложных композиций\n"
            f"• Качество изображения влияет на результат\n\n"
            f"После отправки изображения вы сможете добавить промпт для описания желаемого движения."
        )

    await query.edit_message_text(text, parse_mode='HTML')

async def handle_video_text_request(update: Update, context: ContextTypes.DEFAULT_TYPE, prompt: str):
    """
    Обработка text-to-video запроса с выбранной моделью
    """
    user_id = update.effective_user.id
    context.user_data['mode'] = None

    # Проверка цензуры
    if not is_prompt_safe(prompt):
        await update.message.reply_text(
            "🔞 <b>Запрос отклонен цензурой.</b>\n"
            "Система безопасности заблокировала генерацию. Я не создаю откровенный, NSFW (18+) или жестокий контент. "
            "Пожалуйста, измените описание.",
            parse_mode='HTML'
        )
        return

    safe_api_prompt = clean_prompt(prompt)

    # Проверка тарифа
    tariff = sheets_mgr.get_user_tariff(user_id)
    if tariff not in ['PRO', 'NEO']:
        await update.message.reply_text(
            "🎬 <b>Модуль Видео AI</b> доступен только на тарифах PRO и NEO.\n\n"
            "Обновите тариф в разделе «👤 Мой профиль» → «💳 Тарифные планы»",
            parse_mode='HTML'
        )
        return

    # Получаем выбранную модель
    model_key = context.user_data.get('video_model')
    model_info = get_model_info(model_key) if model_key else None

    if not model_info:
        # Fallback на рекомендуемую модель
        model_key = "seedance-2.0"
        model_info = get_model_info(model_key)

    model_name = model_info['name']
    model_id = model_info['id']

    await context.bot.send_chat_action(chat_id=user_id, action=ChatAction.RECORD_VIDEO)

    # Рассчитываем стоимость
    from config_video_models import calculate_cost
    estimated_cost = calculate_cost(model_key, 8)

    prefix = (
        f"⚠️ <i>Процесс генерации занимает от 2 до 5 минут.</i>\n"
        f"🎬 Модель: <b>{model_name}</b>\n"
        f"💰 Примерная стоимость: <b>${estimated_cost:.3f}</b>\n\n"
    )

    msg = await update.message.reply_text(f"{prefix}{get_wait_message('video')}", parse_mode='HTML')

    loader = DynamicWaitMessage(msg, "video", prefix)
    loader.start()

    try:
        # Генерация через OpenRouter
        video_url = await video_router.generate_video(
            prompt=safe_api_prompt,
            model_key=model_key,
            tariff=tariff,
            duration=8
        )

        # ⚠️ ВРЕМЕННО ОТКЛЮЧЕНО для первого теста:
        # Fallback на KIE может вызвать двойное списание при временной ошибке OpenRouter
        # После успешного теста можно включить обратно

        # if not video_url:
        #     logger.warning(f"OpenRouter failed, trying KIE fallback...")
        #     kie_model = getattr(config, 'VIDEO_KLING_3', "kling-3-motion-control")
        #     video_url = await video_router.generate_video_kie_fallback(
        #         prompt=safe_api_prompt,
        #         model=kie_model
        #     )

    except Exception as e:
        logger.error(f"Video generation error: {e}", exc_info=True)
        video_url = None
    finally:
        loader.stop()

    if video_url:
        try:
            cost_credits = 10  # TODO: динамический подсчёт кредитов
            footer = f"\n\n⚙️ {model_name} | 🎬 Video AI | 🎫 {cost_credits} credits"
            caption_text = (
                f"🎬 <b>Video AI</b>\n"
                f"Модель: <code>{model_name}</code>\n"
                f"Промпт: <i>{safe_api_prompt[:100]}{'...' if len(safe_api_prompt) > 100 else ''}</i>"
                f"{footer}"
            )

            await context.bot.send_video(
                chat_id=user_id,
                video=video_url,
                caption=caption_text,
                parse_mode='HTML',
                reply_markup=get_post_video_generation_keyboard()
            )
            await msg.delete()

        except Exception as e:
            logger.error(f"Telegram Video Send Error: {e}")
            await msg.edit_text(
                f"✅ Видео сгенерировано, но Telegram не смог его загрузить (возможно, слишком большой размер).\n\n"
                f"🔗 <b>Ссылка для скачивания:</b>\n{video_url}",
                parse_mode='HTML'
            )
    else:
        await msg.edit_text(
            "❌ <b>Сбой рендеринга.</b>\n\n"
            "Нейросеть отклонила запрос или время ожидания истекло. Возможные причины:\n"
            "• Промпт содержит запрещённый контент\n"
            "• Сервис временно перегружен\n"
            "• Технический сбой на стороне провайдера\n\n"
            "Попробуйте изменить описание или повторить попытку через пару минут.",
            parse_mode='HTML'
        )

async def handle_video_image_request(update: Update, context: ContextTypes.DEFAULT_TYPE, image_path: str):
    """
    Обработка image-to-video запроса (НОВЫЙ UX по образцу блока изображений)
    """
    user_id = update.effective_user.id

    # Проверка тарифа
    tariff = sheets_mgr.get_user_tariff(user_id)
    if tariff not in ['PRO', 'NEO']:
        await update.message.reply_text(
            "🎬 <b>Модуль Видео AI</b> доступен только на тарифах PRO и NEO.",
            parse_mode='HTML'
        )
        return

    # Получаем выбранную модель
    model_key = context.user_data.get('video_model')
    model_info = get_model_info(model_key) if model_key else None

    if not model_info:
        model_key = "seedance-2.0"
        model_info = get_model_info(model_key)

    # Проверяем поддержку image-to-video
    if "image2video" not in model_info['capabilities']:
        await update.message.reply_text(
            f"❌ Модель <b>{model_info['name']}</b> не поддерживает Image-to-Video.\n\n"
            f"Пожалуйста, выберите другую модель из меню.",
            parse_mode='HTML'
        )
        return

    # Сохраняем путь к фото и переходим к выбору действия
    context.user_data['video_image_path'] = image_path
    context.user_data['mode'] = 'video_image_action_choice'

    await update.message.reply_text(
        "🖼 <b>Фотография получена!</b>\n\n"
        "Теперь выберите, как оживить изображение:\n\n"
        "🎲 <b>Случайная генерация</b> — бот сам выберет подходящий вариант движения.\n"
        "✍️ <b>По моему заданию</b> — вы сами опишете, что должно происходить в видео.\n"
        "🔙 <b>Отмена / назад</b> — выйти из текущего сценария.",
        reply_markup=get_video_image_action_keyboard(),
        parse_mode='HTML'
    )

async def handle_video_image_with_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE, prompt: str):
    """
    Генерация image-to-video с промптом
    """
    user_id = update.effective_user.id
    context.user_data['mode'] = None

    image_path = context.user_data.get('video_image_path')
    if not image_path:
        await update.message.reply_text("❌ Изображение не найдено. Попробуйте снова.", parse_mode='HTML')
        return

    # Проверка цензуры
    if prompt != "/skip" and not is_prompt_safe(prompt):
        await update.message.reply_text(
            "🔞 <b>Запрос отклонен цензурой.</b>\nПожалуйста, измените описание.",
            parse_mode='HTML'
        )
        return

    safe_prompt = clean_prompt(prompt) if prompt != "/skip" else "natural motion"

    # Получаем модель
    tariff = sheets_mgr.get_user_tariff(user_id)
    model_key = context.user_data.get('video_model', "seedance-2.0")
    model_info = get_model_info(model_key)
    model_name = model_info['name']

    await context.bot.send_chat_action(chat_id=user_id, action=ChatAction.RECORD_VIDEO)

    from config_video_models import calculate_cost
    estimated_cost = calculate_cost(model_key, 8)

    prefix = (
        f"⚠️ <i>Процесс генерации занимает от 2 до 5 минут.</i>\n"
        f"🎬 Модель: <b>{model_name}</b>\n"
        f"🖼 Режим: Image-to-Video\n"
        f"💰 Примерная стоимость: <b>${estimated_cost:.3f}</b>\n\n"
    )

    msg = await update.message.reply_text(f"{prefix}{get_wait_message('video')}", parse_mode='HTML')

    loader = DynamicWaitMessage(msg, "video", prefix)
    loader.start()

    try:
        # Генерация через OpenRouter
        video_url = await video_router.generate_video(
            prompt=safe_prompt,
            model_key=model_key,
            tariff=tariff,
            source_image=image_path,
            duration=8
        )

        # ⚠️ ВРЕМЕННО ОТКЛЮЧЕНО для первого теста:
        # Fallback на KIE может вызвать двойное списание при временной ошибке OpenRouter
        # После успешного теста можно включить обратно

        # if not video_url:
        #     logger.warning(f"OpenRouter failed, trying KIE fallback...")
        #     kie_model = getattr(config, 'VIDEO_KLING_3', "kling-3-motion-control")
        #     video_url = await video_router.generate_video_kie_fallback(
        #         prompt=safe_prompt,
        #         model=kie_model,
        #         source_image=image_path
        #     )

    except Exception as e:
        logger.error(f"Image-to-video error: {e}", exc_info=True)
        video_url = None
    finally:
        loader.stop()

    if video_url:
        try:
            cost_credits = 15  # Image-to-video дороже
            footer = f"\n\n⚙️ {model_name} | 🖼➡️🎬 Image2Video | 🎫 {cost_credits} credits"
            caption_text = (
                f"🎬 <b>Video AI (Image-to-Video)</b>\n"
                f"Модель: <code>{model_name}</code>\n"
                f"Промпт: <i>{safe_prompt[:100]}...</i>"
                f"{footer}"
            )

            await context.bot.send_video(
                chat_id=user_id,
                video=video_url,
                caption=caption_text,
                parse_mode='HTML',
                reply_markup=get_post_video_generation_keyboard()
            )
            await msg.delete()

        except Exception as e:
            logger.error(f"Telegram Video Send Error: {e}")
            await msg.edit_text(
                f"✅ Видео сгенерировано.\n\n🔗 <b>Ссылка для скачивания:</b>\n{video_url}",
                parse_mode='HTML'
            )
    else:
        await msg.edit_text(
            "❌ <b>Сбой рендеринга.</b>\n\n"
            "Попробуйте другую модель или изображение.",
            parse_mode='HTML'
        )

    # Очистка временных данных
    context.user_data.pop('video_image_path', None)

async def handle_video_image_with_prompt_and_format(update: Update, context: ContextTypes.DEFAULT_TYPE, prompt: str, image_path: str, aspect_ratio: str):
    """
    Генерация image-to-video с промптом и форматом (НОВЫЙ UX)
    """
    user_id = update.effective_user.id

    # Этот обработчик вызывается и сообщением, и inline-кнопкой.
    # Не используем update.message: у CallbackQuery оно равно None.
    context.user_data['mode'] = None

    if not image_path or not os.path.isfile(image_path):
        context.user_data['mode'] = 'video_image_wait'
        await context.bot.send_message(
            chat_id=user_id,
            text="⚠️ Исходная фотография не найдена. Отправьте её ещё раз.",
            parse_mode='HTML'
        )
        return

    # Проверка цензуры: при отказе возвращаем пользователя к вводу промпта.
    if prompt != "/skip" and not is_prompt_safe(prompt):
        context.user_data['mode'] = 'video_image_custom_prompt_wait'
        await context.bot.send_message(
            chat_id=user_id,
            text="🔞 <b>Запрос отклонен цензурой.</b>\nОпишите движение иначе или напишите «Отмена».",
            parse_mode='HTML'
        )
        return

    safe_prompt = clean_prompt(prompt) if prompt != "/skip" else "natural motion"

    # Получаем модель и страхуемся от некорректного ключа.
    tariff = sheets_mgr.get_user_tariff(user_id)
    model_key = context.user_data.get('video_model') or "seedance-2.0"
    model_info = get_model_info(model_key)
    if not model_info:
        model_key = "seedance-2.0"
        model_info = get_model_info(model_key)
    model_name = model_info['name']

    await context.bot.send_chat_action(chat_id=user_id, action=ChatAction.RECORD_VIDEO)

    from config_video_models import calculate_cost
    estimated_cost = calculate_cost(model_key, 8)

    prefix = (
        f"⚠️ <i>Процесс генерации занимает от 2 до 5 минут.</i>\n"
        f"🎬 Модель: <b>{model_name}</b>\n"
        f"🖼 Режим: Image-to-Video\n"
        f"📐 Формат: <b>{aspect_ratio}</b>\n"
        f"💰 Примерная стоимость: <b>${estimated_cost:.3f}</b>\n\n"
    )

    msg = await context.bot.send_message(
        chat_id=user_id,
        text=f"{prefix}{get_wait_message('video')}",
        parse_mode='HTML'
    )

    loader = DynamicWaitMessage(msg, "video", prefix)
    loader.start()

    try:
        # Генерация через OpenRouter с выбранным форматом
        video_url = await video_router.generate_video(
            prompt=safe_prompt,
            model_key=model_key,
            tariff=tariff,
            source_image=image_path,
            duration=8,
            aspect_ratio=aspect_ratio  # Передаём выбранный формат
        )

        # ⚠️ ВРЕМЕННО ОТКЛЮЧЕНО для первого теста:
        # Fallback на KIE может вызвать двойное списание при временной ошибке OpenRouter
        # После успешного теста можно включить обратно

        # if not video_url:
        #     logger.warning(f"OpenRouter failed, trying KIE fallback...")
        #     kie_model = getattr(config, 'VIDEO_KLING_3', "kling-3-motion-control")
        #     video_url = await video_router.generate_video_kie_fallback(
        #         prompt=safe_prompt,
        #         model=kie_model,
        #         source_image=image_path
        #     )

    except Exception as e:
        logger.error(f"Image-to-video error: {e}", exc_info=True)
        video_url = None
    finally:
        loader.stop()

    if video_url:
        try:
            cost_credits = 15  # Image-to-video дороже
            footer = f"\n\n⚙️ {model_name} | 🖼➡️🎬 Image2Video | 📐 {aspect_ratio} | 🎫 {cost_credits} credits"
            caption_text = (
                f"🎬 <b>Video AI (Image-to-Video)</b>\n"
                f"Модель: <code>{model_name}</code>\n"
                f"Промпт: <i>{safe_prompt[:100]}...</i>"
                f"{footer}"
            )

            await context.bot.send_video(
                chat_id=user_id,
                video=video_url,
                caption=caption_text,
                parse_mode='HTML',
                reply_markup=get_post_video_generation_keyboard()
            )
            await msg.delete()

        except Exception as e:
            logger.error(f"Telegram Video Send Error: {e}")
            await msg.edit_text(
                f"✅ Видео сгенерировано.\n\n🔗 <b>Ссылка для скачивания:</b>\n{video_url}",
                parse_mode='HTML'
            )
    else:
        await msg.edit_text(
            "❌ <b>Сбой рендеринга.</b>\n\n"
            "Попробуйте другую модель или изображение.",
            parse_mode='HTML'
        )

    # Очистка временных данных
    context.user_data.pop('video_image_path', None)
    context.user_data.pop('video_image_prompt', None)
    context.user_data.pop('video_aspect_ratio', None)
