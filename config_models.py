import config

# =========================================================
# 🧠 НЕЙРОННЫЙ РЕЕСТР (MODEL REGISTRY)
# =========================================================

# --- 1. АВАРИЙНАЯ МОДЕЛЬ (FALLBACK) ---
# Самая надежная бесплатная модель. Если Google упадет, она подхватит.
FALLBACK_MODEL = "mistralai/mistral-7b-instruct:free"
FALLBACK_NAME = "Mistral 7B (Emergency Core)"

# --- 2. ДЕФОЛТНАЯ МОДЕЛЬ (ДЛЯ НОВИЧКОВ) ---
# Используем стабильную Flash-версию, а не Lite-Preview
DEFAULT_MODEL_ID = "google/gemini-2.0-flash-exp:free"

# --- 3. СПИСКИ МОДЕЛЕЙ ПО ТАРИФАМ ---

# 💠 START (Бесплатные и дешевые)
MODELS_START = [
    # Google (Обновленный ID)
    ("Gemini 2.0 Flash (Free)", "google/gemini-2.0-flash-exp:free"),
    
    # Надежная классика
    ("Mistral 7B (Free)", "mistralai/mistral-7b-instruct:free"),
    
    # DeepSeek (Может быть перегружен, но ID валидный)
    ("DeepSeek R1 (Free)", "deepseek/deepseek-r1:free"),
    
    # Liquid (Быстрая)
    ("Liquid LFM (Free)", "liquid/lfm-40b:free"),
    
    # Платная, но дешевая (если есть бюджет на START ключе)
    ("GPT-4o Mini", "openai/gpt-4o-mini"), 
]

# ⚡️ PRO (Мощные рабочие лошадки)
MODELS_PRO = [
    ("GPT-4o (Flagship)", "openai/gpt-4o-2024-08-06"),
    ("Claude 3.5 Haiku", "anthropic/claude-3-haiku"),
    ("Perplexity Online", "perplexity/llama-3.1-sonar-large-128k-online"),
    ("Gemini 1.5 Pro", "google/gemini-flash-1.5"),
]

# 🧬 NEO (Самые дорогие и умные)
MODELS_NEO = [
    ("Claude 3.5 Sonnet", "anthropic/claude-3.5-sonnet"),
    ("o1 Preview (Reasoning)", "openai/o1-preview"),
    ("Llama 3.1 405B", "meta-llama/llama-3.1-405b-instruct"),
]

# --- 4. ЛОГИКА ДОСТУПА ---

def get_available_models(tariff: str):
    """Возвращает список моделей (Имя, ID) для меню"""
    # Базовый список
    models = MODELS_START.copy()
    
    # Дополняем в зависимости от тарифа
    if tariff in ["PRO", "NEO"]:
        models.extend(MODELS_PRO)
        
    if tariff == "NEO":
        models.extend(MODELS_NEO)
        
    return models

def is_model_allowed(tariff: str, model_id: str):
    """Проверка прав доступа (Security Check)"""
    allowed = get_available_models(tariff)
    for name, mid in allowed:
        if mid == model_id:
            return True
            
    # ВАЖНО: Разрешаем fallback и default всегда, 
    # чтобы не получить ошибку "Model not allowed" при сбое
    if model_id in [FALLBACK_MODEL, DEFAULT_MODEL_ID]: 
        return True
        
    return False
