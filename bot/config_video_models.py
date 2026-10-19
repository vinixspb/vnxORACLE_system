"""
🎬 VIDEO MODELS REGISTRY
Полный реестр видеомоделей OpenRouter с ценами и возможностями
Обновлено: 2026-10-19
"""

# =========================================================
# 📊 РЕЕСТР ВИДЕОМОДЕЛЕЙ OPENROUTER
# =========================================================

VIDEO_MODELS = {
    # 💰 БЮДЖЕТНЫЕ (Экономные тесты)
    "seedance-2.0-mini": {
        "id": "bytedance/seedance-2.0-mini",
        "name": "Seedance 2.0 Mini",
        "provider": "ByteDance",
        "price_per_second": 0.0756,  # 720p без звука
        "quality_tier": "budget",
        "capabilities": ["text2video", "image2video"],
        "duration_range": [4, 15],
        "description": "Недорогие тесты движения и промптов. Самая экономная версия.",
        "best_for": "Массовые эксперименты с минимальными затратами (~$0.60 за 8 сек)",
        "emoji": "🪙"
    },

    "seedance-2.0-fast": {
        "id": "bytedance/seedance-2.0-fast",
        "name": "Seedance 2.0 Fast",
        "provider": "ByteDance",
        "price_per_second": 0.09072,  # 720p без звука
        "quality_tier": "budget",
        "capabilities": ["text2video", "image2video"],
        "duration_range": [4, 15],
        "description": "Быстрые черновики с более широкими возможностями.",
        "best_for": "Ускоренное тестирование идей перед финальной генерацией (~$0.73 за 8 сек)",
        "emoji": "⚡️"
    },

    # ⭐️ РЕКОМЕНДУЕМЫЕ (Оптимальный баланс)
    "seedance-2.0": {
        "id": "bytedance/seedance-2.0",
        "name": "Seedance 2.0",
        "provider": "ByteDance",
        "price_per_second": 0.1512,  # 720p без звука
        "quality_tier": "balanced",
        "capabilities": ["text2video", "image2video", "motion-control"],
        "duration_range": [4, 15],
        "description": "⭐️ ОСНОВНОЙ КАНДИДАТ. Отличный баланс реализма и управления движением.",
        "best_for": "Финальные сцены с Гришей. Сохранение лица и естественное движение (~$1.21 за 8 сек)",
        "emoji": "⭐️"
    },

    "veo-3.1-fast": {
        "id": "google/veo-3.1-fast",
        "name": "Veo 3.1 Fast",
        "provider": "Google",
        "price_per_second": 0.08,  # 720p без звука
        "quality_tier": "balanced",
        "capabilities": ["text2video", "image2video", "audio"],
        "duration_range": [4, 6, 8],  # Только 4, 6 или 8 секунд
        "description": "Альтернативный вариант для реалистичного движения и звука.",
        "best_for": "Быстрая генерация с хорошим качеством и опциональным звуком (~$0.64 за 8 сек)",
        "emoji": "🎬"
    },

    # 💎 ПРЕМИУМ (Контрольное сравнение)
    "kling-3.0-pro": {
        "id": "kwaivgi/kling-v3.0-pro",
        "name": "Kling Video 3.0 Pro",
        "provider": "Kuaishou",
        "price_per_second": 0.112,  # 720p без звука
        "quality_tier": "premium",
        "capabilities": ["text2video", "image2video", "motion-control", "first-last-frame"],
        "duration_range": [3, 15],
        "description": "Контрольное сравнение качества. Контроль начального и конечного кадра.",
        "best_for": "Проверка максимального качества движения и сохранения внешности (~$0.90 за 8 сек)",
        "emoji": "💎"
    }
}

# =========================================================
# 🎯 РЕКОМЕНДУЕМЫЕ МОДЕЛИ ПО ЗАДАЧАМ
# =========================================================

RECOMMENDED_MODELS = {
    "default": "seedance-2.0",  # Основной выбор
    "best_quality": "veo-3.1",  # Максимальное качество
    "best_price": "seedance-1.5-pro",  # Минимальная цена
    "character_preservation": "kling-3.0-pro",  # Сохранение внешности
    "fast_iteration": "seedance-2.0-fast",  # Быстрые тесты
}

# =========================================================
# 💰 ЦЕНОВЫЕ КАТЕГОРИИ
# =========================================================

PRICE_TIERS = {
    "budget": [m for m, data in VIDEO_MODELS.items() if data["quality_tier"] == "budget"],
    "balanced": [m for m, data in VIDEO_MODELS.items() if data["quality_tier"] == "balanced"],
    "high": [m for m, data in VIDEO_MODELS.items() if data["quality_tier"] == "high"],
    "premium": [m for m, data in VIDEO_MODELS.items() if data["quality_tier"] == "premium"],
}

# =========================================================
# 🎬 ГРУППЫ ПО ВОЗМОЖНОСТЯМ
# =========================================================

CAPABILITY_GROUPS = {
    "text2video": [m for m, data in VIDEO_MODELS.items() if "text2video" in data["capabilities"]],
    "image2video": [m for m, data in VIDEO_MODELS.items() if "image2video" in data["capabilities"]],
    "motion_control": [m for m, data in VIDEO_MODELS.items() if "motion-control" in data["capabilities"]],
    "audio": [m for m, data in VIDEO_MODELS.items() if "audio" in data["capabilities"]],
}

def get_model_info(model_key: str) -> dict:
    """Получить информацию о модели по ключу"""
    return VIDEO_MODELS.get(model_key)

def get_model_id(model_key: str) -> str:
    """Получить OpenRouter ID модели"""
    model = VIDEO_MODELS.get(model_key)
    return model["id"] if model else None

def calculate_cost(model_key: str, duration_seconds: int = 8) -> float:
    """Рассчитать стоимость генерации"""
    model = VIDEO_MODELS.get(model_key)
    if model:
        return model["price_per_second"] * duration_seconds
    return 0.0

def get_models_by_tier(tier: str) -> list:
    """Получить список моделей по ценовой категории"""
    return PRICE_TIERS.get(tier, [])

def get_models_by_capability(capability: str) -> list:
    """Получить список моделей по возможности"""
    return CAPABILITY_GROUPS.get(capability, [])
