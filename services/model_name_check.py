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
        timeout = aiohttp.ClientTimeout(total=5) # Тайм-аут 5 секунд
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("data", [])
                else: return []
    except: return []

async def find_best_replacement(broken_model_id: str, force_free: bool = False, excluded_models: list = None):
    """
    Ищет замену, исключая ВСЕ модели из списка excluded_models.
    Приоритет отдается стабильным провайдерам (Google, Mistral).
    """
    if excluded_models is None: excluded_models = []
    
    # Добавляем саму сломанную модель в исключения
    if broken_model_id not in excluded_models:
        excluded_models.append(broken_model_id)

    logger.info(f"🕵️‍♂️ Searching replacement. Excluded: {len(excluded_models)} models. Force Free: {force_free}")
    
    all_models = await fetch_openrouter_models()
    
    # Если список API недоступен, идем по хардкодному списку надежности
    if not all_models:
        hardcoded_fallbacks = [
            "google/gemini-2.0-flash-lite-preview-02-05:free",
            "google/gemini-2.0-flash-exp:free",
            "mistralai/mistral-7b-instruct:free",
            "deepseek/deepseek-r1:free"
        ]
        for m in hardcoded_fallbacks:
            if m not in excluded_models: return m
        return "mistralai/mistral-7b-instruct:free"

    broken_id_lower = broken_model_id.lower()
    is_free_needed = force_free or (":free" in broken_id_lower)

    # === СТРАТЕГИЯ 1: Надежные бесплатные бренды (Production Stability) ===
    # Если мы в режиме аварии (force_free), мы НЕ ищем похожие. Мы ищем РАБОЧИЕ.
    # Google и Mistral статистически самые надежные на OpenRouter.
    if is_free_needed:
        stability_priority = ["google", "mistral", "microsoft", "deepseek"]
        
        for brand in stability_priority:
            for model in all_models:
                mid = model.get("id", "")
                # Пропускаем, если в черном списке
                if mid in excluded_models: continue
                
                # Ищем бесплатную модель этого бренда
                if ":free" in mid and brand in mid:
                    return mid

    # === СТРАТЕГИЯ 2: Если не нашли надежных, ищем любую другую ===
    for model in all_models:
        mid = model.get("id", "")
        if mid in excluded_models: continue
        
        if is_free_needed and ":free" not in mid: continue
        
        return mid

    # === СТРАТЕГИЯ 3: Последний рубеж (если всё в черном списке) ===
    return "mistralai/mistral-7b-instruct:free"
