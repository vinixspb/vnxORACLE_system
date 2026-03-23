import os
import random
import uuid
import logging
import asyncio
import urllib.parse
import aiohttp
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes
import config
from loader import sheets_mgr
from keyboards.ai_image import get_post_generation_keyboard, get_photo_action_keyboard
from services.prompt_censor import clean_prompt
from services.kie_client import kie_studio 
from services.messages import get_wait_message, DynamicWaitMessage

logger = logging.getLogger(__name__)
DOWNLOADS_DIR = "downloads"
if not os.path.exists(DOWNLOADS_DIR):
    os.makedirs(DOWNLOADS_DIR)

async def generate_image(update: Update, context: ContextTypes.DEFAULT_TYPE, prompt: str, ratio: str = "vertical"):
    user_id = update.effective_user.id
    await context.bot.send_chat_action(chat_id=user_id, action=ChatAction.UPLOAD_PHOTO)
    
    img_model = context.user_data.get('img_model', config.IMG_POLLINATIONS)
    safe_prompt = clean_prompt(prompt)
    
    is_img2img = context.user_data.get('img2img_mode', False)
    source_path = context.user_data.get('img2img_source_path') if is_img2img else None
    
    context.user_data['img2img_mode'] = False
    context.user_data['img2img_source_path'] = None

    # 🔥 ВОЗВРАЩАЕМ QWEN: Теперь мы отправляем правильные форматы файлов, и Qwen будет работать идеально!
    if is_img2img and ("nano-banana" in img_model.lower() or "seedream" in img_model.lower() or "flux" in img_model.lower()):
        logger.info(f"🔄 Auto-Switch: Модель {img_model} перенаправлена на Qwen 2.0 (image-edit).")
        img_model = getattr(config, 'IMG_QWEN_2', "qwen-image-2")
    
    async def generate_pollinations_fallback(reason_text: str):
        logger.warning(f"⚠️ Fallback to Pollinations for user {user_id}. Reason: {reason_text}")
        if ratio == "vertical": w, h = 576, 1024
        elif ratio == "horizontal": w, h = 1024, 576
        else: w, h = 1024, 1024
            
        enhanced_prompt = f"{safe_prompt}, highly detailed, 8k, cinematic lighting"
        encoded_prompt = urllib.parse.quote(enhanced_prompt)
        seed = random.randint(1, 999999)
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?seed={seed}&width={w}&height={h}&nologo=true"
        
        caption_text = f"🎨 <b>Art by vnxORACLE</b>\nModel: <code>Pollinations (Fallback)</code>\nPrompt: {safe_prompt}\n\n⚠️ <i>Основная нейросеть временно недоступна, использован резерв.</i>"
        
        if is_img2img:
            caption_text += "\n\n⚠️ <i>Внимание: Режим редактирования фото недоступен в резервном режиме. Сгенерировано полностью новое изображение.</i>"
            
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url, timeout=aiohttp.ClientTimeout(total=20)) as resp:
                    if resp.status == 200:
                        image_data = await resp.read()
                        if hasattr(update, 'callback_query') and update.callback_query:
                            await context.bot.send_photo(chat_id=user_id, photo=image_data, caption=caption_text, reply_markup=get_post_generation_keyboard(), parse_mode='HTML')
                        else:
                            await update.message.reply_photo(photo=image_data, caption=caption_text, reply_markup=get_post_generation_keyboard(), parse_mode='HTML')
                    else:
                        raise Exception(f"HTTP Status {resp.status}")
        except Exception as e:
            logger.error(f"Pollinations Fallback Error: {e}")
            error_text = "⚠️ <b>Ошибка генерации.</b>\nК сожалению, основные нейросети перегружены, а резервная сеть отклонила запрос. Попробуйте перефразировать промпт."
            await context.bot.send_message(chat_id=user_id, text=error_text, parse_mode='HTML')

    if img_model == config.IMG_POLLINATIONS:
        return await generate_pollinations_fallback("User selected free model")

    wait_text = get_wait_message("image")
    if hasattr(update, 'callback_query') and update.callback_query:
        msg = await context.bot.send_message(chat_id=user_id, text=wait_text, parse_mode='HTML')
    else:
        msg = await update.message.reply_text(wait_text, parse_mode='HTML')
        
    loader = DynamicWaitMessage(msg, "image")
    loader.start()
    
    try:
        result_url, task_id = await kie_studio.generate_image(safe_prompt, img_model, ratio, source_image=source_path)
    finally:
        loader.stop()
    
    if result_url:
        mode_text = "Img2Img" if is_img2img else "Text2Img"
        caption = f"🎨 <b>Art by vnxORACLE</b>\nModel: <code>{img_model}</code>\nMode: {mode_text}\nRatio: {ratio}\nPrompt: {safe_prompt}"
        
        local_path = None
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(result_url) as resp:
                    if resp.status == 200:
                        # 🔥 ГЕНИАЛЬНЫЙ ФИКС: Читаем реальное расширение файла из URL, чтобы не обманывать сервер!
                        ext = "jpg"
                        try:
                            parsed_url = urllib.parse.urlparse(result_url)
                            file_ext = os.path.splitext(parsed_url.path)[1].replace('.', '').lower()
                            if file_ext in ['jpg', 'jpeg', 'png', 'webp']:
                                ext = file_ext
                        except: pass
                        
                        local_path = os.path.abspath(os.path.join(DOWNLOADS_DIR, f"gen_{user_id}_{uuid.uuid4().hex[:8]}.{ext}"))
                        with open(local_path, 'wb') as f:
                            f.write(await resp.read())
                        context.user_data['last_photo_path'] = local_path
                        context.user_data['last_photo_caption'] = safe_prompt
        except Exception as e:
            logger.error(f"❌ Ошибка скачивания сгенерированного фото: {e}")

        try:
            if local_path:
                with open(local_path, 'rb') as photo_to_send:
                    await context.bot.send_photo(
                        chat_id=user_id, photo=photo_to_send, caption=caption, 
                        reply_markup=get_post_generation_keyboard(), parse_mode='HTML'
                    )
            else:
                await context.bot.send_photo(
                    chat_id=user_id, photo=result_url, caption=caption, 
                    reply_markup=get_post_generation_keyboard(), parse_mode='HTML'
                )
            
            try: await msg.delete()
            except: pass
            
        except Exception as e:
            logger.error(f"Telegram Photo Send Error: {e}")
            await msg.edit_text(f"✅ Картинка готова, но Telegram не смог её загрузить.\nСсылка: {result_url}")
    else:
        try: await msg.delete() 
        except: pass
        await generate_pollinations_fallback(f"KIE Error 500 with model {img_model}")


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    mode = context.user_data.get('mode')
    
    photo = update.message.photo[-1]
    caption = update.message.caption or ""
    
    # Фото из Telegram всегда приходят в JPG, тут всё безопасно
    file = await context.bot.get_file(photo.file_id)
    path = os.path.abspath(os.path.join(DOWNLOADS_DIR, f"p_{user_id}_{uuid.uuid4().hex[:8]}.jpg"))
    await file.download_to_drive(path)

    if mode == 'openclaw_wait':
        from services.openclaw_core import claw_manager
        user_name = update.effective_user.first_name or "User"
        
        prefix = "🦞 <b>Агент изучает изображение...</b>\n"
        msg = await update.message.reply_text(f"{prefix}{get_wait_message('text')}", parse_mode='HTML')
        
        loader = DynamicWaitMessage(msg, "text", prefix)
        loader.start()
        
        try:
            injected_prompt = f"{caption}\n\n[SYSTEM: Пользователь прикрепил картинку. Путь: {path}. Опиши её или выполни задачу.]"
            response = await claw_manager.execute_task(injected_prompt, user_id, user_name)
        finally:
            loader.stop()
            
        try:
            await msg.edit_text(response, parse_mode='HTML')
        except:
            await update.message.reply_text(response, parse_mode='HTML')
        return

    elif mode == 'video_image_wait':
        context.user_data['last_photo_path'] = path
        context.user_data['last_photo_caption'] = caption
        await update.message.reply_text(get_wait_message("video"), parse_mode='HTML')
        return

    user_tariff = sheets_mgr.get_user_tariff(user_id)
    if user_tariff not in ['PRO', 'NEO']:
        return await update.message.reply_text("🧬 <b>VISION MODULE</b> доступен на уровнях PRO и NEO.", parse_mode='HTML')
        
    context.user_data['last_photo_path'] = path
    context.user_data['last_photo_caption'] = caption
    
    instruction_text = (
        "📸 <b>Изображение получено!</b>\n\n"
        "Выберите действие:\n"
        "👁 <b>Распознать (Vision)</b>\n"
        "🪄 <b>Редактировать (Img2Img)</b>\n"
        "✨ <b>Улучшить (Upscale)</b>"
    )
    if caption: instruction_text += f"\n\n<i>Ваш промпт: {caption}</i>"

    await update.message.reply_text(instruction_text, reply_markup=get_photo_action_keyboard(), parse_mode='HTML')


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    mode = context.user_data.get('mode')
    
    document = update.message.document
    caption = update.message.caption or "Изучи этот документ."
    
    raw_name = document.file_name if document.file_name else f"doc_{uuid.uuid4().hex[:6]}"
    safe_name = "".join(c for c in raw_name if c.isalnum() or c in " ._-")
    
    file = await context.bot.get_file(document.file_id)
    path = os.path.abspath(os.path.join(DOWNLOADS_DIR, f"d_{user_id}_{safe_name}"))
    await file.download_to_drive(path)

    if mode == 'openclaw_wait':
        from services.openclaw_core import claw_manager
        user_name = update.effective_user.first_name or "User"
        
        prefix = f"🦞 <b>Файл загружен. Агент анализирует данные...</b>\n"
        msg = await update.message.reply_text(f"{prefix}{get_wait_message('text')}", parse_mode='HTML')
        
        loader = DynamicWaitMessage(msg, "text", prefix)
        loader.start()
        
        try:
            injected_prompt = (
                f"{caption}\n\n"
                f"[SYSTEM COMMAND: Пользователь только что загрузил файл.\n"
                f"Имя: {safe_name}\n"
                f"Абсолютный путь: {path}\n"
                f"КРИТИЧЕСКОЕ ПРАВИЛО: НИКОГДА не выводи содержимое этого файла целиком в консоль (не используй cat или вывод всего текста). "
                f"Если это таблица (Excel/CSV/JSON) или большой документ, напиши и выполни Python-скрипт (например, с использованием pandas), "
                f"чтобы проанализировать данные локально, и выведи пользователю ТОЛЬКО готовый ответ, аналитику или запрошенную сумму!]"
            )
            response = await claw_manager.execute_task(injected_prompt, user_id, user_name)
        finally:
            loader.stop()
            
        try:
            await msg.edit_text(response, parse_mode='HTML')
        except:
            await update.message.reply_text(response, parse_mode='HTML')
    else:
        await update.message.reply_text(f"📁 <b>Файл сохранен:</b> {safe_name}\nЧтобы я мог сделать выжимку или аналитику, перейдите в меню 🦞 <b>OpenClaw</b> и отправьте его там.", parse_mode='HTML')
