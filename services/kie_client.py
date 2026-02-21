import aiohttp
import asyncio
import logging
import json
import config

logger = logging.getLogger(__name__)

class KieClient:
    def __init__(self):
        self.api_key = config.KIE_API_KEY
        self.base_url = "https://api.kie.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def generate_image(self, prompt: str, model: str, ratio: str = "9:16") -> str:
        """
        Асинхронная генерация изображения (Create Task -> Polling -> Result)
        """
        if not self.api_key:
            logger.error("❌ KIE Client: KIE_API_KEY is missing.")
            return None

        # ==========================================
        # 1. СОЗДАЕМ ЗАДАЧУ (CREATE TASK)
        # ==========================================
        create_url = f"{self.base_url}/jobs/createTask"
        
        # 🧠 1. Определяем семейство нейросети
        model_family = "default"
        model_lower = model.lower()
        if "flux" in model_lower: model_family = "flux"
        elif "seedream" in model_lower: model_family = "seedream"
        elif "gpt" in model_lower or "dall" in model_lower: model_family = "gpt"

        # 🧠 2. УНИВЕРСАЛЬНАЯ МАТРИЦА КОНФИГУРАЦИЙ
        # Здесь мы заранее прописали, что именно "любит" каждая нейросеть
        config_matrix = {
            "vertical": {
                "flux": {"resolution": "1K", "aspect_ratio": "9:16"},
                "seedream": {"resolution": "1K", "aspect_ratio": "9:16"},
                "gpt": {"resolution": "1024x1792", "aspect_ratio": "2:3"},
                "default": {"resolution": "1024x1792", "aspect_ratio": "9:16"}
            },
            "horizontal": {
                "flux": {"resolution": "1K", "aspect_ratio": "16:9"},
                "seedream": {"resolution": "1K", "aspect_ratio": "16:9"},
                "gpt": {"resolution": "1792x1024", "aspect_ratio": "3:2"},
                "default": {"resolution": "1792x1024", "aspect_ratio": "16:9"}
            },
            "square": {
                "flux": {"resolution": "1K", "aspect_ratio": "1:1"},
                "seedream": {"resolution": "1K", "aspect_ratio": "1:1"},
                "gpt": {"resolution": "1024x1024", "aspect_ratio": "1:1"},
                "default": {"resolution": "1024x1024", "aspect_ratio": "1:1"}
            }
        }

        # 🧠 3. Безопасное извлечение параметров
        # Если вдруг пришел кривой формат, берем вертикальный по умолчанию
        safe_ratio = ratio if ratio in config_matrix else "vertical"
        params = config_matrix[safe_ratio][model_family]

        payload = {
            "model": model,
            "input": {
                "prompt": prompt,
                "resolution": params["resolution"],
                "aspect_ratio": params["aspect_ratio"],
                "num_images": 1
            }
        }
        
        task_id = None
        
        async with aiohttp.ClientSession(headers=self.headers) as session:
            try:
                async with session.post(create_url, json=payload) as resp:
                    data = await resp.json()
                    
                    if data.get("code") != 200:
                        logger.error(f"❌ KIE Create Task Error: {data}")
                        return None
                    
                    task_id = data.get("data", {}).get("taskId")
                    logger.info(f"✅ KIE Task Created: {task_id} (Model: {model}, Ratio: {ratio} -> API: {input_data['aspect_ratio']})")
            except Exception as e:
                logger.error(f"❌ KIE Network Error (Create): {e}")
                return None

        if not task_id:
            return None

        # ==========================================
        # 2. ОПРАШИВАЕМ СЕРВЕР (POLLING)
        # ==========================================
        query_url = f"{self.base_url}/jobs/recordInfo?taskId={task_id}"
        
        # Настраиваем лимиты: 60 попыток по 3 секунды = 3 минуты максимум
        max_attempts = 60 
        
        async with aiohttp.ClientSession(headers=self.headers) as session:
            for attempt in range(max_attempts):
                await asyncio.sleep(3) # Рекомендованный интервал 2-5 сек
                
                try:
                    async with session.get(query_url) as resp:
                        result_data = await resp.json()
                        
                        if result_data.get("code") != 200:
                            logger.warning(f"⚠️ KIE Polling Error: {result_data}")
                            continue
                            
                        task_info = result_data.get("data", {})
                        state = task_info.get("state")
                        
                        if state == "success":
                            # ВАЖНО: resultJson это строка, парсим её
                            result_json_str = task_info.get("resultJson", "{}")
                            try:
                                parsed_result = json.loads(result_json_str)
                                # Достаем первый URL из массива resultUrls
                                image_url = parsed_result.get("resultUrls", [None])[0]
                                logger.info(f"🎨 KIE Task {task_id} Completed! URL: {image_url}")
                                return image_url
                            except json.JSONDecodeError:
                                logger.error(f"❌ KIE JSON Parse Error: {result_json_str}")
                                return None
                                
                        elif state == "fail":
                            fail_msg = task_info.get("failMsg", "Unknown error")
                            logger.error(f"❌ KIE Task {task_id} Failed: {fail_msg}")
                            return None
                            
                        else:
                            # state может быть: waiting, queuing, generating
                            logger.info(f"⏳ KIE Task {task_id} state: {state} (Attempt {attempt+1}/{max_attempts})")
                            
                except Exception as e:
                    logger.error(f"❌ KIE Network Error (Polling): {e}")
                    continue # Игнорируем единичные сбои сети и пробуем снова

        logger.warning(f"⚠️ KIE Task {task_id} Timeout: Exceeded {max_attempts} attempts.")
        return None

# Экспортируем готовый объект клиента
kie_studio = KieClient()
