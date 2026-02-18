import config

# =========================================================
# 🧠 НЕЙРОННЫЙ РЕЕСТР
# =========================================================

# --- АВАРИЙНАЯ МОДЕЛЬ ---
FALLBACK_MODEL = "mistralai/mistral-7b-instruct:free"
FALLBACK_NAME = "Mistral 7B (Core)"

# --- ДЕФОЛТНАЯ МОДЕЛЬ ---
# Используем Google - он самый умный из бесплатных.
# Если ID устареет, система сама найдет новый.
DEFAULT_MODEL_ID = "google/gemini-2.0-flash-lite-preview-02-05:free"

# --- СПИСКИ МОДЕЛЕЙ ---
MODELS_START = [
    ("Gemini 2.0 Flash (Free)", "google/gemini-2.0-flash-lite-preview-02-05:free"),
    ("Mistral 7B (Free)", "mistralai/mistral-7b-instruct:free"),
    ("DeepSeek R1 (Free)", "deepseek/deepseek-r1:free"),
    ("GPT-4o Mini", "openai/gpt-4o-mini"), 
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

def get_available_models(tariff: str):
    models = MODELS_START.copy()
    if tariff in ["PRO", "NEO"]: models.extend(MODELS_PRO)
    if tariff == "NEO": models.extend(MODELS_NEO)
    return models

def is_model_allowed(tariff: str, model_id: str):
    return True # Разрешаем динамические подмены
