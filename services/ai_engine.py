import logging
import httpx
from openai import OpenAI
import config

logger = logging.getLogger(__name__)

class AIEngine:
    def __init__(self):
        """
        Инициализация подключения к OpenRouter.
        Используем библиотеку OpenAI, но меняем base_url.
        """
        if not config.OPENROUTER_API_KEY:
            logger.error("❌ AI Engine: OPENROUTER_API_KEY не найден в конфиге!")
            self.client = None
            return

        try:
            # Настраиваем клиент с таймаутом 60 сек (нейронки иногда тупят)
            self.client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=config.OPENROUTER_API_KEY,
                http_client=httpx.Client(timeout=60.0)
            )
            logger.info("✅ AI Engine: Connected to OpenRouter")
        except Exception as e:
            logger.error(f"❌ AI Engine Init Error: {e}")
            self.client = None

    async def get_response(self, messages, model):
        """
        Отправляет запрос в нейросеть.
        :param messages: Список сообщений [{'role': 'user', 'content': '...'}, ...]
        :param model: Имя модели (например 'openai/gpt-4o')
        :return: Текст ответа
        """
        if not self.client:
            return "⚠️ Ошибка: Модуль ИИ не инициализирован (нет ключа)."

        try:
            # 1. Проверяем, есть ли Системный Промпт в начале истории
            # Если нет - добавляем (это личность бота)
            current_messages = list(messages) # Делаем копию, чтобы не менять оригинал
            if not current_messages or current_messages[0].get('role') != 'system':
                current_messages.insert(0, {"role": "system", "content": config.SYSTEM_PROMPT})

            # 2. Отправляем запрос
            response = self.client.chat.completions.create(
                model=model,
                messages=current_messages,
                temperature=config.AI_TEMPERATURE,
                # OpenRouter просит эти заголовки для статистики
                extra_headers={
                    "HTTP-Referer": "https://vnxmatrix.com", 
                    "X-Title": "vnxORACLE",
                }
            )
            
            # 3. Извлекаем ответ
            answer = response.choices[0].message.content
            return answer

        except Exception as e:
            logger.error(f"🧠 AI Request Error: {e}")
            return "⚠️ <b>CRITICAL ERROR:</b> Сбой связи с нейросетью. Попробуйте позже."
          
