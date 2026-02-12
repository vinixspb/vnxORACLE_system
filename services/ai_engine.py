import logging
import base64
import os
from openai import AsyncOpenAI
import config

logger = logging.getLogger(__name__)

class AIEngine:
    def __init__(self):
        # 1. Инициализация Основного Интеллекта (LLM + Vision)
        # Мы используем универсальный клиент, который настраивается через config.py
        if not config.AI_API_KEY:
            logger.critical("❌ AI Engine: AI_API_KEY (KIA/OpenRouter) not found in config!")
            self.client_llm = None
        else:
            try:
                self.client_llm = AsyncOpenAI(
                    base_url=config.AI_BASE_URL,
                    api_key=config.AI_API_KEY,
                    timeout=60.0
                )
                logger.info(f"✅ AI Engine Connected: {config.AI_BASE_URL}")
            except Exception as e:
                logger.critical(f"❌ AI Engine Connection Failed: {e}")
                self.client_llm = None

        # 2. Инициализация Слухового Модуля (Whisper)
        # Отдельный клиент, так как Whisper часто живет на оригинальном OpenAI API
        if not config.OPENAI_API_KEY:
            logger.warning("⚠️ Whisper STT Disabled: OPENAI_API_KEY not found.")
            self.client_audio = None
        else:
            self.client_audio = AsyncOpenAI(api_key=config.OPENAI_API_KEY)
            logger.info("✅ Whisper STT Module Active")

    def _encode_image(self, image_path):
        """Кодирует изображение в base64 для Vision-запросов"""
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            logger.error(f"🖼 Image Encoding Error: {e}")
            return None

    async def get_response(self, messages, model, image_path=None):
        """
        Генерация ответа через нейросеть.
        Поддерживает: Текст, Контекст, Vision (Фото).
        """
        if not self.client_llm:
            return "⚠️ <b>SYSTEM ERROR:</b> Нейро-ядро не инициализировано. Обратитесь к Архитектору.", 0
        
        try:
            current_messages = list(messages)
            
            # Внедрение системной директивы (System Prompt)
            if not current_messages or current_messages[0].get('role') != 'system':
                current_messages.insert(0, {"role": "system", "content": config.SYSTEM_PROMPT})
            
            # Обработка Vision (Мультимодальность)
            if image_path and os.path.exists(image_path):
                base64_image = self._encode_image(image_path)
                if base64_image:
                    last_msg = current_messages[-1]
                    if last_msg['role'] == 'user':
                        # Формируем payload по стандарту OpenAI Vision
                        # ⚠️ ВНИМАНИЕ: Если KIA.AI не поддерживает этот формат, запрос упадет с 400 Bad Request
                        user_content = [
                            {"type": "text", "text": last_msg['content']},
                            {
                                "type": "image_url", 
                                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                            }
                        ]
                        current_messages[-1]['content'] = user_content
                        logger.info(f"🖼 Vision Request Prepared for model: {model}")

            # Запрос к API
            response = await self.client_llm.chat.completions.create(
                model=model,
                messages=current_messages,
                temperature=config.AI_TEMPERATURE, # Гибкая настройка из конфига
                extra_headers={
                    "HTTP-Referer": "https://vnxmatrix.com", 
                    "X-Title": "vnxORACLE",
                }
            )
            
            answer = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if response.usage else 0
            
            return answer, tokens_used
        
        except Exception as e:
            # Логируем полный трейс для админа
            logger.error(f"🧠 AI Request Critical Failure: {e}", exc_info=True)
            # Пользователю показываем безопасную заглушку
            return "⚠️ <b>CRITICAL ERROR:</b> Сбой нейронного интерфейса. Попробуйте позже.", 0

    async def transcribe_audio(self, file_path):
        """Преобразование голоса в текст (Whisper-1)"""
        if not self.client_audio: 
            return None
        
        try:
            with open(file_path, "rb") as audio_file:
                transcript = await self.client_audio.audio.transcriptions.create(
                    model="whisper-1", 
                    file=audio_file
                )
            return transcript.text
        except Exception as e:
            logger.error(f"🎤 Transcription Error: {e}")
            return None
