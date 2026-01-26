import logging
import os
from openai import AsyncOpenAI
import config

logger = logging.getLogger(__name__)

class AIEngine:
    def __init__(self):
        # 1. Клиент для Текста (LLM) -> OpenRouter
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
                logger.info("✅ AI Engine (OpenRouter): Connected")
            except Exception as e:
                logger.error(f"❌ AI Engine Init Error: {e}")
                self.client_llm = None

        # 2. Клиент для Голоса (Whisper) -> OpenAI Direct
        if not config.OPENAI_API_KEY:
            logger.warning("⚠️ OPENAI_API_KEY не найден - голосовые будут недоступны")
            self.client_audio = None
        else:
            try:
                self.client_audio = AsyncOpenAI(
                    api_key=config.OPENAI_API_KEY,
                    timeout=60.0
                )
                logger.info("✅ Whisper Engine (OpenAI): Connected")
            except Exception as e:
                logger.error(f"❌ Whisper Init Error: {e}")
                self.client_audio = None

    async def get_response(self, messages, model):
        """Генерация текста через OpenRouter (async)"""
        if not self.client_llm:
            return "⚠️ Ошибка: Модуль LLM не инициализирован.", 0
        
        try:
            current_messages = list(messages)
            # Добавляем системный промпт, если его нет
            if not current_messages or current_messages[0].get('role') != 'system':
                current_messages.insert(0, {"role": "system", "content": config.SYSTEM_PROMPT})
            
            # Асинхронный вызов
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
            logger.error(f"🧠 AI Request Error: {e}")
            return "⚠️ <b>CRITICAL ERROR:</b> Сбой связи с нейросетью.", 0

    async def transcribe_audio(self, file_path):
        """Транскрибация через OpenAI Whisper (async)"""
        if not self.client_audio:
            logger.error("🎤 Whisper client (OpenAI Key) not initialized")
            return None
            
        try:
            # Асинхронная отправка файла
            with open(file_path, "rb") as audio_file:
                transcript = await self.client_audio.audio.transcriptions.create(
                    model="whisper-1", 
                    file=audio_file
                )
            
            logger.info(f"✅ Transcription: {len(transcript.text)} chars")
            return transcript.text
        
        except Exception as e:
            logger.error(f"🎤 Transcription Error: {e}")
            return None
