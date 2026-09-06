import logging
from openai import AsyncOpenAI, APIStatusError
import config

logger = logging.getLogger(__name__)

class AIService:
    """
    Сервис для работы с AI через OpenRouter.
    Переиспользует логику из bot/services/ai_engine.py
    """

    def __init__(self):
        self.clients = {}

        # Проверяем ключи
        def check(k):
            return "OK" if k and len(k) > 10 else "MISSING"

        logger.info(
            f"🔑 Keys Status: START={check(config.OPENROUTER_API_KEY_START)} | "
            f"PRO={check(config.OPENROUTER_API_KEY_PRO)}"
        )

        # Инициализируем клиенты
        if config.OPENROUTER_API_KEY_START:
            self.clients["START"] = AsyncOpenAI(
                base_url=config.TEXT_BASE_URL,
                api_key=config.OPENROUTER_API_KEY_START
            )

        if config.OPENROUTER_API_KEY_PRO:
            self.clients["PRO"] = AsyncOpenAI(
                base_url=config.TEXT_BASE_URL,
                api_key=config.OPENROUTER_API_KEY_PRO
            )
        else:
            self.clients["PRO"] = self.clients.get("START")

        if config.OPENROUTER_API_KEY_NEO:
            self.clients["NEO"] = AsyncOpenAI(
                base_url=config.TEXT_BASE_URL,
                api_key=config.OPENROUTER_API_KEY_NEO
            )
        else:
            self.clients["NEO"] = self.clients.get("PRO") or self.clients.get("START")

    def _get_client(self, tier: str = "START"):
        """Получить клиента по тарифу"""
        client = self.clients.get(tier)
        if not client:
            return self.clients.get("START")
        return client

    async def generate_response(
        self,
        messages: list,
        model: str = None,
        tier: str = "START"
    ) -> tuple[str, int]:
        """
        Генерация ответа через OpenRouter.

        Args:
            messages: История сообщений [{role, content}]
            model: ID модели (по умолчанию из config)
            tier: Тариф (START/PRO/NEO)

        Returns:
            (response_text, tokens_used)
        """
        client = self._get_client(tier)
        if not client:
            return "⚠️ Ошибка системы: нет API ключей.", 0

        if model is None:
            model = config.DEFAULT_MODEL

        # Survival loop (5 попыток)
        max_retries = 5
        attempt = 0
        current_model = model

        while attempt < max_retries:
            attempt += 1
            try:
                if attempt > 1:
                    logger.warning(f"🔄 Retry {attempt}/{max_retries}: {current_model}")

                response = await client.chat.completions.create(
                    model=current_model,
                    messages=messages,
                    temperature=config.AI_TEMPERATURE,
                    extra_headers={
                        "HTTP-Referer": "https://vnxoracle.com",
                        "X-Title": "vnxORACLE Chat Widget"
                    }
                )

                answer = response.choices[0].message.content
                tokens = response.usage.total_tokens

                return answer, tokens

            except APIStatusError as e:
                error_code = e.status_code
                logger.warning(f"⚠️ Fail {attempt} ({current_model}): {error_code} - {e}")

                if attempt >= max_retries:
                    logger.error("❌ All retries failed")
                    return (
                        "⚠️ Все каналы перегружены. Повторите запрос позже.",
                        0
                    )

                # Fallback на бесплатные модели
                if error_code in [402, 401]:
                    current_model = "google/gemma-2-9b-it:free"
                    logger.info(f"🔄 Switching to free model: {current_model}")

                continue

            except Exception as e:
                logger.error(f"Critical error: {e}")
                return "⚠️ Критическая ошибка.", 0

        return "⚠️ Нет ответа.", 0


# Глобальный экземпляр
ai_service = AIService()
