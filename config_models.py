import config

# =========================================================
# 🧠 НЕЙРОННЫЙ РЕЕСТР (Март 2026)
# =========================================================

# --- АВАРИЙНАЯ МОДЕЛЬ ---
FALLBACK_MODEL = "mistralai/mistral-7b-instruct:free"
FALLBACK_NAME = "Mistral 7B (Core)"

# --- ДЕФОЛТНАЯ МОДЕЛЬ ---
DEFAULT_MODEL_ID = "openai/o3-mini"  # Самая умная и дешевая Gen 5

# =========================================================
# 💠 ТАРИФ START (Базовые модели)
# =========================================================
MODELS_START = [
    # 🔥 Новое поколение OpenAI (Gen 5: Reasoning)
    ("🧮 OpenAI o3-mini (Gen 5)", "openai/o3-mini"),
    ("⚡️ GPT-4o Mini (Classic)", "openai/gpt-4o-mini"),
    
    # 🌐 Google Gemini (2-е поколение)
    ("💎 Gemini 2.0 Flash", "google/gemini-2.0-flash-001"),
    ("💎 Gemini 2.5 Flash", "google/gemini-2.5-flash"),  # На будущее
    
    # 🧬 Anthropic (Сверхбыстрый)
    ("⚡️ Claude 3.5 Haiku", "anthropic/claude-3-5-haiku-20241022"),
    
    # 🔬 DeepSeek (Хит 2026, дешево и мощно)
    ("🎯 DeepSeek V3 (Chat)", "deepseek/deepseek-chat"),
    ("🧠 DeepSeek R1 (Reasoning)", "deepseek/deepseek-reasoner"),
    
    # 🦙 Meta (Open-Source флагман)
    ("🦙 Llama 3.3 70B", "meta-llama/llama-3.3-70b-instruct"),
    
    # 🇫🇷 Mistral (Надежный европейский)
    ("🇫🇷 Mistral Small 3", "mistralai/mistral-small-24b-instruct-2501")
]

# =========================================================
# ⚡️ ТАРИФ PRO (Флагманы + Интернет)
# =========================================================
MODELS_PRO = [
    ("🧠 GPT-4o (Flagship)", "openai/gpt-4o-2024-08-06"),
    ("🧠 GPT-5.2 (Новинка)", "openai/gpt-5.2"),  # 🆕 Если доступен в OpenRouter
    ("🧬 Claude 3.5 Sonnet", "anthropic/claude-3.5-sonnet"),
    ("🧬 Claude 4.5 Sonnet", "anthropic/claude-4.5-sonnet"),  # 🆕 Март 2026
    ("🌐 Perplexity Online", "perplexity/llama-3.1-sonar-large-128k-online"),
    ("💻 Qwen 2.5 Coder 32B", "qwen/qwen-2.5-coder-32b-instruct")
]

# =========================================================
# 🧬 ТАРИФ NEO (Максимум: Opus, o1, Reasoning)
# =========================================================
MODELS_NEO = [
    ("👑 Claude 4.6 Opus", "anthropic/claude-4.6-opus"),  # 🆕 Самая мощная модель
    ("👑 GPT-5.3 Codex", "openai/gpt-5.3-codex"),  # 🆕 Для программирования
    ("🧮 o1 Preview (Reasoning)", "openai/o1-preview"),
    ("🧮 o1 (Full)", "openai/o1"),  # Полная версия o1
    ("👑 Gemini Ultra 1.5", "google/gemini-1.5-ultra")
]

# =========================================================
# 🛡 ФУНКЦИИ ДОСТУПА
# =========================================================
def get_available_models(tariff: str):
    """Возвращает список моделей для тарифа"""
    models = MODELS_START.copy()
    if tariff in ["PRO", "NEO"]:
        models.extend(MODELS_PRO)
    if tariff == "NEO":
        models.extend(MODELS_NEO)
    return models

def is_model_allowed(tariff: str, model_id: str):
    """Проверяет доступность модели для тарифа"""
    start_ids = [m[1] for m in MODELS_START]
    pro_ids = [m[1] for m in MODELS_PRO]
    neo_ids = [m[1] for m in MODELS_NEO]
    
    if tariff == 'START':
        return model_id in start_ids
    elif tariff == 'PRO':
        return model_id in start_ids or model_id in pro_ids
    elif tariff in ['NEO', 'ARCHITECT']:
        return model_id in start_ids or model_id in pro_ids or model_id in neo_ids
    
    return False

def get_model_display_name(model_id: str) -> str:
    """Возвращает красивое имя модели"""
    all_models = MODELS_START + MODELS_PRO + MODELS_NEO
    for display_name, id_name in all_models:
        if id_name == model_id:
            return display_name
    return model_id
