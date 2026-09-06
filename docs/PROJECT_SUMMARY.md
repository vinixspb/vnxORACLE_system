# vnxORACLE System — Project Summary

**Дата:** 2026-08-12  
**Статус:** Активная разработка Phase 1

---

## 🎯 Ключевые решения

### 1. Позиционирование
- **Концепция:** Employee as a Service (EaaS) — цифровые AI-сотрудники в аренду
- **Слоган (КАНОН):** "Нанимайте Интеллект. Арендуйте Результат."
- **Фокус:** Текстовые каналы (чат, email, мессенджеры), не голосовые звонки
- **Референс:** NEWO.AI (подход и структура), но адаптация под текстовую риторику

### 2. Дизайн-философия
- **Стиль:** Apple минимализм + iOS 26 glass-morphism
- **Палитра:** Dark surfaces (#05070C → #1E2636) + cyan accent (#38BDF8)
- **Принцип:** Простота, ясность, функциональность
- **Канонические тексты:** Зафиксированы в `docs/BRAND_IDENTITY.md`, изменения только с согласования

### 3. Технологический стек

**Frontend (текущий):**
- Landing: React 19 + Vite + Framer Motion
- Дизайн: CSS Grid-first, токенизированные стили

**Backend (новый):**
- API: FastAPI (Python 3.11+)
- AI: OpenRouter (мультимодельный роутинг)
- CRM: Google Sheets (MVP) → PostgreSQL (production)
- Cache: In-memory (MVP) → Redis (production)

**Интеграции:**
- Telegram Bot API (есть 2 production бота)
- Google Sheets API
- amoCRM/Bitrix24 (для RU клиентов, roadmap)

### 4. Production кейсы (Social Proof)

**Lavka Games Support Bot**
- Telegram: [@lavkaigr_support_aibot](https://t.me/lavkaigr_support_aibot)
- 80% тикетов закрыты автоматически
- Освобождено 1.5 FTE

**vnxMATRIX VPN Support Bot**
- Telegram: [@vnxMATRIXsupport_bot](https://t.me/vnxMATRIXsupport_bot)
- 92% вопросов без эскалации
- Поддержка на 5 языках

---

## 📁 Структура проекта

```
vnxORACLE_system/
├── landing/                    # React-сайт (текущий)
│   ├── src/
│   │   ├── App.jsx            # Hero + секции
│   │   ├── App.css
│   │   └── components/        # (будущий ChatWidget)
│   └── package.json
│
├── bot/                        # Telegram Bot (production)
│   ├── main.py
│   ├── config.py
│   ├── handlers/
│   ├── services/
│   │   └── ai_engine.py       # Multi-LLM failover
│   └── keyboards/
│
├── api/                        # FastAPI backend (новый)
│   ├── main.py                # Endpoints
│   ├── config.py              # Настройки
│   ├── requirements.txt
│   ├── .env.example
│   ├── agents/
│   │   ├── base_agent.py
│   │   └── sales_agent.py     # Sales consultant
│   ├── services/
│   │   ├── ai_service.py      # OpenRouter
│   │   ├── sheets_service.py  # Google Sheets CRM
│   │   └── conversation.py    # Управление диалогами
│   └── prompts/
│       └── sales_consultant.txt
│
└── docs/
    ├── BRAND_IDENTITY.md       # Канонические тексты и принципы
    ├── ROADMAP.md              # План развития (6 фаз)
    └── ARCHITECTURE.md         # Техническая архитектура
```

---

## 🚀 Phase 1: MVP Chat Widget (текущая фаза)

### Цель
Добавить умного AI-консультанта на сайт для захвата лидов.

### Реализовано (Backend)
- ✅ FastAPI приложение (`api/main.py`)
- ✅ OpenRouter интеграция с multi-LLM failover
- ✅ Google Sheets CRM сервис
- ✅ Conversation manager (история диалогов)
- ✅ Sales Agent с промптом
- ✅ Endpoints: `/api/chat`, `/api/lead/capture`, `/api/health`

### Следующие шаги (Frontend)
1. **Chat Widget компонент** (React)
   - Floating button (правый нижний угол)
   - Glass-morphism окно чата
   - WebSocket/HTTP polling для real-time
   - Интеграция в `App.jsx`

2. **Deploy Backend**
   - Deploy API на MATRIXde-n1
   - Настроить `.env` с ключами
   - Systemd service для автозапуска

3. **Тестирование**
   - Первые диалоги с реальными посетителями
   - A/B тестирование промпта
   - Настройка Google Sheets

---

## 📋 Roadmap (6 фаз)

### Phase 1: MVP Chat Widget (Weeks 1-2) ← СЕЙЧАС ЗДЕСЬ
- Backend: ✅ Готов
- Frontend: 🔄 В процессе
- Deploy: ⏳ Ожидает

### Phase 2: Production Cases (Weeks 3-4)
- Секция "Real Businesses" на сайте
- Кейсы: Lavka Games, vnxMATRIX
- Ссылки на production ботов

### Phase 3: Templates Marketplace (Weeks 5-8)
- 3 готовых шаблона (Support/Sales/HR)
- Omnichannel архитектура
- Zero Hallucination layer

### Phase 4: Integration Layer (Weeks 9-12)
- amoCRM + Bitrix24
- PostgreSQL + Redis
- API для custom интеграций

### Phase 5: Client Dashboard (Weeks 13-16)
- Bot creator без кода
- Knowledge base manager
- Real-time analytics

### Phase 6: Visual Upgrade (Weeks 17-18)
- Замена руки на аватар девушки
- 3D render или animated loop
- iOS 26 inspired design

---

## 🎨 Планируемые визуальные улучшения

### Приоритет 1: Chat Widget
- Floating кнопка с пульсацией
- Glass-morphism дизайн
- Плавные анимации (Framer Motion)
- Dark/Light theme sync

### Приоритет 2: Background Avatar
- Концепт: Симпатичная девушка (futuristic/cyberpunk)
- Стиль: Минималистичный, в палитре сайта
- Варианты: Static render → Animated loop → Real-time 3D

---

## 🔑 Ключевые файлы

### Документация (канонические)
- **`docs/BRAND_IDENTITY.md`** — брендовые тексты, дизайн-принципы, кейсы
- **`docs/ROADMAP.md`** — детальный план развития
- **`api/prompts/sales_consultant.txt`** — промпт для sales-агента

### Backend
- **`api/main.py`** — FastAPI endpoints
- **`api/services/ai_service.py`** — OpenRouter интеграция
- **`api/services/sheets_service.py`** — Google Sheets CRM

### Frontend (текущий)
- **`landing/src/App.jsx`** — основной компонент сайта
- **`landing/src/App.css`** — стили

---

## 💡 Важные договоренности

1. **Канонические тексты** зафиксированы в `BRAND_IDENTITY.md`
   - Изменения только с согласования
   - Возможность отката через git

2. **Дизайн-принципы**
   - Apple минимализм (не усложняем)
   - iOS 26 glass-morphism (для виджетов)
   - Никаких ярких градиентов

3. **Интеграции**
   - Google Sheets — основная CRM на старте
   - PostgreSQL — для production
   - amoCRM/Bitrix24 — только для RU клиентов или по запросу

4. **Географический фокус**
   - Россия — приоритет
   - International — по запросу

5. **Production кейсы**
   - Lavka Games и vnxMATRIX — можно использовать на сайте
   - Прямые ссылки на Telegram ботов

---

## 🎯 Immediate Next Steps (на завтра)

### Backend
1. ✅ Создать `.env` с реальными ключами
2. ✅ Тестовый запуск API локально
3. ✅ Проверить интеграцию с OpenRouter
4. ✅ Настроить Google Sheets

### Frontend
1. Создать `ChatWidget` компонент
2. Floating button + chat window
3. Интеграция с API (`/api/chat`)
4. Тестирование в браузере

### Deploy
1. Push на GitHub
2. Deploy API на MATRIXde-n1
3. Systemd service setup
4. Проверка на production

---

## 📞 Контакты и ресурсы

- **GitHub:** [github.com/vinixspb/vnxORACLE_system](https://github.com/vinixspb/vnxORACLE_system)
- **Сайт:** [vinixspb.github.io/vnxORACLE_system](https://vinixspb.github.io/vnxORACLE_system/)
- **Production боты:**
  - Lavka Games: [@lavkaigr_support_aibot](https://t.me/lavkaigr_support_aibot)
  - vnxMATRIX VPN: [@vnxMATRIXsupport_bot](https://t.me/vnxMATRIXsupport_bot)
- **Сервер:** MATRIXde-n1

---

**Последнее обновление:** 2026-08-12  
**Текущая фаза:** Phase 1 — MVP Chat Widget (Backend готов, Frontend в процессе)  
**Следующий шаг:** Создание Chat Widget компонента для Landing
