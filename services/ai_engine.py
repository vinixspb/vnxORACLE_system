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
        self.clients = {}
        
        # 1. Инициализация клиентов (Кошельков)
        # Если какой-то ключ не задан, используем более дешевый тариф как запасной вариант
        
        # START Client
        if config.KEY_START:
            self.clients["START"] = AsyncOpenAI(base_url=config.TEXT_BASE_URL, api_key=config.KEY_START)
        
        # PRO Client (fallback -> START)
        if config.KEY_PRO:
            self.clients["PRO"] = AsyncOpenAI(base_url=config.TEXT_BASE_URL, api_key=config.KEY_PRO)
        else:
            self.clients["PRO"] = self.clients.get("START")

        # NEO Client (fallback -> PRO -> START)
        if config.KEY_NEO:
            self.clients["NEO"] = AsyncOpenAI(base_url=config.TEXT_BASE_URL, api_key=config.KEY_NEO)
        else:
            self.clients["NEO"] = self.clients.get("PRO") or self.clients.get("START")

        # Audio Client (Whisper) - прямой OpenAI
        if config.OPENAI_API_KEY:
            self.client_audio = AsyncOpenAI(api_key=config.OPENAI_API_KEY)
        else:
            self.client_audio = None
            
        logger.info(f"✅ AI Engine Initialized. Active Clients keys: {list(self.clients.keys())}")

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

    def _get_client(self, tariff):
        """Выбирает клиента в зависимости от тарифа пользователя"""
        client = self.clients.get(tariff)
        if not client:
            # Fallback на START, если вдруг пришел неизвестный тариф
            return self.clients.get("START")
        return client

    def _encode_image(self, image_path):
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except: return None

    async def get_response(self, messages, model, user_tariff="START", image_path=None):
        """
        user_tariff: Определяет, какой API-ключ (кошелек) будет использован
        """
        # 1. Выбираем кошелек (Client)
        client = self._get_client(user_tariff)
        
        if not client:
            return "⚠️ Ошибка: Нет доступных AI-ключей. Обратитесь к админу.", 0

        # 2. Подготовка сообщений (System Prompt)
        current_messages = list(messages)
        if not current_messages or current_messages[0].get('role') != 'system':
            current_messages.insert(0, {"role": "system", "content": config.SYSTEM_PROMPT})
        
        # 3. Vision logic (Обработка картинок)
        if image_path and os.path.exists(image_path):
            base64_image = self._encode_image(image_path)
            if base64_image:
                last_msg = current_messages[-1]
                if last_msg['role'] == 'user':
                    current_messages[-1]['content'] = [
                        {"type": "text", "text": last_msg['content']},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]

        try:
            # ПОПЫТКА 1: Основной запрос через клиент тарифа
            response = await client.chat.completions.create(
                model=model,
                messages=current_messages,
                temperature=config.AI_TEMPERATURE,
                extra_headers={
                    "HTTP-Referer": "https://vnxmatrix.com",
                    "X-Title": "vnxORACLE",
                }
            )
            return response.choices[0].message.content, response.usage.total_tokens

        except APIStatusError as e:
            # ПЕРЕХВАТ ОШИБОК (402 = Нет денег, 401 = Ошибка ключа, 5xx = Сервер упал)
            error_code = e.status_code
            logger.error(f"⚠️ AI API Error {error_code} (Tariff: {user_tariff}): {e}")

            if error_code in [402, 401, 403, 429, 500, 502, 503]:
                # 1. Шлем сигнал админу
                await self._alert_admin(f"API Error {error_code} on tariff {user_tariff}: {e.message}")
                
                # 2. Переключаемся на бесплатную модель (Fallback)
                # Используем тот же клиент (надеемся, что бесплатная модель сработает даже при 0 балансе)
                # или fallback клиент, если упал сервер
                logger.warning(f"🔄 Switching to Fallback Model: {config_models.FALLBACK_MODEL}")
                try:
                    fallback_resp = await client.chat.completions.create(
                        model=config_models.FALLBACK_MODEL,
                        messages=current_messages,
                        extra_headers={"HTTP-Referer": "https://vnxmatrix.com", "X-Title": "vnxORACLE"}
                    )
                    # Добавляем пометку пользователю
                    answer = fallback_resp.choices[0].message.content
                    answer += f"\n\n<i>(⚠️ Сбой основного канала. Ответ сгенерирован {config_models.FALLBACK_NAME})</i>"
                    return answer, 0
                except Exception as ex:
                    logger.critical(f"❌ Fallback failed too: {ex}")
                    return "⚠️ <b>CRITICAL SYSTEM FAILURE</b>\nИ основной, и резервный каналы недоступны.", 0
            
            # Если ошибка другая (например, 400 Bad Request) — пробрасываем текст
            return f"⚠️ Ошибка запроса: {e.message}", 0
            
        except Exception as e:
            logger.error(f"🧠 Unknown AI Error: {e}")
            return "⚠️ Неизвестная ошибка нейросети.", 0

    async def transcribe_audio(self, file_path):
        if not self.client_audio: return None
        try:
            with open(file_path, "rb") as audio_file:
                transcript = await self.client_audio.audio.transcriptions.create(model="whisper-1", file=audio_file)
            return transcript.text
        except: return None
