import re
import logging

logger = logging.getLogger(__name__)

# Список корней запрещенных слов (чтобы ловить слова в любых падежах)
NSFW_ROOTS = [
    "гола", "голу", "голы", "сиськ", "порн", "эротик", "секс", "ебл", "трах", 
    "пизд", "член", "хуй", "шлюх", "проститут", "изнасил", "педо", "лолит",
    "nude", "naked", "porn", "nsfw", "sex", "boobs", "tits", "vagina", "penis", "xxx"
]

def is_prompt_safe(prompt: str) -> bool:
    """
    Проверяет текст на наличие 18+ контента (Цензура).
    Возвращает True, если текст безопасен, и False, если сработал фильтр.
    """
    if not prompt:
        return True
        
    # Переводим всё в нижний регистр для проверки
    text_lower = prompt.lower()
    
    # Ищем совпадения по корням слов
    for root in NSFW_ROOTS:
        if root in text_lower:
            logger.info(f"🛑 ЦЕНЗУРА: Заблокирован промпт по корню '{root}'.")
            return False
            
    return True
