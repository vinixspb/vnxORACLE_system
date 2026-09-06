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
        
        # ЛОГИРУЕМ КЛЮЧИ (Скрыто) - Проверь это в логах при старте!
        def check(k): return "OK" if k and len(k) > 10 else "MISSING"
        logger.info(f"🔑 Keys Status: START={check(config.KEY_START)} | PRO={check(config.KEY_PRO)}")

        if config.KEY_START: self.clients["START"] = AsyncOpenAI(base_url=config.TEXT_BASE_URL, api_key=config.KEY_START)
        if config.KEY_PRO: self.clients["PRO"] = AsyncOpenAI(base_url=config.TEXT_BASE_URL, api_key=config.KEY_PRO)
        else: self.clients["PRO"] = self.clients.get("START")
        if config.KEY_NEO: self.clients["NEO"] = AsyncOpenAI(base_url=config.TEXT_BASE_URL, api_key=config.KEY_NEO)
        else: self.clients["NEO"] = self.clients.get("PRO") or self.clients.get("START")
        
        if config.OPENAI_API_KEY: self.client_audio = AsyncOpenAI(api_key=config.OPENAI_API_KEY)
        else: self.client_audio = None

    async def _alert_admin(self, error_text):
        if not config.ADMIN_ID or not config.BOT_TOKEN_ORACLE: return
        try:
            url = f"https://api.telegram.org/bot{config.BOT_TOKEN_ORACLE}/sendMessage"
            payload = {"chat_id": config.ADMIN_ID, "text": f"🆘 <b>AI SURVIVAL</b>\n{error_text}", "parse_mode": "HTML"}
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
        if not client: return "⚠️ Ошибка системы: Нет ключей.", 0, model

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

        # =================================================
        # 🛡 SURVIVAL LOOP (5 Попыток)
        # =================================================
        max_retries = 5
        attempt = 0
        current_model = model
        blacklist = [] 
        bad_brands = [] # Бренды, которые мы забаним в рамках этого запроса
        
        while attempt < max_retries:
            attempt += 1
            try:
                # Включаем детальный лог только при сбоях
                if attempt > 1: logger.warning(f"🔄 Try {attempt}/{max_retries}: {current_model}")
                
                response = await client.chat.completions.create(
                    model=current_model,
                    messages=current_messages,
                    temperature=config.AI_TEMPERATURE,
                    extra_headers={"HTTP-Referer": "https://vnxmatrix.com", "X-Title": "vnxORACLE"}
                )
                
                answer = response.choices[0].message.content
                if current_model != model:
                    logger.info(f"🛡 Auto-Switch: {model} -> {current_model}")
                return answer, response.usage.total_tokens, current_model

            except APIStatusError as e:
                error_code = e.status_code
                error_msg = str(e).lower()
                logger.warning(f"⚠️ Fail {attempt} ({current_model}): {error_code} - {e}")
                
                blacklist.append(current_model)

                # --- АНАЛИЗ ---
                force_free = False
                
                # 1. Ошибка "Cookie" или 401 на бесплатных моделях -> БАНИМ ВЕСЬ БРЕНД
                if "cookie" in error_msg or "auth" in error_msg or error_code == 401:
                    force_free = True
                    # Если упал Google/Gemma - баним все гугловское
                    if "google" in current_model or "gemma" in current_model or "gemini" in current_model:
                        bad_brands.extend(["google", "gemini", "gemma"])
                        logger.warning("🚫 Banning Google/Gemini due to cookie error")
                    
                    # Если упал Stepfun
                    if "step" in current_model:
                        bad_brands.append("step")

                # 2. Нет денег (402)
                elif error_code == 402:
                    force_free = True
                    # Если 402 упал на GPT-4o, значит весь OpenAI платный недоступен
                    if "openai" in current_model or "gpt" in current_model:
                        bad_brands.extend(["openai", "gpt"])

                if attempt >= max_retries:
                    logger.error("❌ Survival Loop Failed.")
                    return "⚠️ <b>Все каналы перегружены.</b>\nПовторите запрос позже или выберите другую модель.", 0, current_model

                # Ищем замену, передавая список забаненных брендов
                new_model = await find_best_replacement(
                    current_model, 
                    force_free=force_free, 
                    excluded_models=blacklist,
                    excluded_brands=bad_brands # <--- ВАЖНО
                )
                
                if attempt == 1:
                    await self._alert_admin(f"⚠️ Swap: {current_model} -> {new_model} (Err: {error_code})")
                
                current_model = new_model
                continue

            except Exception as e:
                logger.error(f"Critical: {e}")
                return "⚠️ Критическая ошибка.", 0, current_model

        return "⚠️ Нет ответа.", 0, current_model

    async def transcribe_audio(self, file_path):
        if not self.client_audio: return None
        try:
            with open(file_path, "rb") as audio_file:
                transcript = await self.client_audio.audio.transcriptions.create(model="whisper-1", file=audio_file)
            return transcript.text
        except: return None
