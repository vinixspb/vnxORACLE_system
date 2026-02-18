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
        # Init clients
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
        if not client: return "⚠️ Ошибка: Нет ключей.", 0

        # Подготовка сообщений
        current_messages = list(messages)
        if not current_messages or current_messages[0].get('role') != 'system':
            current_messages.insert(0, {"role": "system", "content": config.SYSTEM_PROMPT})
        
        # Vision
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
        # 🛡 SURVIVAL LOOP (ЦИКЛ ВЫЖИВАНИЯ)
        # =================================================
        max_retries = 3  # Количество жизней у запроса
        attempt = 0
        current_model = model
        blacklist = [] # Список моделей, которые провалились в этом запросе
        
        while attempt < max_retries:
            attempt += 1
            try:
                logger.info(f"🔄 Attempt {attempt}/{max_retries} using {current_model}")
                
                response = await client.chat.completions.create(
                    model=current_model,
                    messages=current_messages,
                    temperature=config.AI_TEMPERATURE,
                    extra_headers={"HTTP-Referer": "https://vnxmatrix.com", "X-Title": "vnxORACLE"}
                )
                
                answer = response.choices[0].message.content
                # Если была замена модели, добавляем пометку
                if current_model != model:
                    short_name = current_model.split('/')[-1].replace(":free", "")
                    answer += f"\n\n<i>(🛡 Auto-Switch: {short_name})</i>"
                
                return answer, response.usage.total_tokens

            except APIStatusError as e:
                error_code = e.status_code
                error_msg = str(e).lower()
                logger.warning(f"⚠️ Fail {attempt} ({current_model}): {error_code} - {e}")
                
                # Добавляем текущую модель в черный список
                blacklist.append(current_model)

                # Анализ ошибки
                is_fatal = False
                force_free = False
                
                if error_code in [404, 400] and ("model" in error_msg or "endpoint" in error_msg):
                    pass # Модель умерла, ищем замену
                elif error_code in [401, 403]:
                    force_free = True # Ошибка авторизации (часто у нестабильных провайдеров)
                elif error_code == 402:
                    force_free = True # Нет денег
                elif error_code >= 500:
                    pass # Сервер упал
                else:
                    is_fatal = True # Неизвестная ошибка (например, слишком длинный контекст), ретрай не поможет

                if is_fatal or attempt >= max_retries:
                    logger.error("❌ All attempts failed.")
                    return f"⚠️ Система перегружена. Ошибка: {error_code}", 0

                # Ищем замену для следующей попытки
                # ВАЖНО: Передаем blacklist, чтобы не выбрать ту же самую
                new_model = await find_best_replacement(current_model, force_free=force_free, excluded_models=blacklist)
                
                if new_model == current_model:
                    # Если функция вернула ту же модель (что невозможно при правильной логике, но на всякий случай)
                    new_model = "mistralai/mistral-7b-instruct:free"

                # Уведомляем админа о переключении (только при первом сбое)
                if attempt == 1:
                    await self._alert_admin(f"Сбой {current_model} ({error_code}).\nРетрай через: {new_model}")
                
                current_model = new_model
                continue # Идем на следующий круг цикла

            except Exception as e:
                logger.error(f"🧠 Critical Error: {e}")
                return "⚠️ Критическая ошибка системы.", 0
        
        return "⚠️ Не удалось получить ответ от нейросети.", 0

    async def transcribe_audio(self, file_path):
        if not self.client_audio: return None
        try:
            with open(file_path, "rb") as audio_file:
                transcript = await self.client_audio.audio.transcriptions.create(model="whisper-1", file=audio_file)
            return transcript.text
        except: return None
