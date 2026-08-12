import aiohttp
import asyncio
import logging
import json
import os
import base64
import copy
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

    def _sanitize_logs(self, payload: dict) -> dict:
        """🛡 ЗАЩИТА ЛОГОВ: Удаляем огромные Base64 строки"""
        safe_payload = copy.deepcopy(payload)
        try:
            if "input" in safe_payload:
                if "image_input" in safe_payload["input"]:
                    safe_payload["input"]["image_input"] = ["<BASE64_HIDDEN>"]
                if "image_url" in safe_payload["input"] and str(safe_payload["input"]["image_url"]).startswith("data:image"):
                    safe_payload["input"]["image_url"] = "<BASE64_HIDDEN>"
            if "base64Data" in safe_payload:
                safe_payload["base64Data"] = "<BASE64_HIDDEN>"
        except Exception:
            pass
        return safe_payload

    async def _upload_stream(self, file_path: str) -> str:
        """🚀 ИДЕАЛЬНЫЙ UPLOAD: Бинарный стрим (без Base64) + Прямой сервер KIE"""
        url = "https://kieai.redpandaai.co/api/file-stream-upload"
        
        try:
            with open(file_path, 'rb') as f:
                async with aiohttp.ClientSession() as session:
                    form = aiohttp.FormData()
                    form.add_field('file', f, filename=os.path.basename(file_path))
                    form.add_field('uploadPath', 'images/bot-uploads')
                    
                    async with session.post(url, headers={"Authorization": f"Bearer {self.api_key}"}, data=form, timeout=60) as resp:
                        if resp.status == 200:
                            res = await resp.json()
                            if res.get("success") and "data" in res:
                                result_url = res["data"].get("downloadUrl")
                                if result_url:
                                    logger.info(f"✅ Успешная STREAM-загрузка: {result_url}")
                                    return result_url
                            logger.error(f"❌ KIE Stream Parse Error: {res}")
                        else:
                            logger.error(f"❌ KIE Stream HTTP Error: {resp.status} - {await resp.text()}")
        except Exception as e:
            logger.error(f"❌ KIE Stream Network Error: {e}")
        return None

    # ==========================================
    # 🖼 ГЕНЕРАЦИЯ ИЗОБРАЖЕНИЙ (И IMG2IMG)
    # ==========================================
    async def generate_image(self, prompt: str, model: str, ratio: str = "vertical", source_image: str = None) -> tuple:
        if not self.api_key:
            logger.error("❌ KIE Client: KIE_API_KEY is missing.")
            return None, None

        create_url = f"{self.base_url}/jobs/createTask"
        
        model_family = "default"
        model_lower = model.lower()
        if "nano-banana" in model_lower: model_family = "nano_banana"
        elif "qwen" in model_lower: model_family = "qwen_image"
        elif "gpt-4o" in model_lower: model_family = "gpt_4o"
        elif "flux" in model_lower: model_family = "flux"
        elif "seedream" in model_lower: model_family = "seedream"
        elif "grok" in model_lower: model_family = "grok"

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

        input_data = {"prompt": prompt, "num_images": 1}
        
        # 🔥 ИНТЕГРАЦИЯ IMG2IMG: УМНЫЙ РОУТЕР (SMART ROUTER) QWEN vs GROK
        if source_image and os.path.exists(source_image):
            # 1. Анализируем сложность промпта (длина > 80 или наличие стилистических маркеров)
            complex_keywords = ['realistic', 'style', 'cinematic', 'cartoon', 'anime', 'фэнтези', 'реалистичн', 'мультяшн', 'стиль', 'детали', 'качеств', 'кинематограф', 'art', 'арт']
            is_complex = len(prompt) > 80 or any(kw in prompt.lower() for kw in complex_keywords)
            
            # 2. Роутинг на основе сложности
            if is_complex:
                model = "grok-imagine/image-to-image"
                model_family = "grok_img2img"
                logger.info(f"🧠 Smart Router: Сложный промпт (len={len(prompt)}). Маршрутизация на GROK (Premium).")
            else:
                model = "qwen/image-edit"
                model_family = "qwen_image"
                logger.info(f"🧠 Smart Router: Простой промпт (len={len(prompt)}). Маршрутизация на QWEN (Default).")

            # 3. Загружаем фото через STREAM (работает безотказно)
            image_url = await self._upload_stream(source_image)
            
            if image_url:
                if model_family == "grok_img2img":
                    # 🔥 ИДЕАЛЬНЫЙ PAYLOAD GROK (из документации: массив image_urls)
                    input_data = {
                        "prompt": prompt,
                        "image_urls": [image_url]
                    }
                else:
                    # 🔥 ИДЕАЛЬНЫЙ PAYLOAD QWEN (стандартное редактирование)
                    input_data = {
                        "image_url": image_url,
                        "prompt": prompt,
                        "acceleration": "none",
                        "guidance_scale": 7.5,
                        "sync_mode": False,
                        "enable_safety_checker": True,
                        "negative_prompt": "blurry, ugly, deformed, bad anatomy, bad quality",
                        "seed": -1
                    }
                logger.info(f"🪄 Img2Img: Фото загружено ({image_url}) для {model}.")
            else:
                logger.error("❌ Не удалось загрузить фото через Stream Upload.")
                return None, None
        else:
            # Для Text2Img (генерация с нуля) прикрепляем стандартные параметры из config_matrix
            for key, value in params.items():
                input_data[key] = value

        payload = {"model": model, "input": input_data}
        task_id = None
        
        async with aiohttp.ClientSession(headers=self.headers) as session:
            # 🔥 ВНЕДРЯЕМ RETRY-ЛОГИКУ (3 попытки)
            for attempt in range(3):
                try:
                    async with session.post(create_url, json=payload, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                        # Если сервер KIE отвечает 5xx - ждем 2 сек и пробуем снова
                        if resp.status >= 500:
                            logger.warning(f"⚠️ KIE Server Error {resp.status}, попытка {attempt + 1}/3...")
                            await asyncio.sleep(2)
                            continue
                            
                        data = await resp.json()
                        if data.get("code") != 200:
                            logger.error(f"❌ KIE Create Task Error: {data} | Payload: {self._sanitize_logs(payload)}")
                            break # Если ошибка 4xx (например 422 параметры), ретрай не поможет
                        
                        task_id = data.get("data", {}).get("taskId")
                        logger.info(f"✅ KIE Task Created: {task_id} (Model: {model})")
                        break # Успех, выходим из цикла retry
                except asyncio.TimeoutError:
                    logger.warning(f"⚠️ KIE Timeout, попытка {attempt + 1}/3...")
                    await asyncio.sleep(2)
                except Exception as e:
                    logger.error(f"❌ KIE Network Error: {e}")
                    break

        if not task_id: return None, None

        query_url = f"{self.base_url}/jobs/recordInfo?taskId={task_id}"
        async with aiohttp.ClientSession(headers=self.headers) as session:
            for attempt in range(60):
                await asyncio.sleep(3)
                try:
                    async with session.get(query_url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                        result_data = await resp.json()
                        if result_data.get("code") != 200: continue
                        task_info = result_data.get("data", {})
                        state = task_info.get("state")
                        if state == "success":
                            result_json_str = task_info.get("resultJson", "{}")
                            try:
                                parsed_result = json.loads(result_json_str)
                                image_url = parsed_result.get("resultUrls", [None])[0]
                                logger.info(f"🎨 KIE Image Complete! URL: {image_url}")
                                return image_url, task_id
                            except json.JSONDecodeError: return None, None
                        elif state == "fail":
                            logger.error(f"❌ KIE Task Failed: {task_info.get('failMsg')}")
                            return None, None
                except Exception: continue
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
        payload = {"model": model, "input": {"prompt": prompt, "aspect_ratio": params["aspect_ratio"], "mode": "normal", "duration": "6", "resolution": params["resolution"]}}
        task_id = None
        async with aiohttp.ClientSession(headers=self.headers) as session:
            try:
                async with session.post(create_url, json=payload, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                    data = await resp.json()
                    if data.get("code") == 200:
                        task_id = data.get("data", {}).get("taskId")
                    else:
                        logger.error(f"❌ KIE Video Task Error: {data}")
            except Exception as e: return None

        if not task_id: return None

        query_url = f"{self.base_url}/jobs/recordInfo?taskId={task_id}"
        async with aiohttp.ClientSession(headers=self.headers) as session:
            for attempt in range(100):
                await asyncio.sleep(3)
                try:
                    async with session.get(query_url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                        result_data = await resp.json()
                        if result_data.get("code") != 200: continue
                        state = result_data.get("data", {}).get("state")
                        if state == "success":
                            result_json_str = result_data.get("data", {}).get("resultJson", "{}")
                            try:
                                parsed = json.loads(result_json_str)
                                return parsed.get("resultUrls", [None])[0]
                            except: return None
                        elif state == "fail": return None
                except: continue
        return None

    # ==========================================
    # ✨ УЛУЧШЕНИЕ КАЧЕСТВА (ГИБРИДНЫЙ UPSCALE PIPELINE)
    # ==========================================
    async def upscale_pipeline(self, task_id: str = None, image_path: str = None) -> tuple:
        """
        🚀 АРХИТЕКТУРА УРОВНЯ SaaS:
        1. KIE (если есть task_id)
        2. ESRGAN через Replicate (если это пользовательское фото)
        Возвращает: (url, provider_name)
        """
        # 1. KIE (основной быстрый контур)
        if task_id:
            logger.info(f"✨ Запуск KIE Upscale для task_id: {task_id}")
            url = await self._kie_upscale(task_id)
            if url:
                return url, "KIE"
            logger.warning("⚠️ KIE Upscale не удался. Переход к fallback...")

        # 2. ESRGAN (внешний премиум контур для загруженных фото)
        if image_path and os.path.exists(image_path):
            replicate_key = getattr(config, 'REPLICATE_API_KEY', None)
            if not replicate_key:
                logger.error("❌ REPLICATE_API_KEY отсутствует. Внешний Upscale невозможен.")
                return None, None

            logger.info(f"✨ Запуск Real-ESRGAN Upscale для: {image_path}")
            url = await self._replicate_esrgan_upscale(image_path, replicate_key)
            if url:
                return url, "ESRGAN"

        return None, None

    async def _kie_upscale(self, task_id: str) -> str:
        """Внутренний Upscale KIE по task_id"""
        create_url = f"{self.base_url}/jobs/createTask"
        
        # 🔥 Отправляем оба варианта (snake_case и camelCase)
        payload = {"model": "grok-imagine/upscale", "input": {"task_id": task_id, "taskId": task_id}}
        task_id_new = None
        
        async with aiohttp.ClientSession(headers=self.headers) as session:
            try:
                async with session.post(create_url, json=payload, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                    data = await resp.json()
                    if data.get("code") == 200: 
                        task_id_new = data.get("data", {}).get("taskId")
                    else:
                        # 🔥 Теперь мы точно увидим причину отклонения в консоли
                        logger.error(f"❌ KIE Upscale API Error: {data} | Payload: {payload}")
            except Exception as e: 
                logger.error(f"❌ KIE Upscale HTTP Error: {e}")
                return None

        if not task_id_new: return None
        
        query_url = f"{self.base_url}/jobs/recordInfo?taskId={task_id_new}"
        async with aiohttp.ClientSession(headers=self.headers) as session:
            for attempt in range(60):
                await asyncio.sleep(3)
                try:
                    async with session.get(query_url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                        result_data = await resp.json()
                        if result_data.get("code") != 200: continue
                        state = result_data.get("data", {}).get("state")
                        if state == "success":
                            result_json_str = result_data.get("data", {}).get("resultJson", "{}")
                            try:
                                parsed = json.loads(result_json_str)
                                return parsed.get("resultUrls", [None])[0]
                            except json.JSONDecodeError: return None
                        elif state == "fail": return None
                except Exception: continue
        return None

    async def _replicate_esrgan_upscale(self, image_path: str, api_key: str) -> str:
        """Внешний премиум Upscale (Real-ESRGAN) через Replicate API"""
        url = "https://api.replicate.com/v1/predictions"
        headers = {
            "Authorization": f"Token {api_key}",
            "Content-Type": "application/json"
        }

        try:
            with open(image_path, "rb") as img_file:
                encoded = base64.b64encode(img_file.read()).decode('utf-8')
                ext = image_path.split('.')[-1].lower()
                mime = "image/png" if ext == "png" else "image/jpeg"
                data_uri = f"data:{mime};base64,{encoded}"

            # Точный Payload для Real-ESRGAN x2 (с улучшением лиц)
            payload = {
                "version": "42fed1c4974146d4d2414e2be2c5277c7fcf05fcc3a73abf41610695738c1d7b", 
                "input": {
                    "image": data_uri,
                    "scale": 2,
                    "face_enhance": True
                }
            }

            async with aiohttp.ClientSession() as session:
                # 1. Отправляем задачу в Replicate
                async with session.post(url, headers=headers, json=payload, timeout=30) as resp:
                    if resp.status != 201:
                        logger.error(f"❌ Replicate Error: {await resp.text()}")
                        return None
                    data = await resp.json()
                    prediction_url = data["urls"]["get"]

                # 2. Ожидаем результат (Polling)
                for _ in range(60):
                    await asyncio.sleep(2)
                    async with session.get(prediction_url, headers=headers, timeout=10) as resp:
                        if resp.status == 200:
                            poll_data = await resp.json()
                            status = poll_data.get("status")
                            if status == "succeeded":
                                return poll_data.get("output")
                            elif status == "failed":
                                logger.error(f"❌ Replicate Prediction Failed: {poll_data}")
                                return None
        except Exception as e:
            logger.error(f"❌ Replicate Network Error: {e}")

        return None

kie_studio = KieClient()
