import aiohttp
import asyncio
import logging
import json
import config

logger = logging.getLogger(__name__)

class KieClient:
    def __init__(self):
        self.api_key = config.KIE_API_KEY
        self.base_url = "[https://api.kie.ai/api/v1](https://api.kie.ai/api/v1)"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    # ==========================================
    # 🖼 ГЕНЕРАЦИЯ ИЗОБРАЖЕНИЙ
    # ==========================================
    async def generate_image(self, prompt: str, model: str, ratio: str = "vertical") -> tuple:
        """
        Асинхронная генерация изображений.
        Возвращает кортеж (image_url, task_id) — task_id нужен для Upscale.
        """
        if not self.api_key:
            logger.error("❌ KIE Client: KIE_API_KEY is missing.")
            return None, None

        create_url = f"{self.base_url}/jobs/createTask"
        
        # 🧠 1. Определяем семейство нейросети
        model_family = "default"
        model_lower = model.lower()
        if "flux" in model_lower: model_family = "flux"
        elif "seedream" in model_lower: model_family = "seedream"
        elif "gpt" in model_lower or "dall" in model_lower: model_family = "gpt"
        elif "grok" in model_lower: model_family = "grok"
        elif "qwen" in model_lower: model_family = "qwen"
        elif "sd3" in model_lower or "stabilityai" in model_lower: model_family = "sd3" # <-- Добавили Nano Banana
        elif "midjourney" in model_lower or "mj" in model_lower: model_family = "midjourney" # <-- Добавили Midjourney

        # 🧠 2. ИДЕАЛЬНАЯ МАТРИЦА (со всеми моделями)
        config_matrix = {
            "vertical": {
                "flux": {"resolution": "1K", "aspect_ratio": "9:16"},
                "seedream": {"resolution": "1K", "aspect_ratio": "9:16"},
                "gpt": {"image_size": "9:16", "output_format": "png"},
                "grok": {"aspect_ratio": "9:16"},
                "qwen": {"image_size": "portrait_16_9", "output_format": "png", "num_inference_steps": 30, "guidance_scale": 2.5, "enable_safety_checker": True},
                "sd3": {"aspect_ratio": "9:16", "output_format": "jpeg"}, # Профиль для Nano Banana
                "midjourney": {"aspect_ratio": "9:16"},
                "default": {"aspect_ratio": "9:16"}
            },
            "horizontal": {
                "flux": {"resolution": "1K", "aspect_ratio": "16:9"},
                "seedream": {"resolution": "1K", "aspect_ratio": "16:9"},
                "gpt": {"image_size": "16:9", "output_format": "png"},
                "grok": {"aspect_ratio": "16:9"},
                "qwen": {"image_size": "landscape_16_9", "output_format": "png", "num_inference_steps": 30, "guidance_scale": 2.5, "enable_safety_checker": True},
                "sd3": {"aspect_ratio": "16:9", "output_format": "jpeg"},
                "midjourney": {"aspect_ratio": "16:9"},
                "default": {"aspect_ratio": "16:9"}
            },
            "square": {
                "flux": {"resolution": "1K", "aspect_ratio": "1:1"},
                "seedream": {"resolution": "1K", "aspect_ratio": "1:1"},
                "gpt": {"image_size": "1:1", "output_format": "png"},
                "grok": {"aspect_ratio": "1:1"},
                "qwen": {"image_size": "square", "output_format": "png", "num_inference_steps": 30, "guidance_scale": 2.5, "enable_safety_checker": True},
                "sd3": {"aspect_ratio": "1:1", "output_format": "jpeg"},
                "midjourney": {"aspect_ratio": "1:1"},
                "default": {"aspect_ratio": "1:1"}
            }
        }

        # Безопасное извлечение
        safe_ratio = ratio if ratio in config_matrix else "vertical"
        params = config_matrix[safe_ratio].get(model_family, config_matrix[safe_ratio]["default"])

        # 🧠 3. Собираем идеальный payload
        input_data = {"prompt": prompt, "num_images": 1}
        for key, value in params.items():
            input_data[key] = value

        payload = {"model": model, "input": input_data}
        task_id = None
        
        # --- Отправка задачи ---
        async with aiohttp.ClientSession(headers=self.headers) as session:
            try:
                async with session.post(create_url, json=payload) as resp:
                    data = await resp.json()
                    if data.get("code") != 200:
                        # 🔥 Расширенное логирование: теперь мы видим, из-за чего ошибка 500!
                        logger.error(f"❌ KIE Create Task Error: {data} | Sent Payload: {payload}")
                        return None, None
                    
                    task_id = data.get("data", {}).get("taskId")
                    logger.info(f"✅ KIE Task Created: {task_id} (Model: {model}, Ratio: {ratio})")
            except Exception as e:
                logger.error(f"❌ KIE Network Error: {e}")
                return None, None

        if not task_id: return None, None

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
                                return image_url, task_id
                            except json.JSONDecodeError:
                                return None, None
                        elif state == "fail":
                            logger.error(f"❌ KIE Task Failed: {task_info.get('failMsg', 'Unknown')}")
                            return None, None
                except Exception:
                    continue 

        return None, None

    # ==========================================
    # 🎬 ГЕНЕРАЦИЯ ВИДЕО
    # ==========================================
    async def generate_video(self, prompt: str, model: str, ratio: str = "vertical") -> str:
        if not self.api_key: return None
        create_url = f"{self.base_url}/jobs/createTask"
        
        config_matrix = {
            "vertical": {"aspect_ratio": "9:16", "resolution": "480p"},
            "horizontal": {"aspect_ratio": "16:9", "resolution": "480p"},
            "square": {"aspect_ratio": "1:1", "resolution": "480p"}
        }
        params = config_matrix.get(ratio, config_matrix["vertical"])

        payload = {
            "model": model,
            "input": {
                "prompt": prompt,
                "aspect_ratio": params["aspect_ratio"],
                "mode": "normal",
                "duration": "6",
                "resolution": params["resolution"]
            }
        }

        task_id = None
        async with aiohttp.ClientSession(headers=self.headers) as session:
            try:
                async with session.post(create_url, json=payload) as resp:
                    data = await resp.json()
                    if data.get("code") == 200:
                        task_id = data.get("data", {}).get("taskId")
                        logger.info(f"✅ KIE Video Task Created: {task_id}")
                    else:
                        logger.error(f"❌ KIE Video Task Error: {data} | Payload: {payload}")
            except Exception as e:
                logger.error(f"❌ KIE Network Error (Video): {e}")
                return None

        if not task_id: return None

        query_url = f"{self.base_url}/jobs/recordInfo?taskId={task_id}"
        max_attempts = 100 
        
        async with aiohttp.ClientSession(headers=self.headers) as session:
            for attempt in range(max_attempts):
                await asyncio.sleep(3) 
                try:
                    async with session.get(query_url) as resp:
                        result_data = await resp.json()
                        if result_data.get("code") != 200: continue
                            
                        state = result_data.get("data", {}).get("state")
                        if state == "success":
                            result_json_str = result_data.get("data", {}).get("resultJson", "{}")
                            try:
                                parsed = json.loads(result_json_str)
                                video_url = parsed.get("resultUrls", [None])[0]
                                logger.info(f"🎬 KIE Video Task Completed! URL: {video_url}")
                                return video_url
                            except json.JSONDecodeError:
                                return None
                        elif state == "fail":
                            return None
                except Exception:
                    continue 
        return None

    # ==========================================
    # ✨ УЛУЧШЕНИЕ КАЧЕСТВА (UPSCALE)
    # ==========================================
    async def upscale_image(self, original_task_id: str) -> str:
        if not self.api_key: return None
        create_url = f"{self.base_url}/jobs/createTask"
        
        payload = {
            "model": "grok-imagine/upscale",
            "input": {"task_id": original_task_id}
        }

        task_id = None
        async with aiohttp.ClientSession(headers=self.headers) as session:
            try:
                async with session.post(create_url, json=payload) as resp:
                    data = await resp.json()
                    if data.get("code") == 200:
                        task_id = data.get("data", {}).get("taskId")
                        logger.info(f"✅ KIE Upscale Task Created: {task_id}")
            except Exception as e:
                logger.error(f"❌ KIE Network Error (Upscale): {e}")
                return None

        if not task_id: return None

        query_url = f"{self.base_url}/jobs/recordInfo?taskId={task_id}"
        
        async with aiohttp.ClientSession(headers=self.headers) as session:
            for attempt in range(60):
                await asyncio.sleep(3) 
                try:
                    async with session.get(query_url) as resp:
                        result_data = await resp.json()
                        if result_data.get("code") != 200: continue
                            
                        state = result_data.get("data", {}).get("state")
                        if state == "success":
                            result_json_str = result_data.get("data", {}).get("resultJson", "{}")
                            try:
                                parsed = json.loads(result_json_str)
                                upscaled_url = parsed.get("resultUrls", [None])[0]
                                logger.info(f"✨ KIE Upscale Task Completed! URL: {upscaled_url}")
                                return upscaled_url
                            except json.JSONDecodeError:
                                return None
                        elif state == "fail":
                            return None
                except Exception:
                    continue 
        return None

kie_studio = KieClient()
