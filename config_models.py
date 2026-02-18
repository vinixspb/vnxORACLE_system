import config

# =========================================================
# 🧠 НЕЙРОННЫЙ РЕЕСТР (MODEL REGISTRY)
# =========================================================

# --- 1. АВАРИЙНАЯ МОДЕЛЬ (FALLBACK) ---
FALLBACK_MODEL = "mistralai/mistral-7b-instruct:free"
FALLBACK_NAME = "Mistral 7B (Emergency)"

# --- 2. ДЕФОЛТНАЯ МОДЕЛЬ ---
# Ставим Mistral как дефолт, пока Google штормит, это самое безопасное решение.
# Как только Google стабилизируется, вернем его.
DEFAULT_MODEL_ID = "mistralai/mistral-7b-instruct:free"

# --- 3. СПИСКИ МОДЕЛЕЙ ---

MODELS_START = [
    # Пробуем этот ID, он чаще бывает жив
    ("Gemini 2.0 Flash (Free)", "google/gemini-2.0-flash-lite-preview-02-05:free"),
    ("Mistral 7B (Free)", "mistralai/mistral-7b-instruct:free"),
    ("DeepSeek R1 (Free)", "deepseek/deepseek-r1:free"),
    ("Liquid LFM (Free)", "liquid/lfm-40b:free"),
    ("GPT-4o Mini", "openai/gpt-4o-mini"), 
]

MODELS_PRO = [
    ("GPT-4o (Flagship)", "openai/gpt-4o-2024-08-06"),
    ("Claude 3.5 Haiku", "anthropic/claude-3-haiku"),
    ("Perplexity Online", "perplexity/llama-3.1-sonar-large-128k-online"),
    ("Gemini 1.5 Pro", "google/gemini-flash-1.5"),
]

MODELS_NEO = [
    ("Claude 3.5 Sonnet", "anthropic/claude-3.5-sonnet"),
    ("o1 Preview (Reasoning)", "openai/o1-preview"),
    ("Llama 3.1 405B", "meta-llama/llama-3.1-405b-instruct"),
]

# --- 4. ЛОГИКА ---
def get_available_models(tariff: str):
    models = MODELS_START.copy()
    if tariff in ["PRO", "NEO"]:
        models.extend(MODELS_PRO)
    if tariff == "NEO":
        models.extend(MODELS_NEO)
    return models

def is_model_allowed(tariff: str, model_id: str):
    allowed = get_available_models(tariff)
    for name, mid in allowed:
        if mid == model_id: return True
    if model_id in [FALLBACK_MODEL, DEFAULT_MODEL_ID]: return True
    return False
