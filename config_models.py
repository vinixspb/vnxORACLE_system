import config

# =========================================================
# 🧠 НЕЙРОННЫЙ РЕЕСТР
# =========================================================

# --- АВАРИЙНАЯ МОДЕЛЬ ---
FALLBACK_MODEL = "mistralai/mistral-7b-instruct:free"
FALLBACK_NAME = "Mistral 7B (Core)"

# --- ДЕФОЛТНАЯ МОДЕЛЬ ---
# Ставим самую умную и дешевую из 5-го поколения
DEFAULT_MODEL_ID = "openai/o3-mini"

# --- СПИСКИ МОДЕЛЕЙ ---
MODELS_START = [
    # Новое поколение OpenAI (Быстрые, умные, дешевые)
    ("OpenAI o3-mini (Gen 5)", "openai/o3-mini"), 
    ("GPT-4o Mini (Classic)", "openai/gpt-4o-mini"),
    
    # Google (Платные API, стоят копейки, аптайм 100%)
    ("Gemini 2.0 Flash", "google/gemini-2.0-flash-001"),
    ("Gemini 2.5 Flash", "google/gemini-2.5-flash"), # На будущее, когда появится
    
    # Топовый Open-Source (Дешевая аренда)
    ("Claude 3.5 Haiku", "anthropic/claude-3-5-haiku-20241022"), # Сверхбыстрый Антропик
    ("DeepSeek V3 (Chat)", "deepseek/deepseek-chat"),            # Хит сезона, очень дешев
    ("DeepSeek R1 (Reasoning)", "deepseek/deepseek-reasoner"),   # С цепочкой рассуждений
    ("Llama 3.3 70B", "meta-llama/llama-3.3-70b-instruct"),      # Мощь от Meta
    ("Mistral Small 3", "mistralai/mistral-small-24b-instruct-2501") # Надежный француз
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
