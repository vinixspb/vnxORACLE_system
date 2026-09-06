"""
Конфигурация для генерации медиа (изображения и видео)
Синхронизировано с bot/config.py
"""
import os
from dotenv import load_dotenv

load_dotenv()

# =========================================================
# 🎨 KIE API (Провайдер генерации медиа)
# =========================================================
KIE_API_KEY = os.getenv("KIE_API_KEY")
KIE_BASE_URL = "https://api.kie.ai/api/v1"

# =========================================================
# 🖼️ МОДЕЛИ ИЗОБРАЖЕНИЙ
# =========================================================
IMG_POLLINATIONS = "pollinations"                          # Бесплатно (Fallback)
IMG_FLUX_PRO = "flux-2/pro-ultra"                          # 🔥 Flux 2 Pro Ultra (2026)
IMG_MIDJOURNEY_7 = "midjourney-7/imagine"                  # 🎨 Midjourney v7 (Фотореализм)
IMG_QWEN_VL = "qwen-vl-max-0809"                          # 🖌 Qwen VL Max (Текст на изображениях)
IMG_DALLE_4 = "dall-e-4-vision"                           # 🌟 DALL-E 4 (Креативность)
IMG_IDEOGRAM_3 = "ideogram-3/turbo"                       # ⚡️ Ideogram 3 Turbo (Типографика)

DEFAULT_IMG_MODEL = IMG_FLUX_PRO

# Список моделей для API меню
IMAGE_MODELS = {
    "flux-pro": {
        "id": IMG_FLUX_PRO,
        "name": "Flux 2 Ultra",
        "description": "Лидер 2026. Фотореализм, логотипы, сложные композиции.",
        "emoji": "🔥"
    },
    "midjourney": {
        "id": IMG_MIDJOURNEY_7,
        "name": "Midjourney v7",
        "description": "Художественные арты и идеальная детализация.",
        "emoji": "🎨"
    },
    "qwen-vl": {
        "id": IMG_QWEN_VL,
        "name": "Qwen VL",
        "description": "Пишет текст на картинке без ошибок (постеры, баннеры).",
        "emoji": "🖌"
    },
    "dalle-4": {
        "id": IMG_DALLE_4,
        "name": "DALL-E 4",
        "description": "Креативные концепты и неожиданные решения.",
        "emoji": "🌟"
    },
    "ideogram-3": {
        "id": IMG_IDEOGRAM_3,
        "name": "Ideogram 3",
        "description": "Типографика премиум-уровня и дизайнерские шрифты.",
        "emoji": "⚡️"
    },
    "pollinations": {
        "id": IMG_POLLINATIONS,
        "name": "Pollinations",
        "description": "Быстрая генерация без ограничений.",
        "emoji": "🆓"
    }
}

# =========================================================
# 🎬 МОДЕЛИ ВИДЕО
# =========================================================
VIDEO_SORA_2 = "sora-2/turbo"                              # 🎬 Sora 2 Turbo (OpenAI, 2026)
VIDEO_VEO_3 = "google/veo-3"                               # 🌊 Google Veo 3 (Реалистичные сцены)
VIDEO_KLING_4 = "kling-4/pro"                              # 🎥 Kling 4 Pro (Китайский лидер)
VIDEO_RUNWAY_5 = "runway/gen-5"                            # 🚀 Runway Gen-5 (Креативные эффекты)

DEFAULT_VIDEO_MODEL = VIDEO_SORA_2

VIDEO_MODELS = {
    "sora-2": {
        "id": VIDEO_SORA_2,
        "name": "Sora 2 Turbo",
        "description": "OpenAI. Реалистичные видео до 20 секунд.",
        "emoji": "🎬"
    },
    "veo-3": {
        "id": VIDEO_VEO_3,
        "name": "Google Veo 3",
        "description": "Реалистичные сцены и природные ландшафты.",
        "emoji": "🌊"
    },
    "kling-4": {
        "id": VIDEO_KLING_4,
        "name": "Kling 4 Pro",
        "description": "Китайский лидер, кинематографичная анимация.",
        "emoji": "🎥"
    },
    "runway-5": {
        "id": VIDEO_RUNWAY_5,
        "name": "Runway Gen-5",
        "description": "Креативные эффекты и стилизация.",
        "emoji": "🚀"
    }
}
