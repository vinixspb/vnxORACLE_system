
# 👁 PROJECT STRUCTURE: vnxORACLE AI System (v2.1.5)

**Philosophy:** Adaptive Intelligence (The Mind) + Hybrid Reliability.

**Core Principle:** Multi-modal AI ecosystem with automatic failover and state-persistent navigation.

**Security:** Google Sheets Authorization + SQLite Session Persistence + TLS Impersonation.

---

## 📂 1. Файловая структура (The File Tree)

```plaintext
/opt/vnxORACLE_system/
├── services/               # 🧠 Изолированные сервисы (Бизнес-логика)
│   ├── ai_engine.py        # Текстовый интеллект (OpenRouter) + Vision + Whisper (STT)
│   ├── audio_studio.py     # Гибридная озвучка (ElevenLabs + OpenAI Fallback)
│   ├── video_studio.py     # Cinematic Unit: Генерация видео (Luma/Runway API) [BETA]
│   ├── database.py         # SQLite: WAL-режим, управление сессиями и токенами
│   └── sheets_mgr.py       # Синхронизация с "Матрицей" (Тарифы и кэшированный доступ)
│
├── docs/                   # 📚 Техническая документация
│   ├── SPECIFICATION.md    # Полное ТЗ системы
│   ├── PROJECT_STRUCTURE.md # Текущий документ
│   └── TODO.md             # План развития (Roadmap)
│
├── downloads/              # 📥 Временный буфер: Голосовые и фото до удаления
│
├── main.py                 # 🚀 Точка входа: Инициализация Dispatcher и Polling
├── loader.py               # 🔌 Синглтон-загрузчик: Инициализация всех сервисов и кэша
├── config.py               # ⚙️ Конфиг: API-ключи, ID кнопок, Системные промпты
├── handlers.py             # 🎮 Обработчики: Логика команд, Vision-обработка и состояния
├── keyboards.py            # ⌨️ Интерфейс: Все Reply и Inline конструкции
├── oracle.db               # 💾 База данных: SQLite (WAL Mode)
└── requirements.txt        # 📦 Зависимости (curl_cffi, python-telegram-bot, aiohttp)

```

---

## 🗺 2. Схема потоков данных (System Flow)

1. **Сигнал:** Пользователь отправляет данные (Текст/Фото/Голос).
2. **Шлюз (Handlers):** Проверяет тариф через `sheets_mgr` (используя TTL-кэш).
3. **Обработка:**
* **Фото:** Скачивается в `downloads/`, кодируется в Base64, уходит в `ai_engine` (Vision).
* **Голос:** Транскрибируется через Whisper, текст уходит в `ai_engine`.
* **Текст:** Извлекается контекст из `database.py` (последние  сообщений).


4. **Синтез:** Ответ ИИ сохраняется в БД, при необходимости озвучивается в `audio_studio`.
5. **Финализация:** Очистка временных файлов, обновление счетчика токенов пользователя.

---

## 🖥 3. Карта Меню (UI/UX Architecture)

### А. Главное меню (Reply Keyboard)

*Центральные команды управления.*

* `♻️ НОВЫЙ ЧАТ`: Сброс текущего контекста (создание новой сессии в БД).
* `💾 ИСТОРИЯ ЧАТОВ`: Список последних 10 диалогов с возможностью удаления.
* `👤 Мой профиль`: Вывод статуса тарифа и общего расхода токенов.
* `💳 Тарифные планы`: Вывод **текстового прайс-листа** и кнопок покупки.

### Б. Меню Возможностей (Inline Hub)

* **Выбор Нейросети:** Переключение между моделями (GPT-4o, Claude 3.5, Free-модели).
* **Аудио ИИ:** Доступ к TTS (ElevenLabs), SFX-генератору и транскрибации.
* **Дизайн с ИИ:** Быстрый доступ к генерации через Pollinations.
* **Видео ИИ (Beta):** Доступ к Luma/Runway (только для тарифа NEO).

---

## 🗄 4. Структура Базы Данных (SQLite)

| Таблица | Критические поля | Описание |
| --- | --- | --- |
| **sessions** | `id`, `user_id`, `is_active` | Хранит дерево диалогов. Только 1 сессия активна. |
| **messages** | `session_id`, `role`, `content` | История сообщений. Поддерживает мультимодальный контент. |
| **users** | `user_id`, `total_tokens` | Глобальный счетчик ресурсов пользователя. |

---

## 🧬 5. Технические Guardrails (Запреты и Правила)

1. **Atomic Vision:** Любое изображение должно быть удалено из `downloads/` сразу после формирования ответа от API.
2. **Hybrid Fallback:** При запросе аудио система обязана проверить `status_code`. Если ElevenLabs выдает 403, управление мгновенно передается OpenAI TTS.
3. **TTL Caching:** Доступ к Google Sheets API ограничен кэшем в `loader.py` на 10 минут, чтобы избежать лимитов Google и задержек в ответах.
4. **Accounting Formula:**
Расход считается по формуле:



---

## ⚠️ Критические зависимости (Requirements Check)

* **curl_cffi**: Обязателен для `audio_studio.py` (TLS Impersonation).
* **python-telegram-bot**: v20.7+ для корректной работы `post_init`.
* **sqlite3**: Обязательная поддержка `PRAGMA journal_mode=WAL;`.

---

*Документ является единственным источником правды об архитектуре vnxORACLE. Любое отклонение в коде без обновления этого файла считается нарушением Техно-Кодекса.*

---

**Что дальше?** Теперь, когда структура зафиксирована, а все документы (`SPECIFICATION`, `PROJECT_STRUCTURE`, `TODO`, `CURRENT_STAGE`) приведены к единому стандарту **v2.1.5**, мы готовы к запуску.

**Хочешь, я подготовлю для тебя финальный `main.py`, чтобы убедиться, что все новые хендлеры (Vision, Photo, Video) зарегистрированы правильно и готовы к работе?**
