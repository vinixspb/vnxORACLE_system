import os
import uuid
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ChatAction
from telegram.ext import ContextTypes
import config
from loader import sheets_mgr, ai_engine, audio_studio, db
from .chat import process_ai_request

logger = logging.getLogger(__name__)
DOWNLOADS_DIR = "downloads"

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not sheets_mgr.get_user_tariff(user_id): 
        from .admin import send_paywall
        return await send_paywall(update)
    
    await context.bot.send_chat_action(chat_id=user_id, action=ChatAction.TYPING)
    if not os.path.exists(DOWNLOADS_DIR): os.makedirs(DOWNLOADS_DIR)
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
                
                msg = await update.message.reply_text("🦞 <i>Агент принял голосовое поручение. Выполняю...</i>", parse_mode='HTML')
                
                # Запускаем агента с расшифрованным текстом
                response = await claw_manager.execute_task(transcript, user_id, user_name)
                
                await msg.edit_text(response, parse_mode='HTML')
                
            else:
                # Стандартный диалог с ChatGPT (если нет других режимов)
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

# ... (остальные функции handle_tts_request и handle_sfx_request остаются без изменений)
