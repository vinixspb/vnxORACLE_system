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
        
        # === ДИАГНОСТИКА КЛЮЧЕЙ (В ЛОГИ) ===
        def mask_key(k): return f"{k[:7]}..." if k and len(k) > 10 else "MISSING/INVALID"
        
        logger.info(f"🔑 Key Check: START={mask_key(config.KEY_START)} | PRO={mask_key(config.KEY_PRO)} | NEO={mask_key(config.KEY_NEO)}")

        # Инициализация клиентов
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
            payload = {"chat_id": config.ADMIN_ID, "text": f"🆘 <b>AI SURVIVAL MODE</b>\n{error_text}", "parse_mode": "HTML"}
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
        if not client: return "⚠️ Ошибка системы: AI-ключи не найдены. Обратитесь к администратору.", 0

        # Подготовка сообщений
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
        # 🛡 SURVIVAL LOOP (5 ПОПЫТОК)
        # =================================================
        max_retries = 5
        attempt = 0
        current_model = model
        blacklist = [] # ID моделей
        bad_brands = [] # Бренды, которые глючат (например, google)
        
        while attempt < max_retries:
            attempt += 1
            try:
                # В продакшене лучше не пугать юзера лишними логами, но для админа пишем
                if attempt > 1:
                    logger.warning(f"🔄 Attempt {attempt}: Trying {current_model}")
                
                response = await client.chat.completions.create(
                    model=current_model,
                    messages=current_messages,
                    temperature=config.AI_TEMPERATURE,
                    extra_headers={"HTTP-Referer": "https://vnxmatrix.com", "X-Title": "vnxORACLE"}
                )
                
                answer = response.choices[0].message.content
                if current_model != model:
                    short_name = current_model.split('/')[-1].replace(":free", "")
                    # Более профессиональная подпись
                    answer += f"\n\n<code>[⚙️ channel switched: {short_name}]</code>"
                
                return answer, response.usage.total_tokens

            except APIStatusError as e:
                error_code = e.status_code
                error_msg = str(e).lower()
                logger.warning(f"⚠️ Fail {attempt} ({current_model}): {error_code} - {e}")
                
                blacklist.append(current_model)

                # --- АНАЛИЗ ОШИБКИ ---
                force_free = False
                
                # Ошибка "No cookie auth" -> Это проблема Google/Gemini. Баним весь бренд Google.
                if "cookie" in error_msg or "auth credentials" in error_msg:
                    force_free = True # Безопаснее уйти на Mistral
                    if "google" not in bad_brands: bad_brands.append("google")
                    if "gemini" not in bad_brands: bad_brands.append("gemini")
                    if "gemma" not in bad_brands: bad_brands.append("gemma")
                    logger.warning(f"🚫 Blocking brands due to cookie error: {bad_brands}")

                elif error_code == 402:
                    force_free = True # Нет денег
                elif error_code in [401, 403]:
                    force_free = True # Ошибка доступа

                # Если это последняя попытка - не кидаем ошибку в лицо, а пишем вежливо
                if attempt >= max_retries:
                    logger.error("❌ Survival Loop exhausted.")
                    return (
                        "⚠️ <b>Временная перегрузка нейросети.</b>\n"
                        "Все каналы связи сейчас заняты или обновляются.\n"
                        "Пожалуйста, повторите запрос через 1-2 минуты."
                    ), 0

                # Ищем замену
                new_model = await find_best_replacement(
                    current_model, 
                    force_free=force_free, 
                    excluded_models=blacklist,
                    excluded_brands=bad_brands # <-- Передаем забаненные бренды
                )
                
                # Если первая попытка упала, тихо сообщаем админу
                if attempt == 1:
                    await self._alert_admin(f"⚠️ <b>Swap Triggered</b>\nFrom: {current_model}\nError: {error_code}\nRetry: {new_model}")
                
                current_model = new_model
                continue

            except Exception as e:
                logger.error(f"🧠 Critical Error: {e}")
                return "⚠️ Внутренняя ошибка обработки данных.", 0
        
        return "⚠️ Нет связи с сервером.", 0

    async def transcribe_audio(self, file_path):
        if not self.client_audio: return None
        try:
            with open(file_path, "rb") as audio_file:
                transcript = await self.client_audio.audio.transcriptions.create(model="whisper-1", file=audio_file)
            return transcript.text
        except: return None
