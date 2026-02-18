import aiohttp
import logging
import config

logger = logging.getLogger(__name__)

async def fetch_openrouter_models():
    """Запрашивает полный список моделей у OpenRouter"""
    url = "https://openrouter.ai/api/v1/models"
    
    # Берем любой ключ, нам нужен просто доступ к списку
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
                    logger.error(f"⚠️ Failed to fetch models list: {resp.status}")
                    return []
    except Exception as e:
        logger.error(f"⚠️ Network error fetching models: {e}")
        return []

async def find_best_replacement(broken_model_id: str):
    """
    Ищет замену сломанной модели.
    Например: если сломалась 'google/gemini-2.0-flash-exp:free',
    он найдет любую другую 'gemini' + 'free'.
    """
    logger.info(f"🕵️‍♂️ Searching replacement for broken model: {broken_model_id}")
    
    all_models = await fetch_openrouter_models()
    if not all_models:
        return "mistralai/mistral-7b-instruct:free" # Самый надежный фоллбек, если сеть лежит

    # Разбираем имя сломанной модели (например, ищем 'gemini' и 'free')
    keywords = []
    if "gemini" in broken_model_id.lower(): keywords.append("gemini")
    if "gpt" in broken_model_id.lower(): keywords.append("gpt")
    if "claude" in broken_model_id.lower(): keywords.append("claude")
    if ":free" in broken_model_id: keywords.append(":free")

    # Ищем кандидата
    best_candidate = None
    
    for model in all_models:
        model_id = model.get("id", "")
        
        # Проверяем совпадение всех ключевых слов
        if all(k in model_id.lower() for k in keywords):
            best_candidate = model_id
            break # Берем первого подходящего
    
    if best_candidate:
        logger.info(f"✅ Found replacement: {best_candidate}")
        return best_candidate
    
    # Если точной замены нет, ищем просто любую бесплатную (если сломалась бесплатная)
    if ":free" in broken_model_id:
        for model in all_models:
            if ":free" in model.get("id", "") and "mistral" in model.get("id", ""):
                return model.get("id")

    return "mistralai/mistral-7b-instruct:free" # Последний рубеж обороны
