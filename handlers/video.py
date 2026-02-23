import logging
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes
from services.kie_client import kie_studio
from loader import sheets_mgr

logger = logging.getLogger(__name__)

async def ask_video_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE, video_type: str):
    """
    Перехватывает нажатие кнопок из подменю "Видео Ai"
    """
    query = update.callback_query
    await query.answer()

    if video_type == "text":
        context.user_data['mode'] = 'video_text_wait'
        text = "📝 <b>Режиссерская: Текст в Видео</b>\n\nОпишите сцену максимально подробно. Нейросеть лучше всего понимает запросы на <b>английском языке</b>.\n\n<i>Например: A cinematic drone shot of a futuristic cyberpunk city at night, neon lights...</i>"
    elif video_type == "image":
        context.user_data['mode'] = 'video_image_wait'
        text = "🖼 <b>Режиссерская: Картинка в Видео</b>\n\nПожалуйста, отправьте мне фотографию или изображение, которое вы хотите 'оживить'."

    await query.edit_message_text(text, parse_mode='HTML')


async def handle_video_text_request(update: Update, context: ContextTypes.DEFAULT_TYPE, prompt: str):
    """
    Обработка текстового промпта и запуск рендеринга видео
    """
    user_id = update.effective_user.id
    context.user_data['mode'] = None # Сбрасываем режим

    # 🛡 Защита: Видео — дорогой процесс, пускаем только PRO и NEO
    tariff = sheets_mgr.get_user_tariff(user_id)
    if tariff not in ['PRO', 'NEO']:
        await update.message.reply_text("🎬 <b>Модуль Видео Ai</b> доступен только на тарифах PRO и NEO.", parse_mode='HTML')
        return

    # Уведомляем пользователя, что процесс долгий
    msg = await update.message.reply_text(
        "⏳ <i>Режиссерская хлопушка! Нейросеть начала рендеринг видео...</i>\n\n"
        "⚠️ <b>Внимание:</b> Процесс генерации видео занимает от 2 до 5 минут. Пожалуйста, не отправляйте новые запросы, пока видео не будет готово.", 
        parse_mode='HTML'
    )
    await context.bot.send_chat_action(chat_id=user_id, action=ChatAction.RECORD_VIDEO)

    # Запускаем генерацию (По умолчанию будем использовать Kling 3.0 или Grok)
    # В следующей итерации мы научим kie_client понимать Kling и Hailuo
    model = "grok-imagine/text-to-video" 
    video_url = await kie_studio.generate_video(prompt=prompt, model=model)

    if video_url:
        try:
            # Отправляем именно как ВИДЕО
            await context.bot.send_video(
                chat_id=user_id,
                video=video_url,
                caption=f"🎬 <b>Video Ai</b>\nМодель: <code>{model}</code>\nПромпт: <i>{prompt[:100]}...</i>",
                parse_mode='HTML'
            )
            await msg.delete()
        except Exception as e:
            logger.error(f"Telegram Video Send Error: {e}")
            await msg.edit_text(f"✅ Видео сгенерировано, но Telegram не смог его загрузить (возможно, слишком большой размер).\n🔗 Ссылка для скачивания: {video_url}")
    else:
        await msg.edit_text("❌ <b>Сбой рендеринга.</b>\nНейросеть отклонила запрос или время ожидания истекло.", parse_mode='HTML')
