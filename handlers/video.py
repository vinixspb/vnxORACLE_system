import logging
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes
from services.kie_client import kie_studio
from loader import sheets_mgr
from services.prompt_censor import is_prompt_safe, clean_prompt
import config
from services.messages import get_wait_message, DynamicWaitMessage

logger = logging.getLogger(__name__)

async def ask_video_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE, video_type: str):
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
    user_id = update.effective_user.id
    context.user_data['mode'] = None 

    if not is_prompt_safe(prompt):
        await update.message.reply_text(
            "🔞 <b>Запрос отклонен цензурой.</b>\nСистема безопасности заблокировала генерацию. Я не создаю откровенный, NSFW (18+) или жестокий контент. Пожалуйста, измените описание.",
            parse_mode='HTML'
        )
        return

    safe_api_prompt = clean_prompt(prompt)

    tariff = sheets_mgr.get_user_tariff(user_id)
    if tariff not in ['PRO', 'NEO']:
        await update.message.reply_text("🎬 <b>Модуль Видео Ai</b> доступен только на тарифах PRO и NEO.", parse_mode='HTML')
        return

    await context.bot.send_chat_action(chat_id=user_id, action=ChatAction.RECORD_VIDEO)

    prefix = "⚠️ <i>Процесс генерации занимает от 2 до 5 минут.</i>\n\n"
    msg = await update.message.reply_text(f"{prefix}{get_wait_message('video')}", parse_mode='HTML')
    
    loader = DynamicWaitMessage(msg, "video", prefix)
    loader.start()

    try:
        model = getattr(config, 'VIDEO_KLING_3', "kling-3-motion-control") 
        video_url = await kie_studio.generate_video(prompt=safe_api_prompt, model=model)
    finally:
        loader.stop()

    if video_url:
        try:
            cost_credits = 10 
            footer = f"\n\n⚙️ {model} | 🎬 Video Ai | 🎫 {cost_credits} credits"
            caption_text = f"🎬 <b>Video Ai</b>\nПромпт: <i>{safe_api_prompt[:100]}...</i>{footer}"
            
            await context.bot.send_video(
                chat_id=user_id,
                video=video_url,
                caption=caption_text,
                parse_mode='HTML'
            )
            await msg.delete()
        except Exception as e:
            logger.error(f"Telegram Video Send Error: {e}")
            await msg.edit_text(f"✅ Видео сгенерировано, но Telegram не смог его загрузить (возможно, слишком большой размер).\n🔗 Ссылка для скачивания: {video_url}")
    else:
        await msg.edit_text("❌ <b>Сбой рендеринга.</b>\nНейросеть отклонила запрос или время ожидания истекло.", parse_mode='HTML')
