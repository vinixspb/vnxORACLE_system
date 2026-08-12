# Landing Site Structure & Component Map

> **Полная схема сайта vnxORACLE с описанием всех блоков, кнопок и связей**

---

## 🏗 Общая архитектура

```
┌────────────────────────────────────────────────────────┐
│                    Landing Page                         │
├────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  1. HERO SECTION (Full-screen with video)       │  │
│  │     - Navbar (fixed top)                         │  │
│  │     - Background Video                           │  │
│  │     - Footer Content (bottom overlay)            │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  2. ROLES SECTION (White background)            │  │
│  │     - "Кого вы берете в команду?"                │  │
│  │     - 3 role cards (grid)                        │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  3. HOW IT WORKS (Dark background)              │  │
│  │     - "Сотрудник как Услуга"                     │  │
│  │     - 3 steps cards (grid)                       │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  4. TRUST SECTION (Light gray)                  │  │
│  │     - "Разум, которому можно доверить"           │  │
│  │     - 3 trust points (grid)                      │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
└────────────────────────────────────────────────────────┘
```

---

## 📦 Компоненты и их состав

### 1. **Hero Section** (Full-screen)

```
┌─────────────────────────────────────────────────┐
│ [Navbar - Fixed Top]                            │ ← z-index: 50
│ ┌──────────┐  ┌──────┐  ┌─────────────────┐    │
│ │ Logo+Brand│ │Menu □│  │Tags: Digital... │    │
│ └──────────┘  └──────┘  └─────────────────┘    │
│                   │                             │
│              [EN/RU] [•••] B2B Solutions        │
├─────────────────────────────────────────────────┤
│                                                 │
│         [Background Video - z-index: 0]         │ ← Autoplay loop
│            (80% mobile, 100% desktop)           │
│                                                 │
├─────────────────────────────────────────────────┤
│ [Footer Content - z-index: 30]                  │ ← Gradient fade
│ • Будущее корпоративного найма 2026             │
│                                                 │
│ Нанимайте Интеллект.                            │
│ Арендуйте Результат.                            │
│                                                 │
│ [Кого мы предлагаем?] [Как работает аренда]    │
│                                                 │
│ [LLM-Модели] [Глубокая Интеграция] [24/7]      │
└─────────────────────────────────────────────────┘
```

#### 1.1 Navbar Elements

| Element | Type | Function | Current State |
|---------|------|----------|--------------|
| **Logo** | Link `<a href="#top">` | Скролл к верху страницы | ✅ Работает |
| **LogoMark SVG** | Icon | Визуальный брендинг | ✅ Статичный |
| **Brand** ("vnxORACLE") | Text | Название компании | ✅ Показывается на desktop |
| **Menu Button** | `<button>` | Открывает меню (не реализовано) | ⚠️ Нет функционала |
| **Menu Icon** (Plus) | Icon | Визуальная индикация меню | ✅ Статичный |
| **Tags Pill** | Container | "Цифровой Штат", "Когнитивный ИИ" | ✅ Информативный |
| **Lang Switch (EN/RU)** | `<button onClick>` | Переключение языка | ✅ **Работает** |
| **Right Pill Button** (DotGrid) | `<button>` | Не реализовано | ⚠️ Нет функционала |
| **"B2B Solutions"** | Text | Категория продукта | ✅ Информативный |

#### 1.2 Footer Content (Hero Bottom)

| Element | Type | Function | Current State |
|---------|------|----------|--------------|
| **Subtitle** ("• Будущее...") | Text + Dot | Контекстный слоган | ✅ Информативный |
| **Heading** (2 lines) | `<h1>` | Главный месседж | ✅ Адаптивный размер |
| **"Кого мы предлагаем?"** | `<button className="btn-primary">` | Скролл к Roles Section | ⚠️ Нет функционала |
| **"Как работает аренда"** | `<button className="btn-ghost">` | Скролл к How Section | ⚠️ Нет функционала |
| **Tag Pills** (x3) | Badges | Ключевые фичи | ✅ Информативные |

---

### 2. **Roles Section** (White)

```
┌─────────────────────────────────────────────────┐
│  Кого вы берете в команду?                      │
│  Мы не продаем чат-ботов. Мы сдаем...           │
├─────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐│
│ │ L1/L2       │ │ Менеджер    │ │ HR Ассистент││
│ │ Техподдержка│ │ по Продажам │ │ / Офис      ││
│ │             │ │             │ │             ││
│ │ Закрывает...│ │ Квалифициру-│ │ Помогает... ││
│ └─────────────┘ └─────────────┘ └─────────────┘│
└─────────────────────────────────────────────────┘
```

| Element | Type | Function | Current State |
|---------|------|----------|--------------|
| **Section Heading** | `<h2>` | Заголовок секции | ✅ Адаптивный |
| **Description** | `<p>` | Описание подхода | ✅ Информативный |
| **Role Cards (x3)** | `<div className="role-card">` | Презентация ролей | ✅ Hover эффект |
| - Role Title | `<h3>` | Название роли | ✅ Текст |
| - Role Desc | `<p>` | Описание функций | ✅ Текст |

**Интерактивность:**
- `:hover` → `translateY(-4px)` + shadow
- Нет кликабельных элементов

---

### 3. **How It Works Section** (Dark #0A0D12)

```
┌─────────────────────────────────────────────────┐
│  Сотрудник как Услуга (EaaS)                    │ ← White text
├─────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐│
│ │ 01          │ │ 02          │ │ 03          ││
│ │ Собеседова- │ │ Стажировка  │ │ Выход на    ││
│ │ ние         │ │             │ │ работу      ││
│ │             │ │             │ │             ││
│ │ Вы рассказы-│ │ Разворачи-  │ │ Начинает... ││
│ │ ваете...    │ │ ваем...     │ │             ││
│ └─────────────┘ └─────────────┘ └─────────────┘│
└─────────────────────────────────────────────────┘
```

| Element | Type | Function | Current State |
|---------|------|----------|--------------|
| **Section Heading** | `<h2>` (white) | Заголовок секции | ✅ Адаптивный |
| **Step Cards (x3)** | `<div className="step-card">` | Этапы процесса | ✅ Статичные |
| - Step Number | `<div className="step-number">` | 01, 02, 03 | ✅ Текст |
| - Step Title | `<h3>` (white) | Название этапа | ✅ Текст |
| - Step Desc | `<p>` (white 0.7 opacity) | Описание | ✅ Текст |

**Интерактивность:**
- Нет hover эффектов
- Нет кликабельных элементов

---

### 4. **Trust Section** (Light #FFFFFF)

```
┌─────────────────────────────────────────────────┐
│  Разум, которому можно доверить бизнес.         │
├─────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐│
│ │▌Изолирован- │ │▌Управляемая │ │▌Непрерывная ││
│ │ ная память  │ │ логика      │ │ эволюция    ││
│ │             │ │             │ │             ││
│ │ Данные...   │ │ Не галлюци- │ │ Апдейты...  ││
│ └─────────────┘ └─────────────┘ └─────────────┘│
└─────────────────────────────────────────────────┘
    ▲ Black left border (3px)
```

| Element | Type | Function | Current State |
|---------|------|----------|--------------|
| **Section Heading** | `<h2>` | Заголовок секции | ✅ Адаптивный |
| **Trust Cards (x3)** | `<div className="trust-card">` | Преимущества | ✅ Статичные |
| - Trust Title | `<h3>` | Название преимущества | ✅ Текст |
| - Trust Desc | `<p>` | Описание | ✅ Текст |
| - Left Border | CSS | Визуальный акцент | ✅ Декоративный |

**Интерактивность:**
- Нет hover эффектов
- Нет кликабельных элементов

---

## 🔘 Все кнопки и их статус

| # | Button | Location | Type | Function | Status |
|---|--------|----------|------|----------|--------|
| 1 | **Menu** (Plus icon) | Navbar left | `<button>` | Открыть меню | ⚠️ **Не реализовано** |
| 2 | **EN/RU** | Navbar right | `<button onClick>` | Переключение языка | ✅ **Работает** |
| 3 | **DotGrid (•••)** | Navbar right pill | `<button>` | Неизвестно | ⚠️ **Не реализовано** |
| 4 | **"Кого мы предлагаем?"** | Hero footer | `<button className="btn-primary">` | Скролл к Roles | ⚠️ **Не реализовано** |
| 5 | **"Как работает аренда"** | Hero footer | `<button className="btn-ghost">` | Скролл к How | ⚠️ **Не реализовано** |

---

## 🎨 Темы (Light/Dark) — Текущее состояние

**❌ Переключатель темы НЕ РЕАЛИЗОВАН**

### Что нужно добавить:

1. **Theme Toggle Button** в Navbar
2. **CSS Variables** для цветов
3. **State Management** (`useState` для темы)
4. **LocalStorage** для сохранения выбора
5. **Dark Mode Styles** для всех секций

---

## 📱 Адаптивность

| Breakpoint | Layout Changes |
|------------|----------------|
| **< 768px** (Mobile) | - Video 80%×80%<br>- Brand скрыт<br>- Tags pill скрыта<br>- Right pill label скрыт<br>- Grids 1 column<br>- Footer column layout |
| **≥ 768px** (Desktop) | - Video 100%×100%<br>- Brand виден<br>- Tags pill видна<br>- Right pill label виден<br>- Grids 3 columns<br>- Footer row layout |

---

## 🌐 Мультиязычность

**✅ Реализовано**

- **Состояние:** `const [lang, setLang] = useState('ru')`
- **Переключение:** Кнопка EN/RU в Navbar
- **Переводы:** Объект `translations` с ключами `en` и `ru`
- **Охват:** Все тексты на странице переводятся

---

## 🔗 Навигация и связи

### Текущие связи:

```
[Logo] (#top) ──────────┐
                        ├──> Скролл к началу страницы
                        │
[Lang Switch] ─────────┼──> Переключение en ↔ ru
                        │
[ ] Menu Button         │    НЕТ связи
[ ] DotGrid Button      │    НЕТ связи
[ ] "Кого предлагаем"   │    НЕТ связи (должно → #roles)
[ ] "Как работает"      │    НЕТ связи (должно → #how)
```

### Что нужно добавить:

```javascript
// Smooth scroll to sections
const scrollToSection = (id) => {
  document.getElementById(id)?.scrollIntoView({ 
    behavior: 'smooth' 
  })
}

// Add IDs to sections:
<section id="roles" className="section roles-section">
<section id="how" className="section how-section">
<section id="trust" className="section trust-section">
```

---

## 📋 TODO: Недостающий функционал

### Высокий приоритет:

- [ ] **Dark/Light Theme Toggle**
  - [ ] Добавить кнопку переключения
  - [ ] CSS Variables для цветов
  - [ ] LocalStorage persistence
  - [ ] Smooth transition

- [ ] **Smooth Scroll Navigation**
  - [ ] "Кого мы предлагаем?" → #roles
  - [ ] "Как работает аренда" → #how
  - [ ] Добавить section IDs

- [ ] **Menu Functionality**
  - [ ] Мобильное меню (drawer/overlay)
  - [ ] Навигация по секциям
  - [ ] Закрытие по клику вне

### Средний приоритет:

- [ ] **DotGrid Button Action**
  - [ ] Определить назначение
  - [ ] Реализовать функционал

- [ ] **CTA Form/Modal**
  - [ ] "Связаться с нами"
  - [ ] Lead capture form

- [ ] **Footer Section**
  - [ ] Copyright, links
  - [ ] Social media icons

### Низкий приоритет:

- [ ] **Анимации при скролле**
  - [ ] Intersection Observer
  - [ ] Fade-in эффекты

- [ ] **Аналитика**
  - [ ] Google Analytics
  - [ ] Button click tracking

---

## 🛠 Технический стек компонентов

| Component | Dependencies | State | Props |
|-----------|-------------|-------|-------|
| `App` | - | `lang` (useState) | - |
| `Navbar` | Lucide (Plus), motion | - | `lang`, `setLang` |
| `BackgroundVideo` | motion | - | - |
| `FooterContent` | motion | - | `lang` |
| `RolesSection` | - | - | `lang` |
| `HowItWorksSection` | - | - | `lang` |
| `TrustSection` | - | - | `lang` |

---

## 📄 Файловая структура

```
landing/
├── src/
│   ├── App.jsx          # Main component (336 lines)
│   ├── App.css          # All styles (517 lines)
│   ├── main.jsx         # Entry point
│   └── index.css        # Global resets
├── index.html           # HTML template
├── vite.config.js       # Vite config (base path)
├── package.json         # Dependencies
└── README.md            # Documentation
```

---

## 🎯 Roadmap для полной функциональности

### Phase 1: Core Interactivity (Сейчас)
1. Theme Toggle (Dark/Light)
2. Smooth Scroll Navigation
3. Menu Drawer (Mobile)

### Phase 2: Content Expansion
4. Pricing Section
5. FAQ Section
6. Contact Form / CTA

### Phase 3: Advanced Features
7. Case Studies / Portfolio
8. Blog Integration
9. Analytics & Tracking

---

## 📞 Контакты для разработки

**Repository:** https://github.com/vinixspb/vnxORACLE_system  
**Live Site:** https://vinixspb.github.io/vnxORACLE_system/  
**Documentation:** `/docs` folder
