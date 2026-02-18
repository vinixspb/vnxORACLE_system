import aiohttp
import logging
import config

logger = logging.getLogger(__name__)

async def fetch_openrouter_models():
    """Запрашивает полный список моделей у OpenRouter"""
    url = "https://openrouter.ai/api/v1/models"
    api_key = config.KEY_START or config.KEY_PRO or config.KEY_NEO
    if not api_key: return []

    try:
        # Увеличили тайм-аут до 5 секунд, чтобы точно прогрузилось
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
    Умный поиск замены.
    excluded_models: список конкретных ID, которые нельзя предлагать.
    excluded_brands: список слов (например, ['google']), которые нельзя предлагать.
    """
    if excluded_models is None: excluded_models = []
    if excluded_brands is None: excluded_brands = []
    
    # Добавляем сломанную модель в исключения
    if broken_model_id not in excluded_models:
        excluded_models.append(broken_model_id)

    logger.info(f"🕵️‍♂️ Searching replacement. Excluded: {len(excluded_models)} models, Brands blocked: {excluded_brands}")
    
    all_models = await fetch_openrouter_models()
    
    # Резервный список, если API списков не отвечает
    fallback_list = [
        "mistralai/mistral-7b-instruct:free",
        "liquid/lfm-40b:free",
        "deepseek/deepseek-r1:free",
        "huggingfaceh4/zephyr-7b-beta:free",
        "openchat/openchat-7b:free"
    ]

    if not all_models:
        for m in fallback_list:
            if m not in excluded_models: return m
        return "mistralai/mistral-7b-instruct:free"

    broken_id_lower = broken_model_id.lower()
    is_free_needed = force_free or (":free" in broken_id_lower)

    # Функция проверки, не забанен ли бренд
    def is_brand_allowed(mid):
        for brand in excluded_brands:
            if brand in mid.lower(): return False
        return True

    # 1. СТРАТЕГИЯ "НАДЕЖНОСТЬ": Ищем Mistral или Liquid (они реже всего требуют куки)
    # Если мы в режиме force_free, сразу ищем их.
    if is_free_needed:
        reliable_brands = ["mistral", "liquid", "microsoft", "openchat"]
        for brand in reliable_brands:
            if brand in excluded_brands: continue
            
            for model in all_models:
                mid = model.get("id", "")
                if mid in excluded_models: continue
                
                if ":free" in mid and brand in mid:
                    return mid

    # 2. СТРАТЕГИЯ "ШИРОКИЙ ПОИСК": Берем любую доступную
    for model in all_models:
        mid = model.get("id", "")
        if mid in excluded_models: continue
        
        # Проверяем фильтр брендов
        if not is_brand_allowed(mid): continue
        
        # Проверяем бесплатность
        if is_free_needed and ":free" not in mid: continue
        
        return mid

    # 3. ПОСЛЕДНИЙ РУБЕЖ
    # Если всё перепробовали, возвращаем Mistral, даже если он был в исключениях (лучше попробовать снова, чем упасть)
    return "mistralai/mistral-7b-instruct:free"
