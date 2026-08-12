# vnxORACLE System Architecture

> **Техническая архитектура экосистемы vnxORACLE**

---

## 🏗 Общая структура

vnxORACLE System — это monorepo, объединяющий два независимых компонента:

```
┌─────────────────────────────────────────┐
│        vnxORACLE Ecosystem              │
├─────────────────────────────────────────┤
│                                         │
│  ┌─────────────┐      ┌──────────────┐ │
│  │   Bot       │      │   Landing    │ │
│  │  (Python)   │      │   (React)    │ │
│  │             │      │              │ │
│  │ Telegram AI │      │ Marketing    │ │
│  │   Backend   │      │   Website    │ │
│  └─────────────┘      └──────────────┘ │
│         │                     │         │
│         │                     │         │
│    AI Models             Users/SEO      │
│   (OpenRouter)          (GitHub Pages)  │
└─────────────────────────────────────────┘
```

---

## 🤖 Bot Architecture

### Technology Stack

- **Runtime:** Python 3.10+
- **Framework:** aiogram 3.x (async Telegram bot framework)
- **Database:** SQLite (user data, history, settings)
- **AI Provider:** OpenRouter API (unified interface)
- **Deployment:** Linux systemd service

### Component Diagram

```
┌──────────────────────────────────────────┐
│           Telegram Bot Layer             │
├──────────────────────────────────────────┤
│                                          │
│  ┌────────────┐  ┌─────────────┐        │
│  │  Handlers  │  │  Keyboards  │        │
│  │  (Routes)  │  │   (UI)      │        │
│  └─────┬──────┘  └──────┬──────┘        │
│        │                │               │
│        └────────┬───────┘               │
│                 │                       │
│        ┌────────▼─────────┐             │
│        │     Services     │             │
│        │  ┌────────────┐  │             │
│        │  │ AI Service │  │             │
│        │  │ DB Service │  │             │
│        │  │ Voice/Video│  │             │
│        │  └────────────┘  │             │
│        └──────────────────┘             │
│                 │                       │
│        ┌────────▼─────────┐             │
│        │   OpenRouter API │             │
│        │  (GPT/Claude/...) │             │
│        └──────────────────┘             │
└──────────────────────────────────────────┘
```

### Data Flow

```
User → Telegram → Bot Handlers → Services → OpenRouter → AI Model
                                     ↓
                                 Database
                                     ↓
Response ← Telegram ← Bot Handlers ← Services ← AI Response
```

### Key Modules

- **`main.py`** — entry point, bot initialization
- **`loader.py`** — bot, dispatcher, router setup
- **`config.py`** — environment variables, settings
- **`handlers/`** — command and message handlers
- **`services/`** — business logic (AI, DB, media)
- **`keyboards/`** — inline and reply keyboards

---

## 🌐 Landing Architecture

### Technology Stack

- **Framework:** React 19 (latest)
- **Build Tool:** Vite 5.x
- **Animations:** Framer Motion (`motion` package)
- **Icons:** Lucide React
- **Styling:** Plain CSS (CSS Grid + Flexbox)
- **Fonts:** Google Fonts (Inter)
- **Deployment:** GitHub Pages / Vercel

### Component Structure

```
┌────────────────────────────────┐
│         App.jsx (Root)         │
├────────────────────────────────┤
│                                │
│  ┌──────────────────────────┐  │
│  │   Navbar (Fixed Top)     │  │
│  │  - Logo + Brand          │  │
│  │  - Menu Button           │  │
│  │  - Tag Pills             │  │
│  └──────────────────────────┘  │
│                                │
│  ┌──────────────────────────┐  │
│  │  Video Background        │  │
│  │  (Absolute, z-index: 0)  │  │
│  └──────────────────────────┘  │
│                                │
│  ┌──────────────────────────┐  │
│  │   Footer Content         │  │
│  │  - Subtitle + Dot        │  │
│  │  - Heading (2 lines)     │  │
│  │  - CTA Buttons           │  │
│  │  - Tag Pills             │  │
│  └──────────────────────────┘  │
│                                │
└────────────────────────────────┘
```

### Animation Timeline (Framer Motion)

```
0.0s ─► Navbar slides down (y: -16 → 0, opacity: 0 → 1)
0.0s ─► Video fades in (opacity: 0 → 1, scale: 1.05 → 1)
0.5s ─► Footer wrapper slides up
0.6s ─► Subtitle animates
0.8s ─► Heading animates
1.0s ─► Buttons animate
```

### Build Pipeline

```
Source (JSX/CSS) → Vite (esbuild) → dist/ → GitHub Pages
                      ↓
                 Hot Module Replacement (dev)
```

---

## 🚀 Deployment Architecture

### Bot Deployment

```
GitHub Repo → Git Pull → Server (MATRIXde-n1)
                            ↓
                    /opt/bots/vnxORACLE_system/bot/
                            ↓
                    systemd service (auto-restart)
                            ↓
                    Running Bot Process
```

**Server:** MATRIXde-n1  
**Path:** `/opt/bots/vnxORACLE_system/bot/`  
**Service:** `vnxoracle-bot.service`  
**Auto-start:** Yes (systemd enabled)

### Landing Deployment

```
GitHub Repo → GitHub Actions → Build (Vite) → GitHub Pages
                                   ↓
                              dist/ artifacts
                                   ↓
                           Public URL (HTTPS)
```

**Target:** GitHub Pages  
**Branch:** `gh-pages` (auto-generated)  
**URL:** `https://vinixspb.github.io/vnxORACLE_system/`

---

## 🔒 Security Considerations

### Bot

- ✅ Environment variables (`.env`) — не в git
- ✅ Whitelist пользователей (ADMIN_IDS)
- ✅ Rate limiting (планируется)
- ✅ Input validation
- ⚠️ API keys rotation (manual)

### Landing

- ✅ Static site (no backend) — low attack surface
- ✅ HTTPS only (GitHub Pages enforced)
- ✅ No user data collection
- ✅ No cookies/tracking (пока)

---

## 📊 Scalability

### Current State

- **Bot:** Single instance, ~100-500 users
- **Landing:** Static CDN, unlimited traffic

### Future Growth

- **Bot:** Horizontal scaling → multiple instances + Redis
- **Landing:** CDN (Cloudflare) → global edge caching

---

## 🔧 Development Workflow

```
Developer → Feature Branch → PR → Code Review → Merge → Deploy
              site_*           ↓
              bot_*         Tests
                              ↓
                          Production
```

**Branch naming:**
- `site_*` — landing page changes
- `bot_*` — bot functionality changes
- `docs_*` — documentation updates

---

## 📚 Tech Debt & TODOs

### Bot
- [ ] Migrate to PostgreSQL (from SQLite)
- [ ] Add Redis for caching
- [ ] Implement rate limiting
- [ ] Add monitoring (Prometheus + Grafana)
- [ ] Unit tests coverage > 80%

### Landing
- [ ] Add SEO meta tags
- [ ] Implement analytics (Google Analytics)
- [ ] Add more sections (Features, Pricing, FAQ)
- [ ] A/B testing framework
- [ ] Performance monitoring (Lighthouse CI)

---

## 📄 References

- [Bot README](../bot/README.md)
- [Landing README](../landing/README.md)
- [Deployment Guide](./DEPLOYMENT.md)
