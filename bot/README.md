# vnxORACLE Telegram Bot

> **AI-Powered Telegram Bot с мультимодальными возможностями**

Telegram-бот на базе aiogram 3.x с интеграцией множества AI-моделей через OpenRouter API.

---

## ✨ Возможности

- 💬 **Текстовая генерация** — ChatGPT, Claude, Gemini, Llama
- 🎨 **Генерация изображений** — DALL-E 3, Midjourney, Stable Diffusion
- 🎤 **Голосовые сообщения** — распознавание и синтез речи
- 🎬 **Обработка видео** — анализ и генерация
- 📊 **База данных** — SQLite для хранения истории и настроек
- 🔐 **Управление доступом** — whitelist пользователей

---

## 🏗 Архитектура

```
bot/
├── main.py              # Точка входа
├── config.py            # Конфигурация (токены, API keys)
├── config_models.py     # Настройки AI-моделей
├── loader.py            # Инициализация bot, dispatcher
├── handlers/            # Обработчики команд и сообщений
│   ├── start.py
│   ├── text_handler.py
│   ├── voice_handler.py
│   └── ...
├── keyboards/           # Inline и Reply клавиатуры
│   └── inline.py
├── services/            # Бизнес-логика
│   ├── ai_service.py
│   ├── database.py
│   └── ...
└── requirements.txt     # Python зависимости
```

---

## 🚀 Установка и запуск

### 1. Установить зависимости

```bash
cd bot
pip install -r requirements.txt
```

### 2. Настроить переменные окружения

Создать файл `.env`:

```env
BOT_TOKEN=your_telegram_bot_token
OPENROUTER_API_KEY=your_openrouter_key
ADMIN_IDS=123456789,987654321
```

### 3. Запустить бота

```bash
python main.py
```

---

## 🔧 Конфигурация

### config.py

Основные настройки:
- `BOT_TOKEN` — токен Telegram бота
- `OPENROUTER_API_KEY` — ключ OpenRouter API
- `ADMIN_IDS` — список ID администраторов
- `DATABASE_PATH` — путь к SQLite базе

### config_models.py

Настройки AI-моделей:
- Список доступных моделей
- Параметры генерации (temperature, max_tokens)
- Стоимость токенов

---

## 📦 Деплой на сервер

### Системный сервис (systemd)

```bash
sudo nano /etc/systemd/system/vnxoracle-bot.service
```

```ini
[Unit]
Description=vnxORACLE Telegram Bot
After=network.target

[Service]
Type=simple
User=botuser
WorkingDirectory=/opt/bots/vnxORACLE_system/bot
ExecStart=/usr/bin/python3 main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Запуск:
```bash
sudo systemctl enable vnxoracle-bot
sudo systemctl start vnxoracle-bot
sudo systemctl status vnxoracle-bot
```

---

## 🧪 Разработка

### Структура обработчиков

```python
from aiogram import Router
from aiogram.types import Message

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Привет! Я vnxORACLE Bot")
```

### Добавление новой модели

1. Добавить в `config_models.py`
2. Обновить `services/ai_service.py`
3. Добавить кнопку в `keyboards/inline.py`

---

## 📊 Версия

**Текущая версия:** v2.1.5

---

## 🐛 Known Issues

- Voice recognition может быть медленным для длинных файлов
- Некоторые модели требуют дополнительных API keys

---

## 📄 Лицензия

Proprietary — vnxORACLE Team © 2024-2026
