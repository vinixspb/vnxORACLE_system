import aiohttp
import logging
import config

logger = logging.getLogger(__name__)

async def fetch_openrouter_models():
    """Запрашивает полный список моделей у OpenRouter"""
    url = "https://openrouter.ai/api/v1/models"
    # Берем любой доступный ключ для доступа к списку
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
    Ищет замену.
    force_free=True: Ищет СТРОГО бесплатную модель (нужно при ошибках 402 и 401).
    """
    logger.info(f"🕵️‍♂️ Searching replacement for: {broken_model_id} (Force Free: {force_free})")
    
    all_models = await fetch_openrouter_models()
    
    # Если список не грузится, возвращаем то, что точно работало в логах
    if not all_models:
        return "stepfun/step-3.5-flash:free" 

    broken_id_lower = broken_model_id.lower()
    keywords = []
    
    # Собираем ключевые слова бренда
    if "gemini" in broken_id_lower: keywords.append("gemini")
    elif "gpt" in broken_id_lower: keywords.append("gpt")
    elif "claude" in broken_id_lower: keywords.append("claude")
    elif "mistral" in broken_id_lower: keywords.append("mistral")
    elif "deepseek" in broken_id_lower: keywords.append("deepseek")
    elif "step" in broken_id_lower: keywords.append("step")
    
    # Определяем, нужна ли бесплатная
    # Если просят принудительно (402) ИЛИ сломанная была бесплатной
    is_free_needed = force_free or (":free" in broken_id_lower)

    # 1. Попытка найти похожую модель того же бренда
    for model in all_models:
        mid = model.get("id", "").lower()
        
        # Фильтр бесплатности
        if is_free_needed and ":free" not in mid:
            continue
            
        # Фильтр бренда
        if any(k in mid for k in keywords):
            return model.get("id")

    # 2. Если бренда нет, берем ЛЮБУЮ живую бесплатную (Priority List)
    if is_free_needed:
        # Приоритет надежности сейчас: Stepfun > Gemini > Mistral > Deepseek
        priority_keywords = ["stepfun", "google", "mistral", "deepseek"]
        for pk in priority_keywords:
            for model in all_models:
                mid = model.get("id", "")
                if ":free" in mid and pk in mid:
                    return mid

    # 3. Полный отчаянный фоллбек (Последняя надежда)
    return "stepfun/step-3.5-flash:free"
