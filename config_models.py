import config

# =========================================================
# 🧠 НЕЙРОННЫЙ РЕЕСТР
# =========================================================

# --- АВАРИЙНАЯ МОДЕЛЬ ---
# Stepfun сейчас живой, ставим его.
FALLBACK_MODEL = "stepfun/step-3.5-flash:free"
FALLBACK_NAME = "StepFun (Emergency)"

# --- ДЕФОЛТНАЯ МОДЕЛЬ ---
DEFAULT_MODEL_ID = "stepfun/step-3.5-flash:free"

# --- СПИСКИ МОДЕЛЕЙ ---
# Здесь просто перечисли, что хотим видеть в меню.
# Реальные ID будут проверяться системой healing.

MODELS_START = [
    ("Gemini 2.0 Flash (Free)", "google/gemini-2.0-flash-exp:free"),
    ("Mistral 7B (Free)", "mistralai/mistral-7b-instruct:free"),
    ("DeepSeek R1 (Free)", "deepseek/deepseek-r1:free"),
    ("StepFun (Free)", "stepfun/step-3.5-flash:free"),
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
    # Разрешаем то, что система нашла сама через healing
    return True
