"""
🎬 VIDEO ROUTER - Универсальный клиент для генерации видео через OpenRouter
Поддержка всех 17 моделей с автоматическим роутингом по тарифам
"""

import aiohttp
import asyncio
import logging
import json
import base64
import os
from typing import Optional, Dict, Any
import config
from config_video_models import (
    VIDEO_MODELS,
    get_model_info,
    get_model_id,
    calculate_cost,
    RECOMMENDED_MODELS
)

logger = logging.getLogger(__name__)

class VideoRouter:
    """
    Универсальный роутер для генерации видео через OpenRouter API.
    Поддерживает все 17 моделей с автоматическим выбором ключа по тарифу.
    """

    def __init__(self):
        # Мультиключевой роутинг как в текстовых моделях
        self.keys = {
            "START": config.KEY_START,
            "PRO": config.KEY_PRO,
            "NEO": config.KEY_NEO
        }
        self.base_url = "https://openrouter.ai/api/v1"
        self.default_model = RECOMMENDED_MODELS["default"]

    def _get_api_key(self, tariff: str) -> str:
        """Получить API ключ по тарифу пользователя"""
        return self.keys.get(tariff, self.keys["START"])

    def _build_headers(self, api_key: str) -> Dict[str, str]:
        """Построить заголовки для запроса"""
        return {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://vnxoracle.uk",
            "X-Title": "vnxORACLE Video AI"
        }

    def _encode_image_to_base64(self, image_path: str) -> str:
        """Кодировать изображение в base64 для отправки в API"""
        try:
            with open(image_path, 'rb') as image_file:
                encoded = base64.b64encode(image_file.read()).decode('utf-8')
                # Определяем MIME тип по расширению
                ext = os.path.splitext(image_path)[1].lower()
                mime_types = {
                    '.jpg': 'image/jpeg',
                    '.jpeg': 'image/jpeg',
                    '.png': 'image/png',
                    '.webp': 'image/webp',
                    '.gif': 'image/gif'
                }
                mime_type = mime_types.get(ext, 'image/jpeg')
                return f"data:{mime_type};base64,{encoded}"
        except Exception as e:
            logger.error(f"❌ Image encoding error: {e}")
            return None

    async def generate_video(
        self,
        prompt: str,
        model_key: str = None,
        tariff: str = "START",
        source_image: str = None,
        duration: int = 8,
        resolution: str = "720p",
        aspect_ratio: str = "16:9",
        generate_audio: bool = False
    ) -> Optional[str]:
        """
        Генерация видео через OpenRouter API (РЕАЛЬНАЯ ДОКУМЕНТАЦИЯ).

        Args:
            prompt: Текстовое описание сцены или движения
            model_key: Ключ модели из config_video_models (например, "seedance-2.0")
            tariff: Тариф пользователя (START/PRO/NEO)
            source_image: URL или путь к исходному изображению для image-to-video
            duration: Длительность видео в секундах (4-15, зависит от модели)
            resolution: Разрешение (720p, 1080p)
            aspect_ratio: Соотношение сторон (16:9, 9:16, 1:1)
            generate_audio: Генерировать ли звук (удорожает)

        Returns:
            URL готового видео или None при ошибке
        """

        # Выбор модели
        if not model_key:
            model_key = self.default_model

        model_info = get_model_info(model_key)
        if not model_info:
            logger.error(f"❌ Unknown model key: {model_key}")
            return None

        model_id = model_info["id"]
        api_key = self._get_api_key(tariff)

        if not api_key:
            logger.error(f"❌ No API key for tariff: {tariff}")
            return None

        # Проверка возможностей модели
        if source_image and "image2video" not in model_info["capabilities"]:
            logger.warning(f"⚠️ Model {model_key} doesn't support image2video. Switching to text2video mode.")
            source_image = None

        # Формируем payload согласно РЕАЛЬНОЙ документации OpenRouter
        payload = {
            "model": model_id,
            "prompt": prompt,
            "duration": duration,
            "resolution": resolution,
            "aspect_ratio": aspect_ratio,
            "generate_audio": generate_audio
        }

        # Добавляем исходное изображение через frame_images (first_frame)
        if source_image:
            # Проверяем, это URL или локальный файл
            if source_image.startswith("http"):
                image_url = source_image
            else:
                # Локальный файл - кодируем в base64
                encoded_image = self._encode_image_to_base64(source_image)
                if not encoded_image:
                    logger.error(f"❌ Failed to encode image: {source_image}")
                    return None
                image_url = encoded_image

            # Используем frame_images согласно документации OpenRouter
            payload["frame_images"] = [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": image_url
                    },
                    "frame_type": "first_frame"
                }
            ]

        # Логируем запрос
        cost = calculate_cost(model_key, duration)
        logger.info(f"🎬 Video generation started:")
        logger.info(f"   Model: {model_info['name']} ({model_id})")
        logger.info(f"   Prompt: {prompt[:50]}...")
        logger.info(f"   Duration: {duration}s")
        logger.info(f"   Resolution: {resolution} {aspect_ratio}")
        logger.info(f"   Mode: {'image2video' if source_image else 'text2video'}")
        logger.info(f"   Audio: {'yes' if generate_audio else 'no'}")
        logger.info(f"   Estimated cost: ${cost:.3f}")

        try:
            headers = self._build_headers(api_key)
            # ПРАВИЛЬНЫЙ endpoint согласно документации OpenRouter
            endpoint = f"{self.base_url}/videos"

            async with aiohttp.ClientSession() as session:
                # Создаем задачу генерации
                async with session.post(
                    endpoint,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        logger.error(f"❌ OpenRouter API Error {resp.status}: {error_text}")
                        return None

                    result = await resp.json()
                    job_id = result.get("id")
                    polling_url = result.get("polling_url")

                    if not job_id or not polling_url:
                        logger.error(f"❌ No job_id or polling_url in response: {result}")
                        return None

                    logger.info(f"✅ Job created: {job_id}")
                    logger.info(f"   Polling URL: {polling_url}")

                # Polling результата согласно документации (начинаем с 30 секунд)
                max_attempts = 20  # 10 минут (30s * 20)
                attempt = 0
                poll_interval = 30  # начинаем с 30 секунд

                while attempt < max_attempts:
                    await asyncio.sleep(poll_interval)
                    attempt += 1

                    # Проверяем статус через polling_url
                    async with session.get(
                        polling_url,
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as status_resp:
                        if status_resp.status != 200:
                            logger.warning(f"⚠️ Status check HTTP {status_resp.status}, retrying...")
                            continue

                        status_data = await status_resp.json()
                        status = status_data.get("status")

                        if status == "completed":
                            # Получаем URL видео из unsigned_urls
                            unsigned_urls = status_data.get("unsigned_urls", [])
                            if unsigned_urls and len(unsigned_urls) > 0:
                                video_url = unsigned_urls[0]
                                logger.info(f"✅ Video generation completed: {video_url}")

                                # Логируем фактическую стоимость если есть
                                usage = status_data.get("usage", {})
                                actual_cost = usage.get("cost")
                                if actual_cost:
                                    logger.info(f"💰 Actual cost: ${actual_cost:.4f}")

                                return video_url
                            else:
                                logger.error(f"❌ No video URL in completed response: {status_data}")
                                return None

                        elif status == "failed":
                            error = status_data.get("error", "Unknown error")
                            logger.error(f"❌ Generation failed: {error}")
                            return None

                        elif status in ["cancelled", "expired"]:
                            logger.error(f"❌ Generation {status}: {status_data.get('error', 'No details')}")
                            return None

                        elif status in ["pending", "in_progress"]:
                            progress = status_data.get("progress", 0)
                            logger.info(f"⏳ {status.capitalize()}... {progress}% (attempt {attempt}/{max_attempts})")
                            # Уменьшаем интервал после первой проверки
                            if attempt == 1:
                                poll_interval = 15

                        else:
                            logger.warning(f"⚠️ Unknown status: {status}")

                logger.error(f"❌ Timeout: Video generation took too long (>{max_attempts * poll_interval}s)")
                return None

        except asyncio.TimeoutError:
            logger.error(f"❌ Request timeout")
            return None
        except Exception as e:
            logger.error(f"❌ Video generation error: {e}", exc_info=True)
            return None

    async def generate_video_kie_fallback(
        self,
        prompt: str,
        model: str = "kling-3-motion-control",
        source_image: str = None
    ) -> Optional[str]:
        """
        Fallback на KIE API (текущий провайдер Kling AI).
        Используется если OpenRouter недоступен или модель не поддерживается.
        """
        from services.kie_client import kie_studio

        logger.info(f"🔄 Fallback to KIE API: {model}")

        try:
            if source_image:
                # Image-to-video через KIE
                video_url = await kie_studio.generate_video(
                    prompt=prompt,
                    model=model,
                    image_input=source_image
                )
            else:
                # Text-to-video через KIE
                video_url = await kie_studio.generate_video(
                    prompt=prompt,
                    model=model
                )

            return video_url

        except Exception as e:
            logger.error(f"❌ KIE fallback error: {e}")
            return None

# Глобальный экземпляр роутера
video_router = VideoRouter()
