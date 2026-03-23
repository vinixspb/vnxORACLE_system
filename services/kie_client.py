import aiohttp
import asyncio
import logging
import json
import os
import base64
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

    # ==========================================
    # 🖼 ГЕНЕРАЦИЯ ИЗОБРАЖЕНИЙ (И IMG2IMG)
    # ==========================================
    async def generate_image(self, prompt: str, model: str, ratio: str = "vertical", source_image: str = None) -> tuple:
        """Асинхронная генерация изображений (поддерживает Img2Img). Возвращает (image_url, task_id)"""
        if not self.api_key:
            logger.error("❌ KIE Client: KIE_API_KEY is missing.")
            return None, None

        create_url = f"{self.base_url}/jobs/createTask"
        
        # Определяем семейство модели
        model_family = "default"
        model_lower = model.lower()
        
        if "nano-banana" in model_lower:
            model_family = "nano_banana"
        elif "qwen-image" in model_lower or "qwen_image" in model_lower:
            model_family = "qwen_image"  # 🆕 Qwen 2.0
        elif "gpt-4o-image" in model_lower:
            model_family = "gpt_4o"
        elif "flux" in model_lower:
            model_family = "flux"
        elif "seedream" in model_lower:
            model_family = "seedream"
        elif "grok" in model_lower:
            model_family = "grok"

        # МАТРИЦА ПАРАМЕТРОВ
        config_matrix = {
            "vertical": {
                "nano_banana": {"aspect_ratio": "9:16", "resolution": "1K", "output_format": "png"},
                "qwen_image": {"image_size": "portrait_16_9", "output_format": "png", "num_inference_steps": 30},  
                "gpt_4o": {},  
                "flux": {"resolution": "1K", "aspect_ratio": "9:16"},
                "seedream": {"resolution": "1K", "aspect_ratio": "9:16"},
                "grok": {"aspect_ratio": "9:16"},
                "default": {"aspect_ratio": "9:16", "resolution": "1K"}
            },
            "horizontal": {
                "nano_banana": {"aspect_ratio": "16:9", "resolution": "1K", "output_format": "png"},
                "qwen_image": {"image_size": "landscape_16_9", "output_format": "png", "num_inference_steps": 30},  
                "gpt_4o": {},
                "flux": {"resolution": "1K", "aspect_ratio": "16:9"},
                "seedream": {"resolution": "1K", "aspect_ratio": "16:9"},
                "grok": {"aspect_ratio": "16:9"},
                "default": {"aspect_ratio": "16:9", "resolution": "1K"}
            },
            "square": {
                "nano_banana": {"aspect_ratio": "1:1", "resolution": "1K", "output_format": "png"},
                "qwen_image": {"image_size": "square", "output_format": "png", "num_inference_steps": 30},  
                "gpt_4o": {},
                "flux": {"resolution": "1K", "aspect_ratio": "1:1"},
                "seedream": {"resolution": "1K", "aspect_ratio": "1:1"},
                "grok": {"aspect_ratio": "1:1"},
                "default": {"aspect_ratio": "1:1", "resolution": "1K"}
            }
        }

        safe_ratio = ratio if ratio in config_matrix else "vertical"
        params = config_matrix[safe_ratio].get(model_family, config_matrix[safe_ratio]["default"])

        # Собираем payload
        input_data = {"prompt": prompt, "num_images": 1}
        
        # 🔥 ИНТЕГРАЦИЯ IMG2IMG (Редактирование фото)
        if source_image and os.path.exists(source_image):
            try:
                with open(source_image, "rb") as img_file:
                    encoded_string = base64.b64encode(img_file.read()).decode('utf-8')
                    ext = source_image.split('.')[-1].lower()
                    mime_type = "image/png" if ext == "png" else "image/jpeg"
                    # KIE API требует передавать картинку массивом image_input
                    input_data["image_input"] = [f"data:{mime_type};base64,{encoded_string}"]
                    logger.info(f"🪄 Img2Img: Прикреплено фото для изменения.")
            except Exception as e:
                logger.error(f"❌ KIE Img2Img Error: Не удалось прочитать исходное фото: {e}")

        # Добавляем остальные параметры матрицы
        for key, value in params.items():
            input_data[key] = value

        payload = {"model": model, "input": input_data}
        task_id = None
        
        # Отправка задачи
        async with aiohttp.ClientSession(headers=self.headers) as session:
            try:
                async with session.post(create_url, json=payload, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                    data = await resp.json()
                    if data.get("code") != 200:
                        logger.error(f"❌ KIE Create Task Error: {data} | Payload: {payload}")
                        return None, None
                    
                    task_id = data.get("data", {}).get("taskId")
                    logger.info(f"✅ KIE Task Created: {task_id} (Model: {model})")
            except Exception as e:
                logger.error(f"❌ KIE Network Error: {e}")
                return None, None

        if not task_id:
            return None, None

        # Ожидание результата
        query_url = f"{self.base_url}/jobs/recordInfo?taskId={task_id}"
        max_attempts = 60
        
        async with aiohttp.ClientSession(headers=self.headers) as session:
            for attempt in range(max_attempts):
                await asyncio.sleep(3)
                try:
                    async with session.get(query_url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                        result_data = await resp.json()
                        if result_data.get("code") != 200:
                            continue
                            
                        task_info = result_data.get("data", {})
                        state = task_info.get("state")
                        
                        if state == "success":
                            result_json_str = task_info.get("resultJson", "{}")
                            try:
                                parsed_result = json.loads(result_json_str)
                                image_url = parsed_result.get("resultUrls", [None])[0]
                                logger.info(f"🎨 KIE Image Complete! URL: {image_url}")
                                return image_url, task_id
                            except json.JSONDecodeError:
                                return None, None
                        elif state == "fail":
                            logger.error(f"❌ KIE Task Failed: {task_info.get('failMsg')}")
                            return None, None
                except Exception:
                    continue

        logger.error(f"❌ KIE Task Timeout")
        return None, None

    # ==========================================
    # 🎬 ГЕНЕРАЦИЯ ВИДЕО
    # ==========================================
    async def generate_video(self, prompt: str, model: str, ratio: str = "vertical") -> str:
        """Генерация видео через KIE (Kling 3.0 / Grok Video)"""
        if not self.api_key:
            return None
            
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
                async with session.post(create_url, json=payload, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                    data = await resp.json()
                    if data.get("code") == 200:
                        task_id = data.get("data", {}).get("taskId")
                        logger.info(f"✅ KIE Video Task Created: {task_id}")
                    else:
                        logger.error(f"❌ KIE Video Task Error: {data} | Payload: {payload}")
            except Exception as e:
                logger.error(f"❌ KIE Video Error: {e}")
                return None

        if not task_id:
            return None

        query_url = f"{self.base_url}/jobs/recordInfo?taskId={task_id}"
        
        async with aiohttp.ClientSession(headers=self.headers) as session:
            for attempt in range(100):
                await asyncio.sleep(3)
                try:
                    async with session.get(query_url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                        result_data = await resp.json()
                        if result_data.get("code") != 200:
                            continue
                            
                        state = result_data.get("data", {}).get("state")
                        if state == "success":
                            result_json_str = result_data.get("data", {}).get("resultJson", "{}")
                            try:
                                parsed = json.loads(result_json_str)
                                video_url = parsed.get("resultUrls", [None])[0]
                                logger.info(f"🎬 KIE Video Complete! URL: {video_url}")
                                return video_url
                            except:
                                return None
                        elif state == "fail":
                            return None
                except:
                    continue
        return None

    # ==========================================
    # ✨ УЛУЧШЕНИЕ КАЧЕСТВА (UPSCALE)
    # ==========================================
    async def upscale_image(self, source_image: str) -> str:
        if not self.api_key or not source_image or not os.path.exists(source_image):
            return None
            
        create_url = f"{self.base_url}/jobs/createTask"
        
        try:
            with open(source_image, "rb") as img_file:
                encoded_string = base64.b64encode(img_file.read()).decode('utf-8')
                ext = source_image.split('.')[-1].lower()
                mime_type = "image/png" if ext == "png" else "image/jpeg"
                image_input = [f"data:{mime_type};base64,{encoded_string}"]
        except Exception as e:
            logger.error(f"❌ KIE Upscale Error: Не удалось прочитать фото: {e}")
            return None

        payload = {
            "model": "grok-imagine/upscale",
            "input": {"image_input": image_input}
        }

        task_id = None
        async with aiohttp.ClientSession(headers=self.headers) as session:
            try:
                async with session.post(create_url, json=payload, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                    data = await resp.json()
                    if data.get("code") == 200:
                        task_id = data.get("data", {}).get("taskId")
                        logger.info(f"✅ KIE Upscale Task Created: {task_id}")
            except Exception as e:
                logger.error(f"❌ KIE Network Error (Upscale): {e}")
                return None

        if not task_id:
            return None

        query_url = f"{self.base_url}/jobs/recordInfo?taskId={task_id}"
        
        async with aiohttp.ClientSession(headers=self.headers) as session:
            for attempt in range(60):
                await asyncio.sleep(3)
                try:
                    async with session.get(query_url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                        result_data = await resp.json()
                        if result_data.get("code") != 200:
                            continue
                            
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
