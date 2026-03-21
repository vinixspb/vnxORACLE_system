"""
Реестр текстовых моделей vnxORACLE
Обновлено: Март 2026 (GPT-5.2, Claude 4.6, Qwen 2.5 Coder)
"""

# Базовая модель по умолчанию
DEFAULT_MODEL_ID = "openai/gpt-4o-mini"

# =========================================================
# 💠 ТАРИФ START (Базовые модели)
# =========================================================
MODELS_START = [
    ("⚡️ GPT-4o Mini", "openai/gpt-4o-mini"),
    ("⚡️ Claude 3 Haiku", "anthropic/claude-3-haiku"),
    ("⚡️ Gemini Flash 1.5", "google/gemini-1.5-flash"),
    ("🆓 Llama 3.1 (Free)", "meta-llama/llama-3.1-8b-instruct:free")
]

# =========================================================
# ⚡️ ТАРИФ PRO (Флагманы + Новинки 2026)
# =========================================================
MODELS_PRO = [
    ("🧠 GPT-4o (Флагман)", "openai/gpt-4o"),
    ("🆕 GPT-5.2 (Новинка)", "openai/gpt-5.2"),  # 🔥 НОВИНКА МАРТ 2026
    ("🆕 Claude 4.5 Sonnet", "anthropic/claude-4.5-sonnet"),  # 🔥 НОВИНКА
    ("🧠 Gemini Pro 1.5", "google/gemini-1.5-pro"),
    ("💻 Qwen 2.5 Coder 32B", "qwen/qwen-2.5-coder-32b-instruct"),
    ("🎯 DeepSeek V3", "deepseek/deepseek-chat")
]

# =========================================================
# 🧬 ТАРИФ NEO (Максимальные мощности)
# =========================================================
MODELS_NEO = [
    ("👑 Claude 4.6 Opus", "anthropic/claude-4.6-opus"),  # 🔥 САМАЯ МОЩНАЯ
    ("👑 GPT-5.3 Codex", "openai/gpt-5.3-codex"),  # 🔥 ДЛЯ ПРОГРАММИРОВАНИЯ
    ("👑 Gemini Ultra 1.5", "google/gemini-1.5-ultra"),
    ("🧮 O3 Mini (Reasoning)", "openai/o3-mini"),
    ("🧮 Claude 4.6 Sonnet", "anthropic/claude-4.6-sonnet")
]

# =========================================================
# 🛡 ПРОВЕРКА ДОСТУПА
# =========================================================
def is_model_allowed(tariff: str, model_id: str) -> bool:
    """Проверяет, может ли пользователь с данным тарифом использовать модель"""
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
    """Возвращает красивое имя модели для отображения"""
    all_models = MODELS_START + MODELS_PRO + MODELS_NEO
    for display_name, id_name in all_models:
        if id_name == model_id:
            return display_name
    return model_id  # Если не нашли, возвращаем ID

def get_models_for_tariff(tariff: str) -> list:
    """Возвращает список доступных моделей для тарифа"""
    if tariff == 'START':
        return MODELS_START
    elif tariff == 'PRO':
        return MODELS_START + MODELS_PRO
    elif tariff in ['NEO', 'ARCHITECT']:
        return MODELS_START + MODELS_PRO + MODELS_NEO
    return []
