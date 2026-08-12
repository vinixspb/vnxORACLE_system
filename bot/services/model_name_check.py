import aiohttp
import logging
import config

logger = logging.getLogger(__name__)

async def fetch_openrouter_models():
    url = "https://openrouter.ai/api/v1/models"
    api_key = config.KEY_START or config.KEY_PRO or config.KEY_NEO
    if not api_key: return []
    try:
        timeout = aiohttp.ClientTimeout(total=5)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("data", [])
                else: return []
    except: return []

async def find_best_replacement(broken_model_id: str, force_free: bool = False, excluded_models: list = None, excluded_brands: list = None):
    """
    Ищет замену.
    excluded_brands: список слов (например 'google'), при наличии которых модель пропускается.
    """
    if excluded_models is None: excluded_models = []
    if excluded_brands is None: excluded_brands = []
    
    # Добавляем сломанную модель в исключения
    if broken_model_id not in excluded_models:
        excluded_models.append(broken_model_id)

    logger.info(f"🕵️‍♂️ Replacement search. Excluded: {len(excluded_models)}. Banned brands: {excluded_brands}")
    
    all_models = await fetch_openrouter_models()
    
    # Резервный список (Надежный Mistral и Liquid)
    fallback_list = [
        "liquid/lfm-40b:free",
        "mistralai/mistral-7b-instruct:free",
        "huggingfaceh4/zephyr-7b-beta:free",
        "openchat/openchat-7b:free"
    ]

    # Если API списка не отвечает
    if not all_models:
        for m in fallback_list:
            if m not in excluded_models: return m
        return "mistralai/mistral-7b-instruct:free"

    broken_id_lower = broken_model_id.lower()
    is_free_needed = force_free or (":free" in broken_id_lower)

    # Функция проверки: разрешена ли модель?
    def is_safe(mid):
        # 1. Не в черном списке моделей
        if mid in excluded_models: return False
        # 2. Не содержит забаненный бренд
        for brand in excluded_brands:
            if brand in mid.lower(): return False
        return True

    # 1. Попытка найти РАБОЧУЮ модель того же бренда (если бренд не в бане)
    for model in all_models:
        mid = model.get("id", "")
        if not is_safe(mid): continue
        
        # Проверяем фильтр бесплатности
        if is_free_needed and ":free" not in mid: continue
        
        # Пытаемся найти совпадение по бренду
        brand_match = False
        if "gemini" in broken_id_lower and "gemini" in mid: brand_match = True
        elif "gpt" in broken_id_lower and "gpt" in mid: brand_match = True
        elif "claude" in broken_id_lower and "claude" in mid: brand_match = True
        elif "mistral" in broken_id_lower and "mistral" in mid: brand_match = True
        
        if brand_match: return mid

    # 2. Если бренда нет или он в бане -> Ищем Надежных (Priority List)
    # Liquid и Mistral сейчас самые стабильные
    priority_brands = ["liquid", "mistral", "openchat", "microsoft"]
    
    if is_free_needed:
        for brand in priority_brands:
            # Пропускаем, если этот бренд забанен (например, если google в бане)
            if brand in excluded_brands: continue
            
            for model in all_models:
                mid = model.get("id", "")
                if is_safe(mid) and ":free" in mid and brand in mid:
                    return mid

    # 3. Берем любую доступную бесплатную
    if is_free_needed:
        for model in all_models:
            mid = model.get("id", "")
            if is_safe(mid) and ":free" in mid:
                return mid

    # 4. Последний рубеж
    return "mistralai/mistral-7b-instruct:free"
