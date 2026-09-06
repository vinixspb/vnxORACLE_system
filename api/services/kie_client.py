"""
KIE API клиент для генерации изображений и видео
Упрощённая версия из bot/services/kie_client.py для Web API
"""
import aiohttp
import logging
from typing import Optional, Tuple
import config_media as media_config

logger = logging.getLogger(__name__)


class KieClient:
    def __init__(self):
        self.api_key = media_config.KIE_API_KEY
        self.base_url = media_config.KIE_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def generate_image(
        self,
        prompt: str,
        model: str,
        ratio: str = "square"
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Генерация изображения через KIE API

        Args:
            prompt: текстовое описание
            model: ID модели (из config_media)
            ratio: vertical | horizontal | square

        Returns:
            (image_url, task_id) или (None, None) при ошибке
        """
        if not self.api_key:
            logger.error("❌ KIE_API_KEY not configured")
            return None, None

        # Определяем family модели для параметров
        model_family = self._detect_model_family(model)
        params = self._get_model_params(model_family, ratio)

        # Формируем payload
        payload = {
            "model": model,
            "input": {
                "prompt": prompt,
                "num_images": 1,
                **params
            }
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/jobs/createTask",
                    headers=self.headers,
                    json=payload,
                    timeout=60
                ) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        task_id = result.get("data", {}).get("task_id")

                        if not task_id:
                            logger.error(f"❌ KIE: No task_id in response")
                            return None, None

                        # Дожидаемся результата
                        image_url = await self._poll_task(task_id)
                        return image_url, task_id
                    else:
                        error_text = await resp.text()
                        logger.error(f"❌ KIE API error {resp.status}: {error_text}")
                        return None, None

        except Exception as e:
            logger.error(f"❌ KIE generate_image exception: {e}")
            return None, None

    async def _poll_task(self, task_id: str, max_attempts: int = 60) -> Optional[str]:
        """Опрашиваем статус задачи до завершения"""
        query_url = f"{self.base_url}/jobs/query-record-info"

        for attempt in range(max_attempts):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        query_url,
                        headers=self.headers,
                        json={"task_id": task_id},
                        timeout=10
                    ) as resp:
                        if resp.status == 200:
                            result = await resp.json()
                            status = result.get("data", {}).get("status")

                            if status == "SUCCESS":
                                outputs = result.get("data", {}).get("output", [])
                                if outputs and len(outputs) > 0:
                                    return outputs[0].get("url")
                            elif status == "FAILED":
                                logger.error(f"❌ KIE task {task_id} failed")
                                return None

                            # Ждём 2 секунды перед следующей попыткой
                            await aiohttp.ClientSession().close()
                            import asyncio
                            await asyncio.sleep(2)

            except Exception as e:
                logger.error(f"❌ KIE polling error: {e}")
                return None

        logger.error(f"❌ KIE task {task_id} timeout after {max_attempts} attempts")
        return None

    def _detect_model_family(self, model: str) -> str:
        """Определяем семейство модели по ID"""
        model_lower = model.lower()
        if "flux" in model_lower:
            return "flux"
        elif "midjourney" in model_lower:
            return "midjourney"
        elif "qwen" in model_lower:
            return "qwen_vl"
        elif "dall-e" in model_lower or "dalle" in model_lower:
            return "dalle"
        elif "ideogram" in model_lower:
            return "ideogram"
        else:
            return "default"

    def _get_model_params(self, family: str, ratio: str) -> dict:
        """Возвращаем параметры генерации для модели и пропорций"""
        config_matrix = {
            "vertical": {
                "flux": {"resolution": "1K", "aspect_ratio": "9:16"},
                "midjourney": {"aspect_ratio": "9:16", "quality": "high"},
                "qwen_vl": {"image_size": "portrait_16_9", "output_format": "png"},
                "dalle": {"size": "1024x1792", "quality": "hd"},
                "ideogram": {"aspect_ratio": "ASPECT_9_16", "style_type": "DESIGN"},
                "default": {"aspect_ratio": "9:16", "resolution": "1K"}
            },
            "horizontal": {
                "flux": {"resolution": "1K", "aspect_ratio": "16:9"},
                "midjourney": {"aspect_ratio": "16:9", "quality": "high"},
                "qwen_vl": {"image_size": "landscape_16_9", "output_format": "png"},
                "dalle": {"size": "1792x1024", "quality": "hd"},
                "ideogram": {"aspect_ratio": "ASPECT_16_9", "style_type": "DESIGN"},
                "default": {"aspect_ratio": "16:9", "resolution": "1K"}
            },
            "square": {
                "flux": {"resolution": "1K", "aspect_ratio": "1:1"},
                "midjourney": {"aspect_ratio": "1:1", "quality": "high"},
                "qwen_vl": {"image_size": "square", "output_format": "png"},
                "dalle": {"size": "1024x1024", "quality": "hd"},
                "ideogram": {"aspect_ratio": "ASPECT_1_1", "style_type": "DESIGN"},
                "default": {"aspect_ratio": "1:1", "resolution": "1K"}
            }
        }

        safe_ratio = ratio if ratio in config_matrix else "square"
        return config_matrix[safe_ratio].get(family, config_matrix[safe_ratio]["default"])


# Singleton instance
kie_client = KieClient()
