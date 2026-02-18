import logging
import base64
import os
import aiohttp
from openai import AsyncOpenAI, APIStatusError
import config
import config_models
from services.model_name_check import find_best_replacement

logger = logging.getLogger(__name__)

class AIEngine:
    def __init__(self):
        self.clients = {}
        # Инициализация клиентов
        if config.KEY_START: self.clients["START"] = AsyncOpenAI(base_url=config.TEXT_BASE_URL, api_key=config.KEY_START)
        
        if config.KEY_PRO: self.clients["PRO"] = AsyncOpenAI(base_url=config.TEXT_BASE_URL, api_key=config.KEY_PRO)
        else: self.clients["PRO"] = self.clients.get("START")

        if config.KEY_NEO: self.clients["NEO"] = AsyncOpenAI(base_url=config.TEXT_BASE_URL, api_key=config.KEY_NEO)
        else: self.clients["NEO"] = self.clients.get("PRO") or self.clients.get("START")
        
        if config.OPENAI_API_KEY: self.client_audio = AsyncOpenAI(api_key=config.OPENAI_API_KEY)
        else: self.client_audio = None
        
        logger.info(f"✅ AI Clients Active: {list(self.clients.keys())}")

    async def _alert_admin(self, error_text):
        if not config.ADMIN_ID or not config.BOT_TOKEN_ORACLE: return
        try:
            url = f"https://api.telegram.org/bot{config.BOT_TOKEN_ORACLE}/sendMessage"
            payload = {"chat_id": config.ADMIN_ID, "text": f"🆘 <b>AI ALERT</b>\n{error_text}", "parse_mode": "HTML"}
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
        if not client: return "⚠️ Ошибка: Нет ключей.", 0

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

        # --- ПОПЫТКА 1 ---
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
            logger.warning(f"⚠️ AI Error {error_code}: {e}")

            # === УНИВЕРСАЛЬНАЯ ЛОГИКА ЛЕЧЕНИЯ (HEALING) ===
            new_model = None
            reason = ""
            need_force_free = False

            # 1. Диагностика проблемы
            if error_code in [404, 400]:
                reason = "Модель удалена/недоступна (404)"
                need_force_free = False # Попробуем найти аналог (даже платный, если был платный)
            
            elif error_code == 402:
                reason = "Нет средств (402)"
                need_force_free = True # СТРОГО ищем бесплатную
            
            elif error_code == 401:
                reason = "Ошибка авторизации провайдера (401)"
                need_force_free = True # Часто бывает у бесплатных провайдеров, лучше сменить

            # 2. Если проблема известна — лечим
            if reason:
                # Ищем замену
                new_model = await find_best_replacement(model, force_free=need_force_free)
                
                log_msg = f"⚠️ <b>{reason}</b>\nТариф: {user_tariff}\nЗамена: <code>{model}</code> ➡️ <code>{new_model}</code>"
                logger.warning(f"🩹 Healing Action: {model} -> {new_model}")
                await self._alert_admin(log_msg)

                try:
                    # ПОВТОРНЫЙ ЗАПРОС (RETRY)
                    response = await client.chat.completions.create(
                        model=new_model,
                        messages=current_messages,
                        extra_headers={"HTTP-Referer": "https://vnxmatrix.com", "X-Title": "vnxORACLE"}
                    )
                    answer = response.choices[0].message.content
                    answer += f"\n\n<i>(🛡 System Auto-Switch: {new_model.split('/')[-1]})</i>"
                    return answer, 0
                
                except Exception as ex2:
                    logger.error(f"❌ Healing failed: {ex2}")
                    return f"⚠️ Система перегружена (Все каналы заняты).\nКод ошибки: {error_code}", 0

            return f"⚠️ Ошибка провайдера: {e.message}", 0
            
        except Exception as e:
            logger.error(f"🧠 Unknown Error: {e}")
            return "⚠️ Неизвестная ошибка.", 0

    async def transcribe_audio(self, file_path):
        if not self.client_audio: return None
        try:
            with open(file_path, "rb") as audio_file:
                transcript = await self.client_audio.audio.transcriptions.create(model="whisper-1", file=audio_file)
            return transcript.text
        except: return None
