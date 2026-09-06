import time
import logging
from collections import defaultdict, deque
from fastapi import Request, HTTPException
import config

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Простой in-memory rate limiter по IP (sliding window).

    Защищает /api/chat от накрутки: endpoint публичный, а каждый
    запрос тратит токены OpenRouter.

    ВНИМАНИЕ: счётчик живёт в памяти процесса. При uvicorn --workers N
    фактический лимит равен RATE_LIMIT_REQUESTS * N, потому что воркеры
    не видят счётчиков друг друга. Для строгого лимита нужен Redis либо
    один воркер.
    """

    def __init__(self):
        # ip -> deque[timestamp]
        self._hits: dict[str, deque] = defaultdict(deque)

    def _client_ip(self, request: Request) -> str:
        """
        IP клиента. Заголовки с адресом принимаем только от доверенного прокси:
        их задаёт кто угодно, поэтому при прямом доступе к порту подмена
        обнуляла бы лимит (новый «IP» на каждый запрос).

        За Cloudflare предпочитаем CF-Connecting-IP: он содержит ровно один
        адрес и его выставляет сам Cloudflare, тогда как X-Forwarded-For
        пришедший от клиента Cloudflare лишь дополняет.
        """
        peer = request.client.host if request.client else "unknown"

        if peer not in config.TRUSTED_PROXIES:
            return peer

        cf_ip = request.headers.get("cf-connecting-ip")
        if cf_ip:
            return cf_ip.strip()

        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            # Цепочка вида "client, proxy1, proxy2" — клиент первым
            return forwarded.split(",")[0].strip()

        return peer

    def check(self, request: Request) -> None:
        """Бросает HTTPException 429, если лимит превышен."""
        limit = config.RATE_LIMIT_REQUESTS
        window = config.RATE_LIMIT_WINDOW

        if limit <= 0:
            return

        ip = self._client_ip(request)
        now = time.time()
        hits = self._hits[ip]

        # Выкидываем всё, что вышло из окна
        while hits and now - hits[0] > window:
            hits.popleft()

        if len(hits) >= limit:
            retry_after = int(window - (now - hits[0])) + 1
            logger.warning(f"🚫 Rate limit: {ip} ({len(hits)}/{limit} за {window}с)")
            raise HTTPException(
                status_code=429,
                detail="Слишком много запросов. Подождите немного.",
                headers={"Retry-After": str(retry_after)},
            )

        hits.append(now)

        # Не даём словарю расти бесконечно
        if len(self._hits) > 10000:
            self._cleanup(now, window)

    def _cleanup(self, now: float, window: int) -> None:
        """Убираем IP без активности в окне."""
        stale = [ip for ip, h in self._hits.items() if not h or now - h[-1] > window]
        for ip in stale:
            del self._hits[ip]
        logger.info(f"🧹 Rate limiter: очищено {len(stale)} IP")


rate_limiter = RateLimiter()
