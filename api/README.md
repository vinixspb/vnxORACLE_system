# vnxORACLE Chat API

FastAPI backend для умного chat widget на сайте.

## Структура

```
api/
├── main.py                    # FastAPI app
├── config.py                  # Настройки
├── requirements.txt
├── .env.example
├── agents/
│   ├── __init__.py
│   ├── base_agent.py          # Базовый класс
│   └── sales_agent.py         # Sales consultant
├── services/
│   ├── __init__.py
│   ├── ai_service.py          # OpenRouter integration
│   ├── sheets_service.py      # Google Sheets CRM
│   └── conversation.py        # Управление диалогами
└── prompts/
    └── sales_consultant.txt   # System prompt
```

## Установка

```bash
cd api/
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Настройка

Скопируй `.env.example` → `.env` и заполни:

```env
# OpenRouter API
OPENROUTER_API_KEY_START=your_key_here
OPENROUTER_API_KEY_PRO=your_key_here
OPENROUTER_API_KEY_NEO=your_key_here

# Google Sheets CRM
GOOGLE_CREDENTIALS_JSON=path/to/credentials.json
SPREADSHEET_ID=your_sheet_id

# Telegram Notifications
BOT_TOKEN_ORACLE=your_telegram_bot_token
ADMIN_ID=your_telegram_user_id

# Server
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=https://vinixspb.github.io,http://localhost:5173
```

## Запуск

### Development:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Endpoints

### POST /api/chat
Отправка сообщения в чат.

**Request:**
```json
{
  "message": "Здравствуйте, интересует автоматизация поддержки",
  "session_id": "uuid-v4",
  "user_data": {
    "name": "John Doe",
    "email": "john@example.com"
  }
}
```

**Response:**
```json
{
  "response": "Здравствуйте! Отлично, что обратились...",
  "session_id": "uuid-v4",
  "needs_contact": false
}
```

### POST /api/lead/capture
Сохранение контакта в Google Sheets.

**Request:**
```json
{
  "name": "John Doe",
  "contact": "john@example.com",
  "company": "ACME Inc",
  "problem": "Много тикетов, нужна автоматизация",
  "messages": ["msg1", "msg2"],
  "session_id": "uuid-v4"
}
```

**Response:**
```json
{
  "success": true,
  "lead_id": "row_42"
}
```

### GET /api/health
Healthcheck.

**Response:**
```json
{
  "status": "ok",
  "timestamp": "2026-08-12T10:30:00Z"
}
```

### WS /api/ws/chat/{session_id}
WebSocket для real-time чата (future).

## Google Sheets Setup

1. Создай Google Sheet для CRM
2. Создай Service Account в Google Cloud Console
3. Скачай JSON с credentials
4. Дай доступ Service Account к таблице (Editor)
5. Укажи путь к JSON в `.env`

**Структура таблицы:**

| Timestamp | Name | Contact | Company | Problem | Messages | Status | Next Step |
|-----------|------|---------|---------|---------|----------|--------|-----------|

## Deploy на MATRIXde-n1

```bash
# На сервере
cd /opt/bots/vnxORACLE_system/api/
git pull
pip install -r requirements.txt
sudo systemctl restart vnxoracle-api
```

## Monitoring

Логи:
```bash
sudo journalctl -u vnxoracle-api -f
```

---

**Version:** 1.0  
**Last Updated:** 2026-08-12
