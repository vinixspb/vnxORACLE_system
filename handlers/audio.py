import os
import uuid
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ChatAction
from telegram.ext import ContextTypes
import config
from loader import sheets_mgr, ai_engine, audio_studio, db
from .chat import process_ai_request
from services.messages import get_wait_message  # 🔥 Интегрируем наши фразы

logger = logging.getLogger(__name__)
DOWNLOADS_DIR = "downloads"

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not sheets_mgr.get_user_tariff(user_id): 
        from .admin import send_paywall
        return await send_paywall(update)
    
    await context.bot.send_chat_action(chat_id=user_id, action=ChatAction.TYPING)
    if not os.path.exists(DOWNLOADS_DIR): os.makedirs(DOWNLOADS_DIR)
    
    # Генерируем уникальное имя файла
    file_path = os.path.join(DOWNLOADS_DIR, f"v_{user_id}_{uuid.uuid4().hex[:8]}.ogg")
    
    try:
        voice_file = await context.bot.get_file(update.message.voice.file_id)
        await voice_file.download_to_drive(file_path)
        transcript = await ai_engine.transcribe_audio(file_path)
        
        if transcript:
            await update.message.reply_text(f"🎤 <i>Распознано:</i> \"{transcript}\"", parse_mode='HTML')
            
            # 🔀 УМНАЯ МАРШРУТИЗАЦИЯ В ЗАВИСИМОСТИ ОТ РЕЖИМА
            mode = context.user_data.get('mode')
            
            if mode == 'openclaw_wait':
                # Перенаправляем голос в OpenClaw
                from services.openclaw_core import claw_manager
                user_name = update.effective_user.first_name or "User"
                
                # 🔥 Динамическая фраза ожидания
                wait_text = get_wait_message("text")
                msg = await update.message.reply_text(wait_text, parse_mode='HTML')
                
                # Запускаем агента с расшифрованным текстом
                response = await claw_manager.execute_task(transcript, user_id, user_name)
                
                # 🔥 Безопасное обновление статуса
                try:
                    await msg.edit_text(response, parse_mode='HTML')
                except Exception as e:
                    logger.warning(f"Voice OpenClaw edit error: {e}")
                    await update.message.reply_text(response, parse_mode='HTML')
                
            else:
                # Стандартный диалог с ИИ
                ai_input = f"[Audio Input]: {transcript}"
                await process_ai_request(update, context, ai_input)
                
        else:
            await update.message.reply_text("🎤 <b>Не удалось распознать голос.</b>", parse_mode='HTML')
    except Exception as e:
        logger.error(f"Voice Error: {e}")
        await update.message.reply_text("⚠️ Ошибка обработки голоса.")
    finally:
        if os.path.exists(file_path):
            try: os.remove(file_path)
            except: pass


async def handle_tts_request(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    user_id = update.effective_user.id
    voice = context.user_data.get('voice_id', config.DEFAULT_VOICE)
    await context.bot.send_chat_action(chat_id=user_id, action=ChatAction.RECORD_VOICE)
    
    # 🔥 Динамическая шутка для генерации аудио
    wait_text = get_wait_message("audio")
    msg = await update.message.reply_text(wait_text, parse_mode='HTML')
    
    audio_data, engine, is_fallback = await audio_studio.text_to_speech(text, voice)
    context.user_data['mode'] = None 
    
    # Жестко удаляем фразу ожидания
    try: await msg.delete()
    except: pass
    
    if audio_data:
        warn = "⚠️ <i>Резервный ИИ</i>\n" if is_fallback else ""
        caption = f"🎙 <b>Готово!</b>\n\n{warn}<blockquote>⚙️ {engine} | 🎫 {len(text)}</blockquote>"
        keyboard = [[InlineKeyboardButton("🎤 Озвучить еще", callback_data="audio_tts_again"), InlineKeyboardButton("💬 Вернуться в чат", callback_data="mode_chat_reset")]]
        
        await update.message.reply_audio(audio=audio_data, caption=caption, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))
        db.update_tokens(user_id, len(text))
    else:
        await update.message.reply_text("❌ Ошибка синтеза речи.")


async def handle_sfx_request(update: Update, context: ContextTypes.DEFAULT_TYPE, desc: str):
    user_id = update.effective_user.id
    await context.bot.send_chat_action(chat_id=user_id, action=ChatAction.RECORD_VOICE)
    
    # 🔥 Динамическая шутка для генерации SFX
    wait_text = get_wait_message("audio")
    msg = await update.message.reply_text(wait_text, parse_mode='HTML')
    
    sfx = await audio_studio.generate_sfx(desc)
    
    # Жестко удаляем фразу ожидания
    try: await msg.delete()
    except: pass
    
    if sfx:
        await update.message.reply_audio(audio=sfx, caption=f"🔊 <b>{desc}</b>", parse_mode='HTML')
    else:
        await update.message.reply_text("⚠️ Ошибка генерации звукового эффекта.")
