import logging
from typing import List, Dict, Optional
from .base_agent import BaseAgent
from services.ai_service import ai_service
import config

logger = logging.getLogger(__name__)


class SalesAgent(BaseAgent):
    """
    Sales Consultant AI Agent.
    Квалифицирует лиды, отвечает на вопросы, доводит до контакта/демо.
    """

    def __init__(self):
        super().__init__(system_prompt=config.SALES_CONSULTANT_PROMPT)

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        context: Optional[Dict] = None
    ) -> str:
        """
        Генерация ответа через OpenRouter.

        Args:
            messages: История диалога
            context: Дополнительный контекст (не используется пока)

        Returns:
            Ответ агента
        """
        # Подготавливаем сообщения (добавляем system prompt если нужно)
        prepared_messages = self.prepare_messages(messages)

        # Генерируем через AI Service
        response_text, tokens = await ai_service.generate_response(
            messages=prepared_messages,
            tier="START"  # Для web-чата используем START тариф
        )

        logger.info(f"✅ SalesAgent response generated | Tokens: {tokens}")

        return response_text

    def should_escalate(self, message: str) -> bool:
        """
        Проверить, нужно ли передать диалог живому менеджеру.

        Args:
            message: Сообщение пользователя

        Returns:
            True если нужна эскалация
        """
        escalation_triggers = [
            "скидка",
            "discount",
            "недоволен",
            "жалоба",
            "complaint",
            "руководитель",
            "manager",
            "enterprise",
            "100+ сотрудников",
        ]

        message_lower = message.lower()
        return any(trigger in message_lower for trigger in escalation_triggers)


# Глобальный экземпляр
sales_agent = SalesAgent()
