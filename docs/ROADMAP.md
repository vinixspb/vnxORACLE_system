# vnxORACLE Development Roadmap

> **Пошаговый план развития экосистемы AI Workforce**

---

## 🎯 Общая стратегия

### Миссия:
Создать платформу для аренды специализированных AI-сотрудников, которые работают через текстовые каналы (чат, email, мессенджеры).

### Ключевые отличия от конкурентов:
- **Фокус:** Письменная риторика (не голосовые звонки)
- **Подход:** Apple-стиль минимализм + iOS 26 glass-morphism
- **Философия:** "Нанимайте Интеллект. Арендуйте Результат."

---

## 📅 PHASE 1: MVP — Chat Widget (Weeks 1-2)

### Цель:
Добавить на сайт умного AI-консультанта для захвата и квалификации лидов.

### Задачи:

#### Week 1: Backend API

**1.1. Создать FastAPI приложение**
```
api/
├── main.py                    # Точка входа
├── config.py                  # Настройки (env vars)
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

**1.2. OpenRouter Integration**
- Переиспользовать логику из `bot/services/ai_engine.py`
- Multi-LLM failover механизм
- Survival loop (5 попыток при сбоях)

**1.3. Google Sheets CRM**
- API интеграция
- Структура таблицы:
  - Timestamp | Name | Contact | Company | Problem | Messages | Status | Next Step
- Webhook уведомления в Telegram админу

**1.4. Endpoints**
```
POST /api/chat             # Отправка сообщения
POST /api/lead/capture     # Сохранение контакта
GET  /api/health           # Healthcheck
WS   /api/ws/chat/{sid}    # WebSocket для real-time
```

#### Week 2: Frontend Chat Widget

**2.1. React компоненты**
```
landing/src/components/ChatWidget/
├── index.jsx              # Main component
├── ChatButton.jsx         # Floating button
├── ChatWindow.jsx         # Chat container
├── MessageList.jsx        # История сообщений
├── MessageBubble.jsx      # Один message
├── ChatInput.jsx          # Поле ввода
└── styles.css             # Стили (glass-morphism)
```

**2.2. Дизайн (iOS 26 inspired)**
- **Floating button:**
  - Позиция: fixed, right: 24px, bottom: 24px
  - Размер: 60x60px, border-radius: 999px
  - Цвет: #38BDF8 (accent)
  - Анимация: пульсация при наведении
  
- **Chat window:**
  - Размер: 400x600px на desktop, fullscreen на mobile
  - Glass-morphism: `backdrop-filter: blur(20px)`
  - Background: `rgba(15, 19, 28, 0.85)` в dark mode
  - Border: 1px solid rgba(255,255,255,0.1)
  - Shadow: custom токенизированная тень

**2.3. Функционал**
- Открытие/закрытие с анимацией (Framer Motion)
- WebSocket connection для real-time
- Автосохранение в localStorage
- Typing indicator
- Захват email/telegram после 2-3 сообщений

**2.4. Интеграция в Landing**
```jsx
// landing/src/App.jsx
import ChatWidget from './components/ChatWidget'

export default function App() {
  // ... existing code
  
  return (
    <div data-theme={theme}>
      {/* ... existing sections */}
      <ChatWidget />  {/* Добавляем виджет */}
    </div>
  )
}
```

#### Deliverables Phase 1:
- ✅ Работающий chat widget на сайте
- ✅ Backend API на FastAPI
- ✅ Google Sheets CRM с автозаписью лидов
- ✅ Telegram уведомления админу о новых лидах
- ✅ Deploy на MATRIXde-n1

---

## 📅 PHASE 2: Production Cases (Weeks 3-4)

### Цель:
Добавить на сайт секцию с реальными кейсами внедрения.

### Задачи:

**3.1. Секция "Real Businesses" на Landing**
```jsx
// landing/src/components/CasesSection.jsx

Структура:
┌─────────────────────────────────────────┐
│ Real Businesses, Real Results           │
├─────────────────────────────────────────┤
│                                         │
│ [Case Card 1: Lavka Games]              │
│ [Case Card 2: vnxMATRIX VPN]            │
│ [Case Card 3: (Placeholder)]            │
│                                         │
└─────────────────────────────────────────┘
```

**3.2. Case Card Design**
```
┌──────────────────────────────────────┐
│ 🎲 Lavka Games Support Bot           │
│ "80% tickets closed automatically"   │
│                                      │
│ • 24/7 consultation                  │
│ • Order tracking                     │
│ • Game recommendations               │
│                                      │
│ [Try Bot →] [@lavkaigr_support_ai...]│
└──────────────────────────────────────┘
```

**3.3. Контент для кейсов**

**Lavka Games:**
```
Компания: Lavka Games & Tabletop KZ
Индустрия: Настольные игры (Retail + E-commerce)
Проблема: 200+ вопросов/день о правилах игр и статусах заказов
Решение: AI Support Specialist в Telegram
Результаты:
  - 80% тикетов закрываются автоматически
  - Среднее время ответа: 8 секунд
  - Освобождено 1.5 FTE (экономия ~150,000₽/год)
  - NPS клиентов: +15 пунктов
Telegram: @lavkaigr_support_aibot
```

**vnxMATRIX VPN:**
```
Компания: vnxMATRIX VPN Service
Индустрия: VPN / Privacy Tech
Проблема: Техподдержка 24/7 для международных клиентов
Решение: AI Support Bot (мультиязычный)
Результаты:
  - 92% вопросов решены без эскалации
  - Поддержка на 5 языках
  - Время ответа < 10 секунд
  - Экономия на найме support-команды
Telegram: @vnxMATRIXsupport_bot
```

**3.4. "Try These Bots" CTA**
- Прямые ссылки на Telegram ботов
- Embedded Telegram Widget (если возможно)
- QR-коды для мобильных пользователей

#### Deliverables Phase 2:
- ✅ Секция Cases на сайте
- ✅ 2 детальных кейса с метриками
- ✅ Прямые ссылки на production ботов
- ✅ Social proof для B2B клиентов

---

## 📅 PHASE 3: Templates Marketplace (Weeks 5-8)

### Цель:
Создать 3 готовых шаблона AI-сотрудников для продажи.

### Задачи:

**4.1. Архитектура шаблона**
```
bot_templates/
├── support_bot/
│   ├── README.md              # Документация
│   ├── config.yaml            # Настройки клиента
│   ├── prompts/
│   │   └── system_prompt.txt
│   ├── knowledge_base/
│   │   └── faq_template.json
│   ├── handlers/
│   │   ├── telegram.py
│   │   ├── web_chat.py
│   │   └── whatsapp.py
│   └── deploy/
│       ├── docker-compose.yml
│       └── .env.example
```

**4.2. Template 1: Support Bot**
- База знаний (FAQ) через JSON/CSV
- Умная эскалация к оператору
- Интеграция с тикет-системой
- Аналитика: время ответа, CSAT

**4.3. Template 2: Sales Bot**
- Квалификация лидов (BANT framework)
- Каталог товаров/услуг
- Обработка возражений
- Запись на демо/созвоны

**4.4. Template 3: HR Assistant**
- База документов компании
- Onboarding новых сотрудников
- FAQ по HR-политикам
- Интеграция с корп. порталом

**4.5. Omnichannel Architecture**
```python
# Один код работает во всех каналах
class BaseAgent:
    async def handle_message(self, message, channel):
        # Единая логика для Telegram/Web/WhatsApp
        response = await self.generate_response(message)
        return await self.send(response, channel)
```

**4.6. Zero Hallucination Layer**
```python
async def generate_response(query, knowledge_base):
    # 1. RAG: поиск фактов
    facts = await retrieve_facts(query, knowledge_base)
    
    # 2. LLM генерирует ответ
    response = await llm.generate(query, context=facts)
    
    # 3. Fact-checker проверяет
    if not await verify_response(response, facts):
        return escalate_to_human()
    
    return response
```

#### Deliverables Phase 3:
- ✅ 3 готовых шаблона ботов
- ✅ Документация по развертыванию
- ✅ Docker-compose для быстрого старта
- ✅ Demo для каждого шаблона

---

## 📅 PHASE 4: Integration Layer (Weeks 9-12)

### Цель:
Реализовать интеграции с популярными CRM и платформами.

### Задачи:

**5.1. Priority 1: Russian Market**

**amoCRM Integration:**
- Webhook для новых лидов
- Автосоздание сделок
- Синхронизация статусов
- Custom fields mapping

**Bitrix24 Integration:**
- REST API интеграция
- Лиды → CRM
- Задачи → Битрикс
- Отчёты по конверсии

**5.2. Priority 2: Database Layer**

**PostgreSQL Migration:**
```sql
-- Таблицы
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255),
    channel VARCHAR(50),
    messages JSONB,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE knowledge_base (
    id SERIAL PRIMARY KEY,
    company_id INT,
    content TEXT,
    embedding VECTOR(1536),  -- для RAG
    metadata JSONB
);
```

**Redis для кеширования:**
- Сессии чатов (TTL 24h)
- Rate limiting
- Temporary context

**5.3. Priority 3: International**
- HubSpot (по запросу)
- Salesforce (Enterprise клиенты)
- Stripe для биллинга

#### Deliverables Phase 4:
- ✅ amoCRM + Bitrix24 интеграции
- ✅ PostgreSQL + Redis
- ✅ API для custom интеграций
- ✅ Документация по интеграциям

---

## 📅 PHASE 5: Client Dashboard (Weeks 13-16)

### Цель:
Веб-панель для клиентов — управление ботами без кода.

### Задачи:

**6.1. Dashboard Architecture**
```
dashboard/
├── pages/
│   ├── Login.jsx              # Авторизация
│   ├── Overview.jsx           # Главная страница
│   ├── BotCreator.jsx         # Конструктор бота
│   ├── KnowledgeBase.jsx      # Управление знаниями
│   ├── Analytics.jsx          # Статистика
│   ├── Integrations.jsx       # Настройка интеграций
│   └── Billing.jsx            # Подписка и оплата
```

**6.2. Ключевые функции**

**Bot Creator:**
- Выбор типа (Support/Sales/HR)
- Upload базы знаний (PDF/CSV/URLs)
- Настройка Tone of Voice через примеры
- Тестовый чат для проверки

**Knowledge Base Manager:**
- Drag & drop загрузка документов
- Парсинг сайтов (URL crawler)
- Версионирование базы знаний
- Поиск по базе

**Analytics Dashboard:**
- Количество диалогов
- Конверсия (lead → qualified lead)
- Sentiment анализ
- Топ вопросов клиентов
- Время ответа / CSAT

**Integrations:**
- One-click подключение Telegram/WhatsApp
- OAuth для amoCRM/Bitrix24
- Webhook endpoints
- API keys management

**6.3. Tech Stack**
- **Frontend:** Next.js 15 + shadcn/ui
- **Backend:** FastAPI (existing)
- **Auth:** JWT + refresh tokens
- **Styling:** Tailwind CSS (в стиле текущего сайта)

#### Deliverables Phase 5:
- ✅ Client dashboard (MVP)
- ✅ Bot creator без кода
- ✅ Knowledge base manager
- ✅ Real-time analytics

---

## 📅 PHASE 6: Visual Upgrade (Weeks 17-18)

### Цель:
Улучшить визуальную часть сайта — заменить руку на аватар.

### Задачи:

**7.1. Концепт аватара**
- **Персонаж:** Симпатичная девушка, futuristic/cyberpunk
- **Стиль:** Минималистичный, в палитре сайта
- **Настроение:** Профессиональная, но дружелюбная

**7.2. Варианты реализации**

**Вариант A: Static Render (быстро)**
- Генерация через Midjourney/Stable Diffusion
- High-quality PNG/WebP
- Subtle parallax effect при scroll
- Время: 2-3 дня

**Вариант B: Animated Loop (средне)**
- Blender → 3-5 секунд loop
- Export как MP4/WebM
- Плавная интеграция вместо текущего видео
- Время: 1-1.5 недели

**Вариант C: Real-time 3D (сложно)**
- React Three Fiber + Drei
- Интерактивная: реагирует на cursor/scroll
- Морфинг эмоций
- Время: 2-3 недели

**Рекомендация:** Начать с Варианта A, потом upgrade до B.

**7.3. Технический подход**
```jsx
// landing/src/components/BackgroundAvatar.jsx
import { motion } from 'motion/react'

export default function BackgroundAvatar() {
  return (
    <motion.div 
      className="avatar-layer"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 1.2 }}
    >
      <img 
        src="/assets/avatar-cyberpunk.webp" 
        alt=""
        className="avatar-image"
      />
    </motion.div>
  )
}
```

#### Deliverables Phase 6:
- ✅ Новый аватар (static render)
- ✅ Плавная интеграция в сайт
- ✅ Адаптация под dark/light themes
- ✅ Responsive для mobile

---

## 🎯 Success Metrics

### Phase 1-2 (MVP):
- [ ] Chat widget установлен и работает
- [ ] 10+ захваченных лидов в первую неделю
- [ ] Конверсия посетитель → лид: >5%
- [ ] Средняя длина диалога: 5+ сообщений

### Phase 3-4 (Templates):
- [ ] 3 готовых шаблона в production
- [ ] Первая продажа шаблона
- [ ] 2+ интеграции (amoCRM/Bitrix24)
- [ ] Документация покрывает 100% функционала

### Phase 5-6 (Dashboard + Visual):
- [ ] 10+ активных клиентов используют dashboard
- [ ] Self-service: 80% клиентов настраивают ботов сами
- [ ] Новый аватар получает положительный feedback
- [ ] Bounce rate сайта снижается на 20%

---

## 🚀 Quick Start (Week 1)

### Приоритет на завтра:

1. **Создать FastAPI backend** (День 1-2)
   ```bash
   cd api/
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install fastapi uvicorn openai google-api-python-client
   ```

2. **Sales Agent Prompt** (День 1)
   - Написать system prompt для sales-консультанта
   - Тестировать в ChatGPT/Claude

3. **Google Sheets Setup** (День 2)
   - Создать таблицу CRM
   - Настроить Service Account
   - Тестовая запись через API

4. **Chat Widget UI** (День 3-4)
   - Floating button
   - Chat window (glass-morphism)
   - Basic WebSocket connection

5. **Deploy & Test** (День 5)
   - Deploy API на MATRIXde-n1
   - Интеграция виджета в Landing
   - Первые тестовые диалоги

---

## 📝 Notes

- **Минимализм превыше всего** — каждая фича должна быть обоснована
- **Канонические тексты** — в BRAND_IDENTITY.md, изменения только после согласования
- **Итеративный подход** — запускаем быстро, улучшаем постепенно
- **Production first** — используем реальные кейсы (Lavka Games, vnxMATRIX) для Social Proof

---

**Roadmap обновлён:** 2026-08-12  
**Версия:** 1.0  
**Статус:** Active Development
