import logging
import base64
import os
import aiohttp
from openai import AsyncOpenAI, APIStatusError
import config
import config_models

# Импортируем из НОВОГО файла
from services.model_name_check import find_best_replacement

logger = logging.getLogger(__name__)

class AIEngine:
    def __init__(self):
        self.clients = {}
        
        # Инициализация клиентов
        if config.KEY_START:
            self.clients["START"] = AsyncOpenAI(base_url=config.TEXT_BASE_URL, api_key=config.KEY_START)
        
        if config.KEY_PRO:
            self.clients["PRO"] = AsyncOpenAI(base_url=config.TEXT_BASE_URL, api_key=config.KEY_PRO)
        else:
            self.clients["PRO"] = self.clients.get("START")

        if config.KEY_NEO:
            self.clients["NEO"] = AsyncOpenAI(base_url=config.TEXT_BASE_URL, api_key=config.KEY_NEO)
        else:
            self.clients["NEO"] = self.clients.get("PRO") or self.clients.get("START")

        if config.OPENAI_API_KEY:
            self.client_audio = AsyncOpenAI(api_key=config.OPENAI_API_KEY)
        else:
            self.client_audio = None
            
        logger.info(f"✅ AI Engine Initialized. Active Clients: {list(self.clients.keys())}")

    async def _alert_admin(self, error_text):
        if not config.ADMIN_ID or not config.BOT_TOKEN_ORACLE: return
        try:
            url = f"https://api.telegram.org/bot{config.BOT_TOKEN_ORACLE}/sendMessage"
            payload = {
                "chat_id": config.ADMIN_ID,
                "text": f"🆘 <b>SYSTEM ALERT: AI HEALING</b>\n\n{error_text}",
                "parse_mode": "HTML"
            }
            async with aiohttp.ClientSession() as session:
                await session.post(url, json=payload)
        except: pass

    def _get_client(self, tariff):
        client = self.clients.get(tariff)
        if not client: return self.clients.get("START")
        return client

    def _encode_image(self, image_path):
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except: return None

    async def get_response(self, messages, model, user_tariff="START", image_path=None):
        client = self._get_client(user_tariff)
        if not client: return "⚠️ Ошибка: Нет доступных AI-ключей.", 0

        current_messages = list(messages)
        if not current_messages or current_messages[0].get('role') != 'system':
            current_messages.insert(0, {"role": "system", "content": config.SYSTEM_PROMPT})
        
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
            response = await client.chat.completions.create(
                model=model,
                messages=current_messages,
                temperature=config.AI_TEMPERATURE,
                extra_headers={"HTTP-Referer": "https://vnxmatrix.com", "X-Title": "vnxORACLE"}
            )
            return response.choices[0].message.content, response.usage.total_tokens

        except APIStatusError as e:
            error_code = e.status_code
            error_msg = str(e).lower() # Приводим к нижнему регистру для поиска
            
            logger.warning(f"⚠️ AI Error {error_code}: {e}")

            # === ЛОГИКА САМОИСЦЕЛЕНИЯ (SELF-HEALING) ===
            # Ловим 404/400.
            # Добавил проверку на 'endpoints', так как OpenRouter пишет "No endpoints found"
            is_model_error = (
                error_code in [404, 400] and 
                ("model" in error_msg or "endpoint" in error_msg or "found" in error_msg)
            )

            if is_model_error:
                # 1. Ищем замену
                new_model = await find_best_replacement(model)
                logger.warning(f"🩹 Healing: Replacing dead model {model} -> {new_model}")
                
                # 2. Уведомляем админа
                await self._alert_admin(f"Модель <code>{model}</code> недоступна.\nОшибка: {e}\n\n♻️ <b>Auto-Healing:</b> Заменяю на <code>{new_model}</code>")

                try:
                    # 3. Повторяем запрос с НОВОЙ моделью
                    response = await client.chat.completions.create(
                        model=new_model,
                        messages=current_messages,
                        temperature=config.AI_TEMPERATURE,
                        extra_headers={"HTTP-Referer": "https://vnxmatrix.com", "X-Title": "vnxORACLE"}
                    )
                    
                    answer = response.choices[0].message.content
                    answer += f"\n\n<i>(🛠 Auto-switch: {new_model.split('/')[-1]})</i>"
                    
                    return answer, response.usage.total_tokens

                except Exception as ex_heal:
                    logger.error(f"❌ Healing failed: {ex_heal}")
                    return "⚠️ Сбой системы восстановления. Попробуйте выбрать другую модель в меню.", 0
            
            # Если денег нет (402)
            if error_code == 402:
                 try:
                    await self._alert_admin(f"💰 Закончился бюджет на тарифе {user_tariff}!")
                    response = await client.chat.completions.create(
                        model="mistralai/mistral-7b-instruct:free",
                        messages=current_messages
                    )
                    return response.choices[0].message.content + "\n\n<i>(⚠️ Low Budget Mode)</i>", 0
                 except: pass

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
