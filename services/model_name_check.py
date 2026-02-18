import aiohttp
import logging
import config

logger = logging.getLogger(__name__)

async def fetch_openrouter_models():
    """Запрашивает полный список моделей у OpenRouter"""
    url = "https://openrouter.ai/api/v1/models"
    
    # Берем любой доступный ключ
    api_key = config.KEY_START or config.KEY_PRO or config.KEY_NEO
    if not api_key:
        return []

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("data", [])
                else:
                    logger.error(f"⚠️ Failed to check models list: {resp.status}")
                    return []
    except Exception as e:
        logger.error(f"⚠️ Network error checking models: {e}")
        return []

async def find_best_replacement(broken_model_id: str):
    """
    Умный поиск замены.
    Если сломалась 'google/gemini...free', ищет другую 'google...free'.
    """
    logger.info(f"🕵️‍♂️ Checking replacement for dead model: {broken_model_id}")
    
    all_models = await fetch_openrouter_models()
    if not all_models:
        # Если не удалось получить список, возвращаем Железный Резерв
        return "mistralai/mistral-7b-instruct:free"

    # 1. Анализируем, что мы ищем (ключевые слова из старого названия)
    broken_id_lower = broken_model_id.lower()
    keywords = []
    
    if "gemini" in broken_id_lower: keywords.append("gemini")
    if "gpt" in broken_id_lower: keywords.append("gpt")
    if "claude" in broken_id_lower: keywords.append("claude")
    if "llama" in broken_id_lower: keywords.append("llama")
    
    # Если модель была бесплатной, замена ОБЯЗАНА быть бесплатной
    is_free = ":free" in broken_id_lower

    # 2. Ищем кандидата
    best_candidate = None
    
    for model in all_models:
        mid = model.get("id", "").lower()
        
        # Если нужна бесплатная, а эта платная — пропускаем
        if is_free and ":free" not in mid:
            continue
            
        # Проверяем совпадение бренда (google, mistral, etc)
        if all(k in mid for k in keywords):
            # Нашли! Например искали 'gemini' и нашли 'google/gemini-2.0-pro-exp:free'
            best_candidate = model.get("id")
            break 
    
    if best_candidate:
        logger.info(f"✅ Found alive replacement: {best_candidate}")
        return best_candidate
    
    # 3. Если точной замены нет, но нужна бесплатная — берем ЛЮБУЮ бесплатную Mistral или Google
    if is_free:
        for model in all_models:
            mid = model.get("id", "")
            if ":free" in mid and ("mistral" in mid or "google" in mid):
                return mid

    # 4. Последний рубеж
    return "mistralai/mistral-7b-instruct:free"
