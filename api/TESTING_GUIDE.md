# 🚀 Quick Start — Backend Testing Guide

**Цель:** Проверить, что FastAPI backend работает корректно перед созданием frontend.

---

## Шаг 1: Установка зависимостей

### Windows (PyCharm):

```bash
# Перейти в директорию API
cd C:\Users\Admin\PycharmProjects\vnxORACLE_system\api

# Создать виртуальное окружение
py -m venv venv

# Активировать
venv\Scripts\activate

# Установить зависимости
pip install -r requirements.txt
```

### Проверка установки:
```bash
pip list | findstr fastapi
# Должен показать: fastapi==0.115.0
```

---

## Шаг 2: Настройка .env

### Создать файл `.env`:

```bash
# Скопировать шаблон
copy .env.example .env

# Отредактировать в PyCharm или любом редакторе
```

### Минимальная конфигурация для тестирования:

```env
# OpenRouter API (ОБЯЗАТЕЛЬНО)
OPENROUTER_API_KEY_START=sk-or-v1-your-key-here

# Google Sheets (ОПЦИОНАЛЬНО для первого теста)
# GOOGLE_CREDENTIALS_JSON=path/to/credentials.json
# SPREADSHEET_ID=your_sheet_id

# Telegram Notifications (ОПЦИОНАЛЬНО)
# BOT_TOKEN_ORACLE=123456789:ABC...
# ADMIN_ID=123456789

# Server Configuration
API_HOST=127.0.0.1
API_PORT=8000
CORS_ORIGINS=http://localhost:5173,https://vinixspb.github.io

# AI Configuration
DEFAULT_MODEL=openai/gpt-4o-mini
AI_TEMPERATURE=0.7
TEXT_BASE_URL=https://openrouter.ai/api/v1
```

**ВАЖНО:** Нужен хотя бы `OPENROUTER_API_KEY_START` для работы AI.

---

## Шаг 3: Запуск сервера

### Вариант A: Через PyCharm

1. Открыть `api/main.py` в PyCharm
2. Правый клик → Run 'main'
3. Или снизу в терминале PyCharm:
   ```bash
   cd api
   venv\Scripts\activate
   py main.py
   ```

### Вариант B: Через командную строку

```bash
cd C:\Users\Admin\PycharmProjects\vnxORACLE_system\api
venv\Scripts\activate
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### Ожидаемый вывод:

```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     🚀 vnxORACLE Chat API starting...
INFO:     📡 CORS origins: ['http://localhost:5173', ...]
INFO:     🔑 AI Service: 1 clients loaded
INFO:     📊 Google Sheets: disabled (or enabled)
INFO:     ✅ vnxORACLE Chat API is ONLINE
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

---

## Шаг 4: Тестирование endpoints

### 1. Healthcheck (базовая проверка)

**Browser:**
Открыть в браузере: http://127.0.0.1:8000/api/health

**Ожидаемый ответ:**
```json
{
  "status": "ok",
  "timestamp": "2026-08-12T20:30:00.123456",
  "services": {
    "ai_service": "ok",
    "sheets_service": "disabled"
  }
}
```

### 2. Root endpoint

**Browser:**
http://127.0.0.1:8000/

**Ожидаемый ответ:**
```json
{
  "service": "vnxORACLE Chat API",
  "version": "1.0.0",
  "status": "online",
  "docs": "/docs"
}
```

### 3. Interactive API Docs (Swagger)

**Browser:**
http://127.0.0.1:8000/docs

Должен открыться Swagger UI с тремя endpoints:
- `POST /api/chat`
- `POST /api/lead/capture`
- `GET /api/health`

---

## Шаг 5: Тестирование чата через Swagger

### В браузере открыть: http://127.0.0.1:8000/docs

### Тест 1: Первое сообщение

1. Раскрыть `POST /api/chat`
2. Нажать **"Try it out"**
3. В Request body ввести:

```json
{
  "message": "Здравствуйте, интересует автоматизация поддержки",
  "session_id": null,
  "user_data": null
}
```

4. Нажать **"Execute"**

**Ожидаемый ответ:**
```json
{
  "response": "Здравствуйте! Отлично, что обратились. Расскажите, какие вопросы чаще всего задают ваши клиенты?...",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "needs_contact": false
}
```

### Тест 2: Продолжение диалога

Использовать **тот же session_id** из предыдущего ответа:

```json
{
  "message": "У нас 100+ обращений в день про доставку",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_data": null
}
```

**Ожидаемый ответ:**
```json
{
  "response": "Понимаю, 100+ обращений — серьёзная нагрузка...",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "needs_contact": false
}
```

### Тест 3: Третье сообщение (должно предложить контакт)

```json
{
  "message": "Сколько это стоит?",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_data": null
}
```

**Ожидаемый ответ:**
```json
{
  "response": "Тариф зависит от нагрузки. Для 100+ обращений...",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "needs_contact": true  <-- TRUE после 2-3 сообщений
}
```

---

## Шаг 6: Тестирование захвата лида

### В Swagger: `POST /api/lead/capture`

**Request body:**
```json
{
  "name": "Иван Тестовый",
  "contact": "ivan@test.com",
  "company": "Test Corp",
  "problem": "Много тикетов, нужна автоматизация",
  "messages": [
    "Здравствуйте, интересует автоматизация",
    "У нас 100+ обращений в день",
    "Сколько это стоит?"
  ],
  "session_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Ожидаемый ответ:**
```json
{
  "success": true,
  "lead_id": "Sheet1!A2:H2"
}
```

**Что произойдёт:**
- ✅ Запись в Google Sheets (если настроено)
- ✅ Уведомление админу в Telegram (если настроено)
- ✅ Лог в консоли сервера

**Если Google Sheets не настроен:**
```json
{
  "success": false,
  "lead_id": null
}
```
Это нормально для первого теста — главное, что endpoint работает.

---

## Шаг 7: Проверка логов

### В консоли где запущен сервер должны быть:

```
INFO: ✅ Chat response generated: 550e8400-... | Tokens: 156 | Needs contact: false
INFO: ✅ Chat response generated: 550e8400-... | Tokens: 203 | Needs contact: false
INFO: ✅ Chat response generated: 550e8400-... | Tokens: 287 | Needs contact: true
INFO: ✅ Lead capture: Иван Тестовый | ivan@test.com
```

---

## Возможные проблемы и решения

### Проблема 1: "ModuleNotFoundError: No module named 'fastapi'"

**Решение:**
```bash
# Убедиться что venv активирован
venv\Scripts\activate

# Переустановить зависимости
pip install -r requirements.txt
```

### Проблема 2: "⚠️ Ошибка системы: нет API ключей"

**Решение:**
- Проверить что `.env` файл создан
- Проверить что `OPENROUTER_API_KEY_START` заполнен
- Перезапустить сервер

### Проблема 3: Google Sheets не работает

**Решение (опционально):**
Это нормально для первого теста. Google Sheets нужен только для production.

Чтобы настроить:
1. Создать Service Account в Google Cloud Console
2. Скачать JSON credentials
3. Дать доступ Service Account к Google Sheet
4. Указать пути в `.env`

### Проблема 4: Сервер не запускается, порт занят

**Решение:**
```bash
# Использовать другой порт
uvicorn main:app --reload --host 127.0.0.1 --port 8001
```

---

## ✅ Checklist готовности

После выполнения всех шагов, должны быть выполнены:

- [ ] Сервер запускается без ошибок
- [ ] `/api/health` возвращает `"status": "ok"`
- [ ] `POST /api/chat` генерирует ответы через AI
- [ ] Диалог работает (session_id сохраняется)
- [ ] После 2-3 сообщений `needs_contact: true`
- [ ] `POST /api/lead/capture` работает (хотя бы логируется)
- [ ] Swagger docs доступны на `/docs`

---

## Следующий шаг

После успешного тестирования backend переходим к **Этапу A: Frontend (Chat Widget)**.

---

**Готов к тестированию?** Сообщи если что-то не работает!
