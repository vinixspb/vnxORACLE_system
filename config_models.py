import config

# =========================================================
# 🧠 НЕЙРОННЫЙ РЕЕСТР
# =========================================================

# --- АВАРИЙНАЯ МОДЕЛЬ ---
# Используем Liquid LFM - это сейчас одна из самых стабильных бесплатных моделей
FALLBACK_MODEL = "liquid/lfm-40b:free"
FALLBACK_NAME = "Liquid LFM (Emergency)"

# --- ДЕФОЛТНАЯ МОДЕЛЬ ---
# Ставим ту, которая точно работает, чтобы юзеры не ловили ошибки на старте
DEFAULT_MODEL_ID = "liquid/lfm-40b:free"

# --- СПИСКИ МОДЕЛЕЙ ---
MODELS_START = [
    ("Liquid LFM (Free)", "liquid/lfm-40b:free"), # Самая быстрая сейчас
    ("Gemini 2.0 Flash (Free)", "google/gemini-2.0-flash-lite-preview-02-05:free"),
    ("Mistral 7B (Free)", "mistralai/mistral-7b-instruct:free"),
    ("DeepSeek R1 (Free)", "deepseek/deepseek-r1:free"),
    ("GPT-4o Mini", "openai/gpt-4o-mini"), # Платная, дешевая
]

MODELS_PRO = [
    ("GPT-4o (Flagship)", "openai/gpt-4o-2024-08-06"),
    ("Claude 3.5 Haiku", "anthropic/claude-3-haiku"),
    ("Perplexity Online", "perplexity/llama-3.1-sonar-large-128k-online"),
]

MODELS_NEO = [
    ("Claude 3.5 Sonnet", "anthropic/claude-3.5-sonnet"),
    ("o1 Preview (Reasoning)", "openai/o1-preview"),
]

# --- ЛОГИКА ---
def get_available_models(tariff: str):
    models = MODELS_START.copy()
    if tariff in ["PRO", "NEO"]: models.extend(MODELS_PRO)
    if tariff == "NEO": models.extend(MODELS_NEO)
    return models

def is_model_allowed(tariff: str, model_id: str):
    allowed = get_available_models(tariff)
    for name, mid in allowed:
        if mid == model_id: return True
    return True # Разрешаем динамические замены
