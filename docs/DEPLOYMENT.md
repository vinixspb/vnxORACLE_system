# vnxORACLE System Deployment Guide

> **Инструкции по деплою и настройке производственного окружения**

---

## 🤖 Bot Deployment

### Prerequisites

- Linux сервер (Ubuntu 20.04+ / Debian 11+)
- Python 3.10+
- Git
- systemd

### Step 1: Clone Repository

```bash
cd /opt/bots
git clone https://github.com/vinixspb/vnxORACLE_system.git
cd vnxORACLE_system/bot
```

### Step 2: Setup Python Environment

```bash
# Создать виртуальное окружение
python3 -m venv venv
source venv/bin/activate

# Установить зависимости
pip install -r requirements.txt
```

### Step 3: Configure Environment

```bash
# Создать .env файл
cp .env.example .env
nano .env
```

**Required variables:**
```env
BOT_TOKEN=your_telegram_bot_token_here
OPENROUTER_API_KEY=your_openrouter_api_key_here
ADMIN_IDS=123456789,987654321
DATABASE_PATH=./data/bot.db
```

### Step 4: Create systemd Service

```bash
sudo nano /etc/systemd/system/vnxoracle-bot.service
```

**Service file content:**
```ini
[Unit]
Description=vnxORACLE Telegram Bot
After=network.target

[Service]
Type=simple
User=botuser
Group=botuser
WorkingDirectory=/opt/bots/vnxORACLE_system/bot
Environment="PATH=/opt/bots/vnxORACLE_system/bot/venv/bin"
ExecStart=/opt/bots/vnxORACLE_system/bot/venv/bin/python main.py
Restart=always
RestartSec=10
StandardOutput=append:/var/log/vnxoracle-bot/output.log
StandardError=append:/var/log/vnxoracle-bot/error.log

[Install]
WantedBy=multi-user.target
```

### Step 5: Create Log Directory

```bash
sudo mkdir -p /var/log/vnxoracle-bot
sudo chown botuser:botuser /var/log/vnxoracle-bot
```

### Step 6: Enable and Start Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable auto-start
sudo systemctl enable vnxoracle-bot

# Start service
sudo systemctl start vnxoracle-bot

# Check status
sudo systemctl status vnxoracle-bot
```

### Step 7: Verify Deployment

```bash
# Check logs
sudo journalctl -u vnxoracle-bot -f

# Or check log files directly
tail -f /var/log/vnxoracle-bot/output.log
```

---

## 🌐 Landing Deployment (GitHub Pages)

### Method 1: Automatic (GitHub Actions) ✅ Recommended

**Настройка уже включена в репозиторий!**

1. **Enable GitHub Pages:**
   - Перейти на https://github.com/vinixspb/vnxORACLE_system/settings/pages
   - Source: GitHub Actions
   - Сохранить

2. **Push to main branch:**
   ```bash
   git push origin main
   ```

3. **GitHub Actions automatically:**
   - Соберет landing (`npm run build`)
   - Задеплоит на GitHub Pages
   - URL: https://vinixspb.github.io/vnxORACLE_system/

4. **Monitor deployment:**
   - Actions tab: https://github.com/vinixspb/vnxORACLE_system/actions

### Method 2: Manual (Vercel)

```bash
cd landing

# Install Vercel CLI
npm i -g vercel

# Deploy
vercel deploy --prod
```

### Method 3: Manual (Netlify)

```bash
cd landing

# Install Netlify CLI
npm i -g netlify-cli

# Build
npm run build

# Deploy
netlify deploy --prod --dir=dist
```

---

## 🔄 Update Procedures

### Update Bot

```bash
# SSH to server
ssh user@server

# Navigate to bot directory
cd /opt/bots/vnxORACLE_system/bot

# Pull latest changes
git pull origin main

# Activate venv
source venv/bin/activate

# Update dependencies (if needed)
pip install -r requirements.txt --upgrade

# Restart service
sudo systemctl restart vnxoracle-bot

# Check status
sudo systemctl status vnxoracle-bot
```

### Update Landing

**Automatic (GitHub Actions):**
```bash
# Local machine
git add landing/
git commit -m "Update landing page"
git push origin main
# GitHub Actions will auto-deploy
```

**Manual:**
```bash
cd landing
npm run build
# Upload dist/ to hosting
```

---

## 🔧 Troubleshooting

### Bot Issues

**Service not starting:**
```bash
# Check logs
sudo journalctl -u vnxoracle-bot -n 100 --no-pager

# Check Python errors
python main.py  # Run manually to see errors
```

**Database errors:**
```bash
# Check database file permissions
ls -la data/bot.db

# Reset database (CAUTION: data loss!)
rm data/bot.db
python main.py  # Will recreate DB
```

**API errors:**
```bash
# Verify .env file
cat .env | grep -v "^#"

# Test OpenRouter API
curl -X POST https://openrouter.ai/api/v1/chat/completions \
  -H "Authorization: Bearer $OPENROUTER_API_KEY"
```

### Landing Issues

**Build fails:**
```bash
cd landing
rm -rf node_modules package-lock.json
npm install
npm run build
```

**GitHub Pages not updating:**
- Check Actions tab for errors
- Verify GitHub Pages settings (Source: GitHub Actions)
- Clear browser cache (Ctrl+Shift+R)

---

## 📊 Monitoring

### Bot Monitoring

```bash
# View live logs
sudo journalctl -u vnxoracle-bot -f

# Check service status
sudo systemctl status vnxoracle-bot

# Check resource usage
ps aux | grep python
top -p $(pgrep -f "python main.py")
```

### Landing Monitoring

- **GitHub Actions:** https://github.com/vinixspb/vnxORACLE_system/actions
- **GitHub Pages Status:** Settings → Pages
- **Uptime:** Use UptimeRobot or similar

---

## 🔒 Security Checklist

- [x] `.env` файлы не в Git (проверено в `.gitignore`)
- [x] API keys в environment variables
- [ ] SSL/TLS для бота (если используется webhook)
- [x] HTTPS для landing (GitHub Pages enforce)
- [ ] Rate limiting на bot (TODO)
- [ ] Firewall правила на сервере
- [ ] Regular backups базы данных
- [ ] Log rotation настроен

---

## 📈 Performance Optimization

### Bot

- [ ] Migrate to PostgreSQL (from SQLite) для scale
- [ ] Add Redis для кеширования
- [ ] Implement connection pooling
- [ ] Add monitoring (Prometheus + Grafana)

### Landing

- [x] Vite production build (minified)
- [x] CDN (GitHub Pages)
- [ ] Add Cloudflare для global CDN
- [ ] Image optimization
- [ ] Lazy loading video

---

## 📞 Support

**Issues:** https://github.com/vinixspb/vnxORACLE_system/issues  
**Team:** vnxORACLE Development Team
