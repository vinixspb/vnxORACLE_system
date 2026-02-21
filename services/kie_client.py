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

    async def generate_image(self, prompt: str, model: str, ratio: str = "vertical") -> str:
        """
        Асинхронная генерация (Create Task -> Polling -> Result)
        """
        if not self.api_key:
            logger.error("❌ KIE Client: KIE_API_KEY is missing.")
            return None

        create_url = f"{self.base_url}/jobs/createTask"
        
        # 🧠 1. Определяем семейство нейросети
        model_family = "default"
        model_lower = model.lower()
        if "flux" in model_lower: model_family = "flux"
        elif "seedream" in model_lower: model_family = "seedream"
        elif "gpt" in model_lower or "dall" in model_lower: model_family = "gpt"

        # 🧠 2. ИДЕАЛЬНАЯ МАТРИЦА (По официальным спецификациям KIE)
        config_matrix = {
            "vertical": {
                "flux": {"resolution": "1K", "aspect_ratio": "9:16"},
                "seedream": {"resolution": "1K", "aspect_ratio": "9:16"},
                "gpt": {"image_size": "9:16", "output_format": "png"},
                "default": {"aspect_ratio": "9:16"}
            },
            "horizontal": {
                "flux": {"resolution": "1K", "aspect_ratio": "16:9"},
                "seedream": {"resolution": "1K", "aspect_ratio": "16:9"},
                "gpt": {"image_size": "16:9", "output_format": "png"},
                "default": {"aspect_ratio": "16:9"}
            },
            "square": {
                "flux": {"resolution": "1K", "aspect_ratio": "1:1"},
                "seedream": {"resolution": "1K", "aspect_ratio": "1:1"},
                "gpt": {"image_size": "1:1", "output_format": "png"},
                "default": {"aspect_ratio": "1:1"}
            }
        }

        # Безопасное извлечение
        safe_ratio = ratio if ratio in config_matrix else "vertical"
        params = config_matrix[safe_ratio][model_family]

        # 🧠 3. Собираем идеальный payload
        input_data = {
            "prompt": prompt,
            "num_images": 1
        }
        
        # Динамически заливаем нужные ключи
        for key, value in params.items():
            input_data[key] = value

        payload = {
            "model": model,
            "input": input_data
        }

        task_id = None
        
        # --- Отправка задачи ---
        async with aiohttp.ClientSession(headers=self.headers) as session:
            try:
                async with session.post(create_url, json=payload) as resp:
                    data = await resp.json()
                    
                    if data.get("code") != 200:
                        logger.error(f"❌ KIE Create Task Error: {data}")
                        return None
                    
                    task_id = data.get("data", {}).get("taskId")
                    logger.info(f"✅ KIE Task Created: {task_id} (Model: {model}, Ratio: {ratio})")
            except Exception as e:
                logger.error(f"❌ KIE Network Error (Create): {e}")
                return None

        if not task_id: return None

        # --- Ожидание результата ---
        query_url = f"{self.base_url}/jobs/recordInfo?taskId={task_id}"
        max_attempts = 60 
        
        async with aiohttp.ClientSession(headers=self.headers) as session:
            for attempt in range(max_attempts):
                await asyncio.sleep(3) 
                
                try:
                    async with session.get(query_url) as resp:
                        result_data = await resp.json()
                        if result_data.get("code") != 200: continue
                            
                        task_info = result_data.get("data", {})
                        state = task_info.get("state")
                        
                        if state == "success":
                            result_json_str = task_info.get("resultJson", "{}")
                            try:
                                parsed_result = json.loads(result_json_str)
                                image_url = parsed_result.get("resultUrls", [None])[0]
                                logger.info(f"🎨 KIE Task Completed! URL: {image_url}")
                                return image_url
                            except json.JSONDecodeError:
                                return None
                        elif state == "fail":
                            fail_msg = task_info.get("failMsg", "Unknown error")
                            logger.error(f"❌ KIE Task Failed: {fail_msg}")
                            return None
                            
                except Exception as e:
                    continue 

        return None

kie_studio = KieClient()
