import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
import config
import config_media
from services import ai_service, sheets_service, conversation_manager, rate_limiter
from services.kie_client import kie_client

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Создаём FastAPI приложение
app = FastAPI(
    title="vnxORACLE Chat API",
    description="AI Sales Consultant для сайта vnxORACLE",
    version="1.0.0"
)

# CORS для работы с фронтендом
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================================
# МОДЕЛИ ДАННЫХ
# =========================================================

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=config.MAX_MESSAGE_LENGTH)
    session_id: Optional[str] = None
    user_data: Optional[dict] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    needs_contact: bool = False

class LeadCaptureRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    contact: str = Field(..., min_length=1, max_length=200)  # Email или Telegram
    company: Optional[str] = Field("", max_length=200)
    problem: Optional[str] = Field("", max_length=2000)
    messages: Optional[List[str]] = []
    session_id: Optional[str] = ""

class LeadCaptureResponse(BaseModel):
    success: bool
    lead_id: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    services: dict

class ImageModelsResponse(BaseModel):
    models: Dict[str, dict]

class ImageGenerateRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=2000)
    model: str = Field(default=config_media.DEFAULT_IMG_MODEL)
    ratio: str = Field(default="square", pattern="^(vertical|horizontal|square)$")

class ImageGenerateResponse(BaseModel):
    success: bool
    image_url: Optional[str] = None
    task_id: Optional[str] = None
    error: Optional[str] = None

# =========================================================
# ENDPOINTS
# =========================================================

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Healthcheck endpoint"""
    return HealthResponse(
        status="ok",
        timestamp=datetime.now().isoformat(),
        services={
            "ai_service": "ok" if ai_service.clients else "degraded",
            "sheets_service": "ok" if sheets_service.service else "disabled",
        }
    )

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, http_request: Request):
    """
    Основной endpoint для чата.

    1. Проверяет rate limit по IP
    2. Получает сообщение пользователя
    3. Генерирует ответ через AI
    4. Сохраняет в историю
    5. Проверяет, нужно ли запросить контакт
    """
    # Защита от накрутки: каждый запрос тратит токены OpenRouter
    rate_limiter.check(http_request)

    try:
        # Создаём или получаем сессию
        if not request.session_id:
            session_id = conversation_manager.create_session()
        else:
            session_id = request.session_id

        # Добавляем сообщение пользователя в историю
        conversation_manager.add_message(
            session_id=session_id,
            role="user",
            content=request.message
        )

        # Лимит на сессию: не даём крутить один диалог бесконечно
        if config.MAX_MESSAGES_PER_SESSION > 0:
            total = len(conversation_manager.get_messages(session_id))
            if total > config.MAX_MESSAGES_PER_SESSION:
                logger.warning(f"🚫 Session limit: {session_id} ({total})")
                raise HTTPException(
                    status_code=429,
                    detail="Диалог получился длинным. Оставьте контакт — консультант продолжит."
                )

        # Получаем полную историю для LLM
        messages = conversation_manager.get_messages(session_id)

        # Добавляем system prompt, если его ещё нет (должен быть первым сообщением)
        if not messages or messages[0].get("role") != "system":
            messages.insert(0, {
                "role": "system",
                "content": config.SALES_CONSULTANT_PROMPT
            })

        # Генерируем ответ через AI
        response_text, tokens = await ai_service.generate_response(
            messages=messages,
            tier="START"  # Для web-чата используем START тариф
        )

        # Добавляем ответ AI в историю
        conversation_manager.add_message(
            session_id=session_id,
            role="assistant",
            content=response_text
        )

        # Проверяем, нужно ли запросить контакт
        needs_contact = conversation_manager.should_capture_contact(session_id)

        logger.info(
            f"✅ Chat response generated: {session_id} | "
            f"Tokens: {tokens} | Needs contact: {needs_contact}"
        )

        return ChatResponse(
            response=response_text,
            session_id=session_id,
            needs_contact=needs_contact
        )

    except HTTPException:
        # 429 и прочие осознанные ответы пробрасываем как есть
        raise
    except Exception as e:
        logger.error(f"❌ Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/lead/capture", response_model=LeadCaptureResponse)
async def capture_lead(request: LeadCaptureRequest, http_request: Request):
    """
    Сохранение контакта лида в Google Sheets и отправка уведомления.
    """
    rate_limiter.check(http_request)

    try:
        # Сохраняем в Google Sheets
        lead_id = await sheets_service.save_lead(
            name=request.name,
            contact=request.contact,
            company=request.company,
            problem=request.problem,
            messages=request.messages,
            session_id=request.session_id
        )

        # Отмечаем в сессии, что контакт захвачен
        if request.session_id:
            conversation_manager.mark_contact_captured(request.session_id)

        success = lead_id is not None

        logger.info(
            f"{'✅' if success else '❌'} Lead capture: "
            f"{request.name} | {request.contact}"
        )

        return LeadCaptureResponse(
            success=success,
            lead_id=lead_id
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Lead capture error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/image/models", response_model=ImageModelsResponse)
async def get_image_models():
    """Список доступных моделей для генерации изображений"""
    return ImageModelsResponse(models=config_media.IMAGE_MODELS)

@app.post("/api/image/generate", response_model=ImageGenerateResponse)
async def generate_image(request: ImageGenerateRequest, http_request: Request):
    """
    Генерация изображения через KIE API

    1. Проверяет rate limit
    2. Отправляет запрос в KIE
    3. Дожидается результата
    4. Возвращает URL готового изображения
    """
    rate_limiter.check(http_request)

    try:
        if not config_media.KIE_API_KEY:
            raise HTTPException(
                status_code=503,
                detail="Image generation service not configured"
            )

        logger.info(f"🎨 Image generation: model={request.model}, ratio={request.ratio}")

        image_url, task_id = await kie_client.generate_image(
            prompt=request.prompt,
            model=request.model,
            ratio=request.ratio
        )

        if image_url:
            logger.info(f"✅ Image generated: {task_id}")
            return ImageGenerateResponse(
                success=True,
                image_url=image_url,
                task_id=task_id
            )
        else:
            logger.error(f"❌ Image generation failed: {task_id}")
            return ImageGenerateResponse(
                success=False,
                error="Generation failed or timed out"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Image generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "vnxORACLE Chat API",
        "version": "1.0.0",
        "status": "online",
        "docs": "/docs"
    }

# =========================================================
# STARTUP / SHUTDOWN
# =========================================================

@app.on_event("startup")
async def startup_event():
    """Действия при запуске"""
    logger.info("🚀 vnxORACLE Chat API starting...")
    logger.info(f"📡 CORS origins: {config.CORS_ORIGINS}")
    logger.info(f"🔑 AI Service: {len(ai_service.clients)} clients loaded")
    logger.info(f"📊 Google Sheets: {'enabled' if sheets_service.service else 'disabled'}")
    logger.info("✅ vnxORACLE Chat API is ONLINE")

@app.on_event("shutdown")
async def shutdown_event():
    """Действия при остановке"""
    logger.info("🛑 vnxORACLE Chat API shutting down...")

# =========================================================
# ЗАПУСК (для разработки)
# =========================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=True
    )
