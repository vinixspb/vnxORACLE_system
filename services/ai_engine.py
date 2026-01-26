import logging
import base64
import os
from openai import AsyncOpenAI
import config

logger = logging.getLogger(__name__)

class AIEngine:
    def __init__(self):
        # 1. Основной клиент для текста и зрения (OpenRouter)
        if not config.OPENROUTER_API_KEY:
            logger.error("❌ AI Engine: OPENROUTER_API_KEY не найден!")
            self.client_llm = None
        else:
            try:
                self.client_llm = AsyncOpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=config.OPENROUTER_API_KEY,
                    timeout=60.0
                )
                logger.info("✅ AI Engine (OpenRouter Vision Support): Connected")
            except Exception as e:
                logger.error(f"❌ AI Engine Init Error: {e}")
                self.client_llm = None

        # 2. Клиент для голоса (Whisper)
        if not config.OPENAI_API_KEY:
            self.client_audio = None
        else:
            self.client_audio = AsyncOpenAI(api_key=config.OPENAI_API_KEY)

    def _encode_image(self, image_path):
        """Превращает картинку в base64 строку для передачи в API"""
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            logger.error(f"🖼 Image Encoding Error: {e}")
            return None

    async def get_response(self, messages, model, image_path=None):
        """
        Генерация ответа. Поддерживает текст и изображения.
        """
        if not self.client_llm:
            return "⚠️ Ошибка: Модуль LLM не инициализирован.", 0
        
        try:
            current_messages = list(messages)
            
            # Внедрение системного промпта
            if not current_messages or current_messages[0].get('role') != 'system':
                current_messages.insert(0, {"role": "system", "content": config.SYSTEM_PROMPT})
            
            # Если передано изображение, пересобираем последнее сообщение как мультимодальное
            if image_path and os.path.exists(image_path):
                base64_image = self._encode_image(image_path)
                if base64_image:
                    last_msg = current_messages[-1]
                    if last_msg['role'] == 'user':
                        # Формат контента для Vision-моделей (OpenRouter/OpenAI)
                        user_content = [
                            {"type": "text", "text": last_msg['content']},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                            }
                        ]
                        current_messages[-1]['content'] = user_content

            # Асинхронный вызов API
            response = await self.client_llm.chat.completions.create(
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
            logger.error(f"🧠 AI Vision/Text Request Error: {e}")
            return "⚠️ <b>CRITICAL ERROR:</b> Сбой нейронного интерфейса.", 0

    async def transcribe_audio(self, file_path):
        """Транскрибация Whisper (STT)"""
        if not self.client_audio: return None
        try:
            with open(file_path, "rb") as audio_file:
                transcript = await self.client_audio.audio.transcriptions.create(
                    model="whisper-1", file=audio_file
                )
            return transcript.text
        except Exception as e:
            logger.error(f"🎤 Transcription Error: {e}")
            return None
