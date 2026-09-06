# Liquid Glass Chat Bot Integration Guide

**Date**: 2026-09-06  
**Source**: ai-worker-template (branch: feature/web-channel)  
**Target**: vnxORACLE landing page

## Overview

Интеграция омниканального чат-бота с liquid glass каплей-FAB в лендинг vnxORACLE.

## What's Being Integrated

### 1. Liquid Glass Water Drop Button
- Apple Vision Pro материалы (Fresnel effect, dual caustics, chromatic aberration)
- Реалистичная физика деформации (8-corner border-radius morphing)
- Анимация появления падающей капли
- Spring physics для органичного движения
- 60fps на всех устройствах, 5KB total size

### 2. Chat Widget
- Glassmorphism окно чата
- REST API интеграция (polling 3s)
- Telegram deep link для cross-channel handoff
- Session management (UUIDv4 в LocalStorage)

### 3. Backend API
- FastAPI endpoints: `/api/chat/message`, `/api/chat/history`, `/api/chat/updates`
- WebChannel adapter для REST клиентов
- PostgreSQL persistent message history
- Session merging при Telegram linking

## Source Files Location

**In ai-worker-template/web-widget/:**
- `chat-widget.html` - UI + CSS (liquid glass styles)
- `chat-widget.js` - Physics engine + ChatWidget class
- `README.md` - Integration docs

**Backend (ai-worker-template):**
- `core/channels/web.py` - WebChannel adapter
- `core/api/routes.py` - FastAPI endpoints
- `core/handlers/start.py` - Telegram /start handler
- `migrations/003_omnichannel_foundation.sql` - DB schema

## Integration Steps

### Step 1: Copy Widget Files to vnxORACLE

Create directory structure:
```
vnxORACLE_system/landing/public/
├── chat-widget/
│   ├── chat-widget.html
│   ├── chat-widget.js
│   └── chat-widget.css (extract from HTML)
```

### Step 2: Extract CSS from HTML

Split `chat-widget.html` into:
- `chat-widget.html` (markup only)
- `chat-widget.css` (all styles)

### Step 3: Embed in Landing Page

Add to `landing/index.html` before `</body>`:

```html
<!-- Liquid Glass Chat Widget -->
<link rel="stylesheet" href="/chat-widget/chat-widget.css">
<script src="/chat-widget/chat-widget.js"></script>
<script>
  window.chatWidget = new ChatWidget({
    apiUrl: 'https://api.vnxoracle.com/api/chat',
    botUsername: 'vnxoracle_bot',
    pollingInterval: 3000
  });
</script>

<!-- Widget HTML -->
<div class="chat-widget" id="chatWidget">
  <button class="chat-fab" id="chatFab" aria-label="Open chat">
    <svg viewBox="0 0 24 24">
      <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/>
    </svg>
  </button>
  
  <div class="chat-window" id="chatWindow">
    <!-- ... rest of widget markup ... -->
  </div>
</div>
```

### Step 4: Update Configuration

In `chat-widget.js`, update config:

```javascript
document.addEventListener('DOMContentLoaded', () => {
  // Initialize Liquid Glass FAB
  const fab = document.getElementById('chatFab');
  if (fab) {
    new LiquidGlassFAB(fab);
  }

  // Initialize Chat Widget
  window.chatWidget = new ChatWidget({
    apiUrl: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/chat',
    botUsername: import.meta.env.VITE_BOT_USERNAME || 'vnxoracle_bot',
    pollingInterval: 3000
  });
});
```

### Step 5: Add Environment Variables

Create `landing/.env`:

```bash
VITE_API_URL=https://api.vnxoracle.com/api/chat
VITE_BOT_USERNAME=vnxoracle_bot
```

### Step 6: Backend Deployment

**Option A: Use existing ai-worker-template instance**
- Deploy ai-worker-template with FastAPI enabled
- Point landing to its API URL

**Option B: Standalone API server**
- Copy `core/channels/web.py` and `core/api/routes.py` to vnxORACLE/api
- Run FastAPI separately from landing

**Recommended: Option A** - reuse existing infrastructure

### Step 7: Database Setup

Run migration on production DB:

```bash
psql -U your_user -d vnxoracle_db -f migrations/003_omnichannel_foundation.sql
```

Adds:
- `clients.web_session_token` column
- `clients.last_channel` column
- `messages` table for persistent history

### Step 8: Update run.py (if using ai-worker-template)

Add FastAPI to bot startup:

```python
import asyncio
import uvicorn
from fastapi import FastAPI
from core.api import router, init_routes
from core.bot import get_bot, get_dispatcher
from core.db.storage import get_storage
from core.pipeline import get_pipeline

async def main():
    storage = get_storage()
    pipeline = get_pipeline()
    bot = get_bot()
    dp = get_dispatcher()
    
    # NEW: Initialize FastAPI
    app = FastAPI(title="vnxORACLE Bot API")
    init_routes(storage, pipeline)
    app.include_router(router)
    
    # CORS for landing domain
    from fastapi.middleware.cors import CORSMiddleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["https://vnxoracle.com", "http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["*"]
    )
    
    # Run both servers
    config = uvicorn.Config(app, host="0.0.0.0", port=8000)
    server = uvicorn.Server(config)
    
    await asyncio.gather(
        server.serve(),
        dp.start_polling(bot)
    )

if __name__ == '__main__':
    asyncio.run(main())
```

## Customization for vnxORACLE

### Colors

Update CSS variables in `chat-widget.css`:

```css
.chat-fab {
  background:
    /* vnxORACLE brand colors */
    radial-gradient(
      circle at var(--light-x, 35%) var(--light-y, 35%),
      rgba(255,255,255,0.65),
      rgba(255,255,255,0.2) 35%,
      transparent 60%
    ),
    radial-gradient(
      circle at 50% 50%,
      rgba(139, 92, 246, 0.25),  /* purple */
      rgba(168, 85, 247, 0.35)
    ),
    radial-gradient(
      circle at 50% 65%,
      rgba(139, 92, 246, 0.8),
      rgba(168, 85, 247, 0.9)
    );
}
```

### Welcome Message

Update in `chat-widget.html`:

```html
<div class="message bot">
  <div>
    <div class="message-bubble">
      Здравствуйте! Я AI-ассистент vnxORACLE. 
      Помогу настроить голосового бота для вашего бизнеса. Чем могу помочь?
    </div>
  </div>
</div>
```

### Avatar

Replace icon in FAB:

```html
<!-- vnxORACLE logo instead of generic chat icon -->
<button class="chat-fab" id="chatFab">
  <img src="/logo-icon.svg" alt="Chat" style="width: 28px; height: 28px;">
</button>
```

## Testing

### Local Development:

```bash
cd landing
npm run dev
# Visit http://localhost:5173
```

### Test Sequence:

1. **FAB appears** with water drop animation
2. **Hover** - morphing follows cursor
3. **Click** - ripple effect, window opens
4. **Send message** - REST API call works
5. **Telegram banner** appears (if not linked)
6. **Click banner** - opens t.me/vnxoracle_bot?start=<token>
7. **Return to Telegram** - sessions merged

### API Testing:

```bash
# Test message endpoint
curl -X POST http://localhost:8000/api/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "web_session_token": "test-123",
    "message": "Хочу настроить голосового бота"
  }'

# Test history
curl http://localhost:8000/api/chat/history/test-123

# Test updates polling
curl "http://localhost:8000/api/chat/updates/test-123?since_seq_id=0"
```

## Production Deployment

### CDN Optimization:

```html
<!-- Preload critical assets -->
<link rel="preload" href="/chat-widget/chat-widget.css" as="style">
<link rel="preload" href="/chat-widget/chat-widget.js" as="script">

<!-- Async load for non-critical widget -->
<link rel="stylesheet" href="/chat-widget/chat-widget.css" media="print" onload="this.media='all'">
<script src="/chat-widget/chat-widget.js" defer></script>
```

### Minification:

```bash
# CSS
npx csso chat-widget.css -o chat-widget.min.css

# JS
npx terser chat-widget.js -c -m -o chat-widget.min.js
```

Expected sizes:
- CSS: ~3KB gzipped
- JS: ~2KB gzipped
- Total: ~5KB (vs 500KB+ for WebGL alternatives)

### Performance:

- Lazy load: Widget JS loads after page content
- Session storage: Entrance animation plays once
- RAF throttling: Physics paused when tab inactive
- Mobile optimization: Simplified springs on slow devices

## Monitoring

Add analytics:

```javascript
// In chat-widget.js
class ChatWidget {
  constructor(config) {
    // ... existing code ...
    
    // Track widget opens
    this.trackEvent = (event, data) => {
      if (window.gtag) {
        gtag('event', event, {
          event_category: 'chat_widget',
          ...data
        });
      }
    };
  }
  
  open() {
    this.trackEvent('widget_opened');
    // ... rest of open logic ...
  }
  
  async sendMessage() {
    this.trackEvent('message_sent', { 
      message_length: text.length 
    });
    // ... rest of sendMessage logic ...
  }
}
```

## Troubleshooting

### Widget doesn't appear:
- Check browser console for JS errors
- Verify CSS loaded (DevTools Network tab)
- Confirm `chatFab` element exists in DOM

### API calls fail:
- Check CORS headers in browser console
- Verify API_URL environment variable
- Test API endpoints with curl

### Animation stutters:
- Check GPU acceleration: `will-change` hints present?
- Test on target device (not just desktop)
- Reduce `pollingInterval` to 5000ms on mobile

### Telegram linking fails:
- Verify bot username in config
- Check `/start` handler registered in core/bot.py
- Test deep link manually: t.me/bot?start=test-token

## Next Steps

After basic integration:

1. **Add typing indicators from bot side** - via polling or WebSocket
2. **File upload support** - multipart/form-data endpoint
3. **Long polling** - replace 3s polling with asyncio.wait_for()
4. **Secure sync tokens** - temporary tokens instead of web_session_token in URL
5. **Analytics dashboard** - conversation metrics, conversion rates

## Files to Copy

From `ai-worker-template` to `vnxORACLE_system`:

```
ai-worker-template/
├── web-widget/
│   ├── chat-widget.html     → landing/public/chat-widget/
│   ├── chat-widget.js        → landing/public/chat-widget/
│   └── README.md             → docs/CHAT_WIDGET.md
├── core/channels/web.py      → api/channels/web.py (if standalone)
├── core/api/routes.py        → api/routes.py (if standalone)
└── migrations/003_*.sql      → migrations/
```

## Summary

**Effort**: ~2-3 hours for basic integration  
**Dependencies**: FastAPI, asyncpg, pydantic (already in ai-worker-template)  
**Performance**: 60fps on all devices, <5KB payload  
**Browser support**: Chrome 76+, Safari 9+, Firefox 103+, Edge 79+

Ready to integrate!
