# 🎯 TODO: Следующие шаги разработки

**Текущий статус:** Backend API готов ✅  
**Следующий этап:** Frontend Chat Widget

---

## 🔧 Этап B: Backend Testing (ТЕКУЩИЙ)

### Быстрый старт:

```bash
# 1. Перейти в API директорию
cd C:\Users\Admin\PycharmProjects\vnxORACLE_system\api

# 2. Создать виртуальное окружение (если еще нет)
py -m venv venv

# 3. Активировать
venv\Scripts\activate

# 4. Установить зависимости
pip install -r requirements.txt

# 5. Создать .env файл и добавить OPENROUTER_API_KEY_START
copy .env.example .env
# Отредактировать .env в текстовом редакторе

# 6. Запустить сервер
py main.py
# или
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### Проверка:
- Открыть в браузере: http://127.0.0.1:8000/docs
- Протестировать `/api/chat` через Swagger UI
- Проверить что ответы генерируются

📖 **Детальный гайд:** `api/TESTING_GUIDE.md`

---

## 🎨 Этап A: Frontend Chat Widget (СЛЕДУЮЩИЙ)

### Задачи:

**1. Создать компонент ChatWidget**

Файл: `landing/src/components/ChatWidget/index.jsx`

```jsx
import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'motion/react'
import { MessageCircle, X, Send } from 'lucide-react'
import './ChatWidget.css'

export default function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false)
  const [messages, setMessages] = useState([])
  const [inputValue, setInputValue] = useState('')
  const [sessionId, setSessionId] = useState(null)
  const [isTyping, setIsTyping] = useState(false)

  // API endpoint
  const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

  // ... implementation
}
```

**2. Дизайн в стиле сайта**

Файл: `landing/src/components/ChatWidget/ChatWidget.css`

```css
/* Glass-morphism style */
.chat-widget {
  position: fixed;
  right: 24px;
  bottom: 24px;
  z-index: 1000;
}

.chat-button {
  width: 60px;
  height: 60px;
  border-radius: 999px;
  background: #38BDF8;
  backdrop-filter: blur(20px);
  /* ... */
}

.chat-window {
  width: 400px;
  height: 600px;
  background: rgba(15, 19, 28, 0.85);
  backdrop-filter: blur(40px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  /* ... */
}
```

**3. API интеграция**

```javascript
// POST /api/chat
const sendMessage = async (message) => {
  const response = await fetch(`${API_URL}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message,
      session_id: sessionId,
      user_data: null
    })
  })
  const data = await response.json()
  return data
}
```

**4. Интеграция в App.jsx**

```jsx
// landing/src/App.jsx
import ChatWidget from './components/ChatWidget'

export default function App() {
  // ... existing code
  
  return (
    <div data-theme={theme}>
      {/* ... existing sections */}
      <ChatWidget />  {/* Добавить в конец */}
    </div>
  )
}
```

**5. Environment Variables**

Файл: `landing/.env.local`

```env
VITE_API_URL=http://127.0.0.1:8000
```

Для production:
```env
VITE_API_URL=https://api.vnxoracle.com
```

### Структура компонента:

```
landing/src/components/ChatWidget/
├── index.jsx               # Main component
├── ChatWidget.css          # Styles
├── ChatButton.jsx          # Floating button
├── ChatWindow.jsx          # Chat container
├── MessageList.jsx         # Messages
├── MessageBubble.jsx       # Single message
├── ChatInput.jsx           # Input field
└── ContactForm.jsx         # Email/Telegram capture
```

### Ключевые фичи:

- ✅ Floating button с пульсацией
- ✅ Glass-morphism дизайн (iOS 26 style)
- ✅ Dark/Light theme sync с сайтом
- ✅ Typing indicator
- ✅ localStorage для истории
- ✅ Плавные анимации (Framer Motion)
- ✅ Responsive (fullscreen на mobile)
- ✅ Contact capture после 2-3 сообщений

---

## 🚀 Этап C: Deploy (ПОСЛЕДНИЙ)

### 1. Backend Deploy на MATRIXde-n1

```bash
# На локальной машине
git add .
git commit -m "Add FastAPI backend for chat widget"
git push origin main

# На сервере MATRIXde-n1
ssh vnxadmin@matrixde-n1.server.com
cd /opt/bots/vnxORACLE_system
git pull origin main

# Setup
cd api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Создать .env с production ключами
nano .env

# Systemd service
sudo nano /etc/systemd/system/vnxoracle-api.service
```

**vnxoracle-api.service:**
```ini
[Unit]
Description=vnxORACLE Chat API
After=network.target

[Service]
Type=simple
User=vnxadmin
WorkingDirectory=/opt/bots/vnxORACLE_system/api
Environment="PATH=/opt/bots/vnxORACLE_system/api/venv/bin"
ExecStart=/opt/bots/vnxORACLE_system/api/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Запуск сервиса
sudo systemctl daemon-reload
sudo systemctl enable vnxoracle-api
sudo systemctl start vnxoracle-api
sudo systemctl status vnxoracle-api

# Проверка логов
sudo journalctl -u vnxoracle-api -f
```

### 2. Frontend Deploy на GitHub Pages

```bash
# landing/.env.production
VITE_API_URL=https://api.vnxoracle.com

# Build
cd landing
npm run build

# Deploy через GitHub Actions (уже настроен)
git add .
git commit -m "Add chat widget to landing"
git push origin main
```

### 3. Nginx Reverse Proxy (на сервере)

```nginx
# /etc/nginx/sites-available/vnxoracle-api

server {
    listen 80;
    server_name api.vnxoracle.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/vnxoracle-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# SSL (Let's Encrypt)
sudo certbot --nginx -d api.vnxoracle.com
```

---

## 📋 Checklist полной готовности

### Backend:
- [ ] Локальное тестирование пройдено
- [ ] `.env` с production ключами готов
- [ ] Deploy на MATRIXde-n1
- [ ] Systemd service работает
- [ ] Nginx proxy настроен
- [ ] SSL сертификат установлен

### Frontend:
- [ ] ChatWidget компонент создан
- [ ] Дизайн соответствует сайту (glass-morphism)
- [ ] API интеграция работает
- [ ] Тестирование в браузере
- [ ] Responsive на mobile
- [ ] Dark/Light theme sync

### Production:
- [ ] GitHub Pages deploy
- [ ] CORS настроен для production domain
- [ ] Google Sheets CRM работает
- [ ] Telegram уведомления работают
- [ ] Monitoring настроен

### Testing:
- [ ] 10+ тестовых диалогов
- [ ] Захват контакта работает
- [ ] Сессии сохраняются
- [ ] Escalation работает (при необходимости)

---

## 🎯 Immediate Actions (прямо сейчас)

### ШАГ 1: Протестировать Backend
```bash
cd api
py main.py
# Открыть http://127.0.0.1:8000/docs
# Протестировать /api/chat через Swagger
```

### ШАГ 2: Если backend работает → создавать Frontend
```bash
cd landing/src/components
mkdir ChatWidget
# Создать файлы компонента
```

### ШАГ 3: После frontend → Deploy
```bash
git add .
git commit -m "Phase 1: MVP Chat Widget complete"
git push origin main
```

---

**Текущий фокус:** Тестирование Backend (Этап B)  
**Следующий шаг:** Создание Chat Widget (Этап A)  
**Финальный шаг:** Deploy на production (Этап C)

---

📝 **Note:** Все детальные инструкции в соответствующих файлах:
- Backend testing: `api/TESTING_GUIDE.md`
- API docs: `api/README.md`
- Project roadmap: `docs/ROADMAP.md`
- Brand identity: `docs/BRAND_IDENTITY.md`
