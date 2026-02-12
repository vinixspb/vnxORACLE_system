# =========================================================
# 🧠 НЕЙРОННЫЙ РЕЕСТР (MODEL REGISTRY)
# =========================================================

# --- 1. АВАРИЙНАЯ МОДЕЛЬ (FALLBACK) ---
# Используется автоматически, если закончились деньги или основной API упал.
# Должна быть бесплатной и надежной.
FALLBACK_MODEL = "google/gemini-2.0-flash-exp:free"
FALLBACK_NAME = "Gemini Flash (Emergency)"

# --- 2. СПИСКИ МОДЕЛЕЙ ПО ТАРИФАМ ---
# Format: ("Красивое имя для меню", "ID_модели_в_OpenRouter")

# 💠 START (Бесплатные и дешевые)
MODELS_START = [
    ("Gemini 2.0 Flash (Free)", "google/gemini-2.0-flash-exp:free"),
    ("Mistral 7B (Free)", "mistralai/mistral-7b-instruct:free"),
    ("DeepSeek R1 (Free)", "deepseek/deepseek-r1:free"),
    ("Liquid LFM (Free)", "liquid/lfm-40b:free"),
    ("GPT-4o Mini", "openai/gpt-4o-mini"), # Платная, но дешевая (включена в старт)
]

# ⚡️ PRO (Мощные рабочие лошадки)
# Включает всё из START + эти:
MODELS_PRO = [
    ("GPT-4o (Flagship)", "openai/gpt-4o-2024-08-06"),
    ("Claude 3.5 Haiku", "anthropic/claude-3-haiku"),
    ("Perplexity Online", "perplexity/llama-3.1-sonar-large-128k-online"), # С поиском в интернете
]

# 🧬 NEO (Самые дорогие и умные)
# Включает всё из PRO + эти:
MODELS_NEO = [
    ("Claude 3.5 Sonnet", "anthropic/claude-3.5-sonnet"),
    ("o1 Preview (Reasoning)", "openai/o1-preview"), # Очень дорогая
    ("Llama 3.1 405B", "meta-llama/llama-3.1-405b-instruct"),
]

# --- 3. ФУНКЦИЯ ПОЛУЧЕНИЯ ДОСТУПНЫХ МОДЕЛЕЙ ---
def get_available_models(tariff: str):
    """Возвращает список моделей в зависимости от уровня доступа"""
    models = MODELS_START.copy()
    
    if tariff in ["PRO", "NEO"]:
        models.extend(MODELS_PRO)
        
    if tariff == "NEO":
        models.extend(MODELS_NEO)
        
    return models

# Проверка, имеет ли право юзер использовать конкретный ID модели
def is_model_allowed(tariff: str, model_id: str):
    allowed = get_available_models(tariff)
    for name, mid in allowed:
        if mid == model_id:
            return True
    # Разрешаем fallback модель всегда
    if model_id == FALLBACK_MODEL: 
        return True
    return False
