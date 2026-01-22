import logging
import httpx
import os
from openai import OpenAI
import config

logger = logging.getLogger(__name__)

class AIEngine:
    def __init__(self):
        if not config.OPENROUTER_API_KEY:
            logger.error("❌ AI Engine: OPENROUTER_API_KEY не найден!")
            self.client = None
            return

        try:
            self.client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=config.OPENROUTER_API_KEY,
                http_client=httpx.Client(timeout=60.0)
            )
            logger.info("✅ AI Engine: Connected")
        except Exception as e:
            logger.error(f"❌ AI Engine Init Error: {e}")
            self.client = None

    async def get_response(self, messages, model):
        """Возвращает (текст_ответа, токены)"""
        if not self.client:
            return "⚠️ Ошибка: Модуль ИИ не инициализирован.", 0

        try:
            current_messages = list(messages)
            if not current_messages or current_messages[0].get('role') != 'system':
                current_messages.insert(0, {"role": "system", "content": config.SYSTEM_PROMPT})

            response = self.client.chat.completions.create(
                model=model,
                messages=current_messages,
                temperature=config.AI_TEMPERATURE,
                extra_headers={
                    "HTTP-Referer": "https://vnxmatrix.com", 
                    "X-Title": "vnxORACLE",
                }
            )
            
            answer = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if response.usage else 0

            return answer, tokens_used

        except Exception as e:
            logger.error(f"🧠 AI Request Error: {e}")
            return "⚠️ <b>CRITICAL ERROR:</b> Сбой связи с нейросетью.", 0

    async def transcribe_audio(self, file_path):
        """Переводит голос в текст (Whisper)"""
        if not self.client:
            return None
            
        try:
            # ВАЖНО: OpenRouter может не поддерживать endpoint audio/transcriptions.
            # Если здесь будет ошибка, придется использовать библиотеку SpeechRecognition или прямой ключ OpenAI.
            # Пока пробуем через стандартный интерфейс.
            with open(file_path, "rb") as audio_file:
                # Используем стандартный openai-whisper через API
                # Некоторые провайдеры на OpenRouter это поддерживают, но не все.
                # Если не сработает - бот напишет ошибку в лог.
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1", 
                    file=audio_file
                )
            return transcript.text
        except Exception as e:
            logger.error(f"🎤 Transcription Error: {e}")
            return None
