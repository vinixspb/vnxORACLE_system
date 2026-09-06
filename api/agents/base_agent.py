from abc import ABC, abstractmethod
from typing import List, Dict, Optional


class BaseAgent(ABC):
    """
    Базовый класс для всех AI-агентов.
    Определяет общий интерфейс.
    """

    def __init__(self, system_prompt: str):
        self.system_prompt = system_prompt

    @abstractmethod
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        context: Optional[Dict] = None
    ) -> str:
        """
        Генерация ответа на основе истории сообщений.

        Args:
            messages: История [{role, content}]
            context: Дополнительный контекст (user_data, metadata)

        Returns:
            Ответ агента
        """
        pass

    def prepare_messages(
        self,
        user_messages: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        """
        Подготовить сообщения для LLM (добавить system prompt).

        Args:
            user_messages: История диалога

        Returns:
            Полный список сообщений с system prompt
        """
        if not user_messages:
            return [{"role": "system", "content": self.system_prompt}]

        # Если первое сообщение не system — добавляем
        if user_messages[0].get("role") != "system":
            return [
                {"role": "system", "content": self.system_prompt},
                *user_messages
            ]

        return user_messages
