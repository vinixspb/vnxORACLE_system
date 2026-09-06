# 🚀 vnxORACLE API Deployment Guide

## Архитектура системы

```
┌─────────────────────────────────────────────────┐
│              USERS                              │
├──────────────┬──────────────────────────────────┤
│  Telegram    │  Website (motionsites.ai)        │
└──────┬───────┴──────────────┬───────────────────┘
       │                      │
       ▼                      ▼
┌──────────────────┐   ┌──────────────────┐
│  Telegram Bot    │   │   Web API        │
│  (vnx-oracle)    │   │ (vnx-oracle-api) │
│  Port: -         │   │  Port: 8000      │
└──────┬───────────┘   └──────┬───────────┘
       │                      │
       └──────────┬───────────┘
                  ▼
         ┌─────────────────┐
         │   OpenRouter    │
         │   AI Engine     │
         └─────────────────┘
                  │
         ┌────────┴─────────┐
         │  Google Sheets   │
         │    (CRM/Leads)   │
         └──────────────────┘
```

## 📋 Что будет установлено

1. **FastAPI сервер** - HTTP API для веб-чата
2. **Systemd service** - автозапуск API при перезагрузке сервера
3. **Nginx proxy** - безопасное проксирование с SSL и CORS
4. **Логирование** - `/var/log/vnxoracle-api/`

## ⚠️ Важно: Не сломаем существующий бот

- Telegram Bot (`/opt/vnxORACLE_system/bot`) - **НЕ ТРОГАЕМ**
- API (`/opt/vnxORACLE_system/api`) - новый сервис, независимый

Оба используют общий OpenRouter ключ, но работают отдельно.

## 🔧 Установка на сервер

### Шаг 1: Подключение к серверу

```bash
ssh root@your-server-ip
```

### Шаг 2: Переход в директорию проекта

```bash
cd /opt/vnxORACLE_system
```

### Шаг 3: Обновление кода (если нужно)

```bash
git pull origin main
```

### Шаг 4: Проверка .env файла

```bash
cd api
cat .env
```

**Обязательные переменные:**
- `OPENROUTER_API_KEY_START` - ключ OpenRouter
- `GOOGLE_CREDENTIALS_JSON` - JSON с credentials Google Sheets
- `SPREADSHEET_ID` - ID таблицы для сохранения лидов
- `BOT_TOKEN_ORACLE` - токен Telegram бота (для уведомлений)
- `ADMIN_ID` - ваш Telegram ID

Если файла нет:
```bash
cp .env.example .env
nano .env
```

### Шаг 5: Запуск установки

```bash
chmod +x deploy/install.sh
./deploy/install.sh
```

Скрипт автоматически:
- ✅ Создаст виртуальное окружение
- ✅ Установит зависимости
- ✅ Создаст директорию для логов
- ✅ Установит systemd service
- ✅ Проверит конфигурацию

### Шаг 6: Настройка nginx

#### Вариант A: Выделенный поддомен (рекомендуется)

1. Создать A-запись для `api.vnxoracle.com` → IP сервера
2. Получить SSL сертификат:
```bash
sudo certbot --nginx -d api.vnxoracle.com
```
3. Установить конфигурацию:
```bash
sudo cp deploy/nginx.conf /etc/nginx/sites-available/vnxoracle-api
sudo ln -s /etc/nginx/sites-available/vnxoracle-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### Вариант B: Использовать существующий домен

Если у вас уже есть `vnxoracle.com` с nginx, добавьте в существующий server block:

```nginx
location /api/ {
    proxy_pass http://127.0.0.1:8000/;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    # CORS для сайта
    add_header Access-Control-Allow-Origin "*" always;
    add_header Access-Control-Allow-Methods "GET, POST, OPTIONS" always;
    add_header Access-Control-Allow-Headers "Content-Type, Authorization" always;
}
```

Затем:
```bash
sudo nginx -t
sudo systemctl reload nginx
```

### Шаг 7: Запуск API

```bash
sudo systemctl start vnx-oracle-api
sudo systemctl enable vnx-oracle-api  # Автозапуск
```

### Шаг 8: Проверка работы

```bash
# Статус
sudo systemctl status vnx-oracle-api

# Логи
sudo journalctl -u vnx-oracle-api -f

# HTTP тест
curl http://localhost:8000/api/health

# Должно вернуть:
# {"status":"ok","timestamp":"2024-...","services":{...}}
```

## 📊 Управление API

### Команды systemctl

```bash
# Запуск
sudo systemctl start vnx-oracle-api

# Остановка
sudo systemctl stop vnx-oracle-api

# Перезапуск
sudo systemctl restart vnx-oracle-api

# Статус
sudo systemctl status vnx-oracle-api

# Логи (real-time)
sudo journalctl -u vnx-oracle-api -f

# Логи (последние 100 строк)
sudo journalctl -u vnx-oracle-api -n 100
```

### Добавление алиасов в .bashrc

Добавьте в `/root/.bashrc` (или `~/.bashrc`):

```bash
# --- vnxORACLE API ---
alias oracle-api-cd='cd /opt/vnxORACLE_system/api'
alias oracle-api-restart='systemctl restart vnx-oracle-api && journalctl -u vnx-oracle-api -f'
alias oracle-api-logs='journalctl -u vnx-oracle-api -f'
alias oracle-api-stop='systemctl stop vnx-oracle-api'
alias oracle-api-start='systemctl start vnx-oracle-api'
alias oracle-api-status='systemctl status vnx-oracle-api'
```

Затем:
```bash
source ~/.bashrc
```

Теперь можно использовать:
```bash
oracle-api-restart  # Перезапуск с логами
oracle-api-logs     # Просмотр логов
```

## 🔄 Обновление API

```bash
# 1. Переход в директорию
cd /opt/vnxORACLE_system

# 2. Обновление кода
git pull origin main

# 3. Обновление зависимостей (если изменились)
cd api
source venv/bin/activate
pip install -r requirements.txt --upgrade

# 4. Перезапуск сервиса
sudo systemctl restart vnx-oracle-api

# 5. Проверка логов
sudo journalctl -u vnx-oracle-api -f
```

## 🔍 Проверка работы с сайтом

### Тест из браузера

1. Откройте сайт: https://motionsites.ai/vnxoracle
2. Откройте DevTools (F12) → Console
3. Проверьте запросы к API

### Тест через curl

```bash
# Health check
curl https://api.vnxoracle.com/api/health

# Chat request (test)
curl -X POST https://api.vnxoracle.com/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Привет! Расскажи про AI-ботов для бизнеса"
  }'
```

### Ожидаемый ответ:

```json
{
  "response": "Здравствуйте! Отлично, что обратились...",
  "session_id": "uuid-here",
  "needs_contact": false
}
```

## 🐛 Troubleshooting

### API не стартует

```bash
# Проверка логов
sudo journalctl -u vnx-oracle-api -n 100

# Ручной запуск для диагностики
cd /opt/vnxORACLE_system/api
source venv/bin/activate
python main.py
```

### Ошибка "Address already in use"

```bash
# Найти процесс на порту 8000
sudo lsof -i :8000

# Убить процесс
sudo kill -9 <PID>
```

### CORS ошибки на сайте

Проверьте nginx конфигурацию:
```bash
sudo nginx -t
sudo cat /etc/nginx/sites-enabled/vnxoracle-api | grep -A 5 "Access-Control"
```

Должны быть headers:
```
Access-Control-Allow-Origin "*"
Access-Control-Allow-Methods "GET, POST, OPTIONS"
Access-Control-Allow-Headers "Content-Type, Authorization"
```

### OpenRouter ошибки

```bash
# Проверка ключа в .env
cd /opt/vnxORACLE_system/api
grep OPENROUTER_API_KEY_START .env

# Тест ключа
curl -X POST https://openrouter.ai/api/v1/chat/completions \
  -H "Authorization: Bearer sk-or-v1-..." \
  -H "Content-Type: application/json" \
  -d '{
    "model": "openai/gpt-4o-mini",
    "messages": [{"role": "user", "content": "test"}]
  }'
```

## 📈 Monitoring Dashboard

Добавьте в конец `.bashrc` для quick status:

```bash
alias vnx-status='echo "=== vnxORACLE STATUS ===" && \
  printf "%-15s | %s\n" "Telegram Bot" "$(systemctl is-active vnx-oracle)" && \
  printf "%-15s | %s\n" "Web API" "$(systemctl is-active vnx-oracle-api)" && \
  echo "======================="'
```

Теперь команда `vnx-status` покажет статус обоих сервисов.

## 🔒 Security Checklist

- [ ] SSL сертификат установлен (certbot)
- [ ] Firewall настроен (ufw allow 80,443)
- [ ] Rate limiting в nginx (30 req/min)
- [ ] .env файл имеет права 600 (`chmod 600 .env`)
- [ ] Логи ротируются (logrotate)
- [ ] Google Sheets credentials защищены
- [ ] CORS настроен только для нужных доменов (production)

## 📞 Support

- **Telegram Bot logs:** `oracle-logs`
- **Web API logs:** `oracle-api-logs`
- **Architect:** @vinixspb

---

**Версия:** 1.0
**Дата:** 2024-09-06
**Проект:** vnxORACLE System
