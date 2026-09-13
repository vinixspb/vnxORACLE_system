# MATRIXde-n1 Server Infrastructure — Диагностика и План SSL

**Дата:** 2026-09-13  
**Цель:** Установка SSL сертификата для api.vnxoracle.uk без нарушения текущей инфраструктуры

---

## 📊 Текущее состояние инфраструктуры

### Владение портами (актуально на 13.09.2026)

| Порт | Владелец | Что обслуживает | Статус |
|---|---|---|---|
| **80** | **nginx (systemd)** | helloneo.uk, games.helloneo.uk, vnxoracle.uk, api.helloneo.uk, **api.vnxoracle.uk** | ✅ Работает |
| **443** | **docker (mtg-proxy)** | MTProto-прокси VPN | ⚠️ **НЕ ТРОГАТЬ** |
| **9443** | **caddy** (ручной запуск) | selfsteal-декой для Reality VPN | ✅ Работает |
| **8445** | **remnanode** | GO-приёмник Reality (каскады T1/B1) | ✅ Работает |
| **8001** | **uvicorn** (vnx-oracle-api.service) | vnxORACLE Chat API (за nginx reverse proxy) | ✅ Работает |
| **2222** | **remnanode** | API ноды для панели | ✅ Работает |

### Конфигурация nginx для api.vnxoracle.uk

**Файл:** `/etc/nginx/sites-available/vnxoracle-api-uk`  
**Симлинк:** `/etc/nginx/sites-enabled/vnxoracle-api-uk`

```nginx
server {
    listen 80;
    listen [::]:80;
    server_name api.helloneo.uk api.vnxoracle.uk;

    access_log /var/log/nginx/vnxoracle-api-uk-access.log;
    error_log  /var/log/nginx/vnxoracle-api-uk-error.log;

    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        proxy_connect_timeout 120s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }
}
```

**Проблема:** Нет SSL блока (443) — виджет на HTTPS сайте не может обращаться к HTTP API.

---

## 🚨 Критические ограничения

1. **Порт 443 занят Docker контейнером** — nginx НЕ МОЖЕТ слушать 443 напрямую
2. **Caddy мёртв для веб-сервисов** — обслуживает только selfsteal на 9443
3. **Инцидент 12.09.2026:** nginx занял порт 80 → Caddy упал в restart loop → 6 дней простоя
4. **VPN-система критична** — любые сетевые правки могут сломать маскировку Reality

---

## ✅ План установки SSL (безопасный вариант)

### Вариант 1: nginx на нестандартном порту + Cloudflare Proxy (РЕКОМЕНДУЕТСЯ)

**Идея:** nginx слушает HTTPS на порту **8443** (свободен), Cloudflare проксирует 443 → 8443

#### Шаги:

1. **Получить Cloudflare Origin Certificate:**
   - Cloudflare Dashboard → SSL/TLS → Origin Server
   - Create Certificate (15 лет)
   - Сохранить на сервер:
     ```bash
     /etc/ssl/cloudflare/api.vnxoracle.uk.crt
     /etc/ssl/cloudflare/api.vnxoracle.uk.key
     ```

2. **Обновить nginx config:**
   ```nginx
   server {
       listen 8443 ssl http2;
       listen [::]:8443 ssl http2;
       server_name api.vnxoracle.uk;

       ssl_certificate /etc/ssl/cloudflare/api.vnxoracle.uk.crt;
       ssl_certificate_key /etc/ssl/cloudflare/api.vnxoracle.uk.key;
       ssl_protocols TLSv1.2 TLSv1.3;
       ssl_ciphers HIGH:!aNULL:!MD5;

       access_log /var/log/nginx/vnxoracle-api-uk-ssl-access.log;
       error_log  /var/log/nginx/vnxoracle-api-uk-ssl-error.log;

       location / {
           proxy_pass http://127.0.0.1:8001;
           proxy_http_version 1.1;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto https;

           proxy_connect_timeout 120s;
           proxy_send_timeout 120s;
           proxy_read_timeout 120s;
       }
   }

   # Редирект HTTP → HTTPS (опционально)
   server {
       listen 80;
       listen [::]:80;
       server_name api.vnxoracle.uk;
       return 301 https://$host$request_uri;
   }
   ```

3. **Настроить Cloudflare:**
   - Переключить **api.vnxoracle.uk** на **Proxied** (оранжевая тучка)
   - SSL/TLS Mode: **Full (strict)**
   - В DNS → Cloudflare автоматически проксирует 443 → 8443

4. **Перезапустить nginx:**
   ```bash
   nginx -t && systemctl reload nginx
   ```

**Плюсы:**
- ✅ Не трогает порт 443 (Docker продолжает работать)
- ✅ Cloudflare выдаёт сертификат за 2 минуты
- ✅ DDoS защита и кеширование от Cloudflare
- ✅ Автопродление не требуется (сертификат на 15 лет)

**Минусы:**
- ⚠️ Зависимость от Cloudflare Proxy (если Proxied отключить — HTTPS сломается)
- ⚠️ Origin Certificate не доверяется браузерами напрямую

---

### Вариант 2: Let's Encrypt + nginx на порту 8443 (без Cloudflare Proxy)

**Идея:** Получить публичный SSL от Let's Encrypt, nginx слушает 8443, но DNS остаётся **DNS only**

#### Проблема:
Let's Encrypt требует либо:
- HTTP challenge на порту 80 (занят nginx, но можно через `/.well-known/acme-challenge/`)
- DNS challenge (требует API токен Cloudflare)

#### Шаги (если нужен публичный SSL):

1. **Установить certbot:**
   ```bash
   apt install certbot python3-certbot-nginx -y
   ```

2. **Получить сертификат через HTTP challenge:**
   ```bash
   certbot certonly --webroot -w /var/www/html \
     -d api.vnxoracle.uk \
     --email admin@vnxoracle.uk \
     --agree-tos --non-interactive
   ```

3. **Настроить nginx на 8443:**
   ```nginx
   server {
       listen 8443 ssl http2;
       server_name api.vnxoracle.uk;

       ssl_certificate /etc/letsencrypt/live/api.vnxoracle.uk/fullchain.pem;
       ssl_certificate_key /etc/letsencrypt/live/api.vnxoracle.uk/privkey.pem;
       include /etc/letsencrypt/options-ssl-nginx.conf;

       # ... остальное как в Варианте 1
   }
   ```

4. **Настроить автопродление:**
   ```bash
   systemctl enable certbot.timer
   ```

**Проблема:** Порт 8443 не стандартный для HTTPS → браузеры будут ругаться на `https://api.vnxoracle.uk:8443`

---

## 🎯 Рекомендация: Вариант 1 (Cloudflare Origin Certificate)

**Почему:**
1. Не трогает порт 443 (VPN продолжает работать)
2. Быстро (5 минут настройки)
3. Не требует автопродления
4. Cloudflare скрывает нестандартный порт 8443 от клиентов

**Следующий шаг:**
Получить согласие на переключение **api.vnxoracle.uk** в режим **Proxied** в Cloudflare.

---

## 📝 Связанные документы

- [matrixde-n1-ports.md](C:\Users\Admin\.claude\projects\C--Users-Admin\memory\matrixde-n1-ports.md) — реестр портов
- [vnxoracle-deploy-state.md](C:\Users\Admin\.claude\projects\C--Users-Admin\memory\vnxoracle-deploy-state.md) — история деплоя
- [ECOSYSTEM.md](ECOSYSTEM.md) — архитектура vnxORACLE

---

**Дата создания:** 2026-09-13  
**Автор:** vnxORACLE DevOps Team
