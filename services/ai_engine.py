import logging
import httpx
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
        """
        Возвращает кортеж: (текст_ответа, количество_токенов)
        """
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
            
            # Считаем токены (если API их вернул)
            tokens_used = 0
            if response.usage:
                tokens_used = response.usage.total_tokens

            return answer, tokens_used

        except Exception as e:
            logger.error(f"🧠 AI Request Error: {e}")
            return "⚠️ <b>CRITICAL ERROR:</b> Сбой связи с нейросетью.", 0
