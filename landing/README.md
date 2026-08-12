# vnxORACLE Landing Page

> **Modern Full-Screen Hero Landing with Video Background**

Современная посадочная страница с полноэкранным видео-фоном и плавными анимациями на базе React 19 и Framer Motion.

---

## ✨ Особенности

- 🎬 **Full-screen video background** — автоматический autoplay
- ✨ **Плавные анимации** — Framer Motion (motion package)
- 📱 **Адаптивный дизайн** — mobile-first подход
- 🎨 **Минималистичный дизайн** — черно-белая палитра
- ⚡ **Высокая производительность** — Vite + React 19
- 🔤 **Кастомная типографика** — Inter font family

---

## 🏗 Стек технологий

- **React 19** — UI framework
- **Vite** — сборщик и dev-server
- **Framer Motion** (`motion`) — анимации
- **Lucide React** — иконки
- **CSS Grid & Flexbox** — layout
- **Google Fonts** — Inter (300, 400, 500, 600)

---

## 🚀 Быстрый старт

### 1. Установить зависимости

```bash
cd landing
npm install
```

### 2. Запустить dev-server

```bash
npm run dev
```

Откройте [http://localhost:5173](http://localhost:5173)

### 3. Production build

```bash
npm run build
npm run preview  # предпросмотр production сборки
```

---

## 📁 Структура проекта

```
landing/
├── src/
│   ├── App.jsx          # Главный компонент
│   ├── App.css          # Стили
│   └── main.jsx         # Точка входа
├── index.html           # HTML шаблон
├── vite.config.js       # Конфигурация Vite
├── package.json         # Зависимости
└── .gitignore
```

---

## 🎨 Дизайн-система

### Цветовая палитра

- **Background:** `#FFFFFF` (белый)
- **Primary Text:** `#000000` (черный)
- **Secondary Text:** `rgba(0, 0, 0, 0.55)` (55% opacity)
- **Accent (Pills):** `#F4F4F6` (светло-серый)
- **Borders:** `rgba(0, 0, 0, 0.12)` (12% opacity)

### Типографика

```css
font-family: 'Inter', system-ui, -apple-system, sans-serif;
font-weights: 300 (light), 400 (regular), 500 (medium), 600 (semibold)
```

### Responsive Breakpoints

- **Mobile:** < 768px
- **Desktop:** ≥ 768px

---

## 🎬 Видео-фон

**URL:** CloudFront CDN  
**Формат:** MP4, autoplay, muted, playsInline  
**Размер:**
- Mobile: 80% × 80% (centered)
- Desktop: 100% × 100% (cover)

---

## ✨ Анимации (Framer Motion)

Все анимации используют easing: `[0.16, 1, 0.3, 1]`

| Элемент | Эффект | Delay | Duration |
|---------|--------|-------|----------|
| Navbar | slide down + fade | 0s | 0.8s |
| Video | fade + scale | 0s | 1.8s |
| Footer wrapper | slide up | 0.5s | 1.0s |
| Subtitle | slide up | 0.6s | 0.8s |
| Heading | slide up | 0.8s | 0.8s |
| Buttons | slide up | 1.0s | 0.8s |

---

## 📦 Деплой

### GitHub Pages

```bash
npm run build
# Загрузить dist/ на GitHub Pages
```

### Vercel

```bash
vercel deploy
```

### Netlify

```bash
netlify deploy --prod
```

---

## 🔧 Конфигурация

### vite.config.js

```js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
})
```

### package.json scripts

- `npm run dev` — запуск dev-server
- `npm run build` — production сборка
- `npm run preview` — предпросмотр production

---

## 🎯 Roadmap

- [ ] Добавить больше секций (Features, Pricing, FAQ)
- [ ] Интеграция с Telegram Bot API
- [ ] Multi-language support (EN, RU)
- [ ] SEO оптимизация (meta tags, sitemap)
- [ ] Analytics (Google Analytics / Yandex Metrika)

---

## 📄 Лицензия

Proprietary — vnxORACLE Team © 2024-2026
