# vnxORACLE System

> **Cognitive AI Ecosystem for Business**

Экосистема искусственного интеллекта vnxORACLE — комплексная платформа, объединяющая Telegram-бота с AI-возможностями и современный landing page.

---

## 🏗 Структура проекта

```
vnxORACLE_system/
├── bot/          # 🤖 Telegram Bot (Python)
├── landing/      # 🌐 Landing Page (React + Vite)
├── docs/         # 📚 Документация
└── .github/      # CI/CD workflows
```

---

## 🤖 Bot — Telegram AI Bot

**Стек:** Python 3.10+, aiogram 3.x, SQLite

Многофункциональный Telegram-бот с AI-возможностями:
- 💬 Генерация текстов (ChatGPT, Claude, Gemini)
- 🎨 Создание изображений (DALL-E, Midjourney, Stable Diffusion)
- 🎤 Распознавание и синтез речи
- 🎬 Обработка видео

**Запуск:**
```bash
cd bot
pip install -r requirements.txt
cp .env.example .env  # настроить токены
python main.py
```

[📖 Подробная документация](./bot/README.md)

---

## 🌐 Landing — Modern Web Interface

**Стек:** React 19, Vite, Framer Motion, Lucide Icons

Современный full-screen hero landing с видео-фоном и плавными анимациями.

**Запуск:**
```bash
cd landing
npm install
npm run dev        # http://localhost:5173
npm run build      # production build
```

[📖 Подробная документация](./landing/README.md)

---

## 🚀 Деплой

- **Bot:** Развернут на сервере MATRIXde-n1 (`/opt/bots/lavkagames`)
- **Landing:** GitHub Pages / Vercel (планируется)

---

## 📚 Документация

- [Архитектура системы](./docs/ARCHITECTURE.md)
- [Инструкции по деплою](./docs/DEPLOYMENT.md)
- [Contributing Guidelines](./docs/CONTRIBUTING.md)

---

## 🔧 Технологии

**Backend:** Python, aiogram, SQLite, OpenRouter API  
**Frontend:** React, Vite, Framer Motion, CSS Grid  
**Infrastructure:** Linux, systemd, GitHub Actions

---

## 📄 Лицензия

Proprietary — vnxORACLE Team © 2024-2026

---

## 👥 Команда

Разработка и поддержка: vnxORACLE Development Team

**GitHub:** [github.com/vinixspb/vnxORACLE_system](https://github.com/vinixspb/vnxORACLE_system)
