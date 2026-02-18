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
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("data", [])
                else: return []
    except: return []

async def find_best_replacement(broken_model_id: str, force_free: bool = False):
    """
    Ищет замену, ИСКЛЮЧАЯ саму сломанную модель.
    """
    logger.info(f"🕵️‍♂️ Searching replacement for: {broken_model_id} (Force Free: {force_free})")
    
    all_models = await fetch_openrouter_models()
    if not all_models:
        # Резерв на случай, если API списков лежит
        return "mistralai/mistral-7b-instruct:free" 

    broken_id_lower = broken_model_id.lower()
    keywords = []
    
    # Собираем ключевые слова бренда
    if "gemini" in broken_id_lower: keywords.append("gemini")
    elif "gpt" in broken_id_lower: keywords.append("gpt")
    elif "claude" in broken_id_lower: keywords.append("claude")
    elif "mistral" in broken_id_lower: keywords.append("mistral")
    elif "deepseek" in broken_id_lower: keywords.append("deepseek")
    elif "step" in broken_id_lower: keywords.append("step")
    elif "liquid" in broken_id_lower: keywords.append("liquid")
    
    is_free_needed = force_free or (":free" in broken_id_lower)

    # 1. Ищем модель того же бренда (но другую версию!)
    for model in all_models:
        mid = model.get("id", "").lower()
        
        # ГЛАВНОЕ ИСПРАВЛЕНИЕ: Не выбираем ту же самую сломанную модель
        if mid == broken_id_lower:
            continue
        
        # Фильтр бесплатности
        if is_free_needed and ":free" not in mid:
            continue
            
        # Фильтр бренда
        if any(k in mid for k in keywords):
            return model.get("id")

    # 2. Если бренда нет, берем ЛЮБУЮ живую бесплатную (Priority List)
    # StepFun убираем из приоритета, раз он глючит (401)
    if is_free_needed:
        priority_keywords = ["liquid", "mistral", "google", "deepseek"]
        for pk in priority_keywords:
            for model in all_models:
                mid = model.get("id", "")
                # Также проверяем, не является ли это сломанной моделью
                if mid.lower() == broken_id_lower: continue
                
                if ":free" in mid and pk in mid:
                    return mid

    # 3. Полный отчаянный фоллбек (Liquid сейчас стабилен)
    return "liquid/lfm-40b:free"
