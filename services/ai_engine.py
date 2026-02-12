import logging
import base64
import os
import aiohttp # Для отправки алерта админу без циклического импорта бота
from openai import AsyncOpenAI, APIStatusError
import config
import config_models # Наш новый реестр

logger = logging.getLogger(__name__)

class AIEngine:
    def __init__(self):
        # ... (Инициализация такая же, как была раньше) ...
        # (Просто скопируй блок __init__ из предыдущей версии ai_engine.py)
        if config.KIE_API_KEY:
             self.client_llm = AsyncOpenAI(base_url="https://api.kie.ai/v1", api_key=config.KIE_API_KEY)
        elif config.OPENROUTER_API_KEY:
             self.client_llm = AsyncOpenAI(base_url="https://openrouter.ai/api/v1", api_key=config.OPENROUTER_API_KEY)
        else:
             self.client_llm = None
        
        if config.OPENAI_API_KEY:
            self.client_audio = AsyncOpenAI(api_key=config.OPENAI_API_KEY)
        else:
            self.client_audio = None

    async def _alert_admin(self, error_text):
        """Тихая отправка уведомления Архитектору (через прямой запрос к API Telegram)"""
        if not config.ADMIN_ID or not config.BOT_TOKEN_ORACLE: return
        try:
            url = f"https://api.telegram.org/bot{config.BOT_TOKEN_ORACLE}/sendMessage"
            payload = {
                "chat_id": config.ADMIN_ID,
                "text": f"🆘 <b>SYSTEM ALERT: AI FAILURE</b>\n\nПричина: {error_text}\n\n<i>Система автоматически переключилась на резервный канал.</i>",
                "parse_mode": "HTML"
            }
            async with aiohttp.ClientSession() as session:
                await session.post(url, json=payload)
        except:
            pass # Если не удалось отправить алерт, не роняем бота

    # ... (метод _encode_image оставляем как был) ...
    def _encode_image(self, image_path):
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except: return None

    async def get_response(self, messages, model, image_path=None):
        if not self.client_llm:
            return "⚠️ Ошибка: Нейро-ядро отключено.", 0
        
        # Подготовка сообщений (System Prompt + Vision)
        # (Код подготовки messages идентичен предыдущей версии - скопируй его или оставь)
        current_messages = list(messages)
        if not current_messages or current_messages[0].get('role') != 'system':
            current_messages.insert(0, {"role": "system", "content": config.SYSTEM_PROMPT})
        
        # Vision logic (shortened for brevity here, assume same as before)
        if image_path and os.path.exists(image_path):
             # ... (код vision) ...
             pass

        try:
            # ПОПЫТКА 1: Основной запрос
            response = await self.client_llm.chat.completions.create(
                model=model,
                messages=current_messages,
                temperature=config.AI_TEMPERATURE,
                extra_headers={"HTTP-Referer": "https://vnxmatrix.com", "X-Title": "vnxORACLE"}
            )
            return response.choices[0].message.content, response.usage.total_tokens

        except APIStatusError as e:
            # ПЕРЕХВАТ ОШИБОК (402 = Нет денег, 401 = Ошибка ключа, 5xx = Сервер упал)
            error_code = e.status_code
            logger.error(f"⚠️ AI API Error {error_code}: {e}")

            if error_code in [402, 401, 403, 429, 500, 502, 503]:
                # 1. Шлем сигнал админу
                await self._alert_admin(f"API Error {error_code}: {e.message}")
                
                # 2. Переключаемся на бесплатную модель
                logger.warning(f"🔄 Switching to Fallback Model: {config_models.FALLBACK_MODEL}")
                try:
                    fallback_resp = await self.client_llm.chat.completions.create(
                        model=config_models.FALLBACK_MODEL,
                        messages=current_messages
                    )
                    # Добавляем пометку пользователю
                    answer = fallback_resp.choices[0].message.content
                    answer += f"\n\n<i>(⚠️ Сбой основного канала. Ответ сгенерирован {config_models.FALLBACK_NAME})</i>"
                    return answer, 0
                except Exception as ex:
                    logger.critical(f"❌ Fallback failed too: {ex}")
                    return "⚠️ <b>CRITICAL SYSTEM FAILURE</b>\nИ основной, и резервный каналы недоступны.", 0
            
            # Если ошибка другая (например, 400 Bad Request из-за кривого промпта) — пробрасываем
            return f"⚠️ Ошибка запроса: {e.message}", 0
            
        except Exception as e:
            logger.error(f"🧠 Unknown AI Error: {e}")
            return "⚠️ Неизвестная ошибка нейросети.", 0

    # ... (метод transcribe_audio оставляем как был) ...
    async def transcribe_audio(self, file_path):
        if not self.client_audio: return None
        try:
            with open(file_path, "rb") as audio_file:
                transcript = await self.client_audio.audio.transcriptions.create(model="whisper-1", file=audio_file)
            return transcript.text
        except: return None
