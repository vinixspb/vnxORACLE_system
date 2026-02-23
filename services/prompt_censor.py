import re

# Список корней запрещенных слов (чтобы ловить слова в любых падежах)
NSFW_ROOTS = [
    "гола", "голу", "голы", "сиськ", "порн", "эротик", "секс", "ебл", "трах", 
    "пизд", "член", "хуй", "шлюх", "проститут", "изнасил",
    "nude", "naked", "porn", "nsfw", "sex", "boobs", "tits", "vagina", "penis", "xxx"
]

def is_prompt_safe(prompt: str) -> bool:
    """
    Проверяет текст на наличие 18+ контента.
    Возвращает True, если текст безопасен, и False, если сработал фильтр.
    """
    if not prompt:
        return True
        
    # Переводим всё в нижний регистр для проверки
    text_lower = prompt.lower()
    
    # Ищем совпадения по корням слов
    for root in NSFW_ROOTS:
        if root in text_lower:
            return False
            
    return True
