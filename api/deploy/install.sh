#!/bin/bash

# =========================================================
# 🚀 vnxORACLE API Deployment Script
# =========================================================
# Безопасное развертывание Web API для сайта
# Не трогает существующий Telegram Bot
# =========================================================

set -e  # Остановка при ошибке

echo "=========================================="
echo "🚀 vnxORACLE API Deployment"
echo "=========================================="

# Проверка, что мы на сервере
if [ ! -d "/opt/vnxORACLE_system" ]; then
    echo "❌ Ошибка: /opt/vnxORACLE_system не найден"
    echo "Скрипт должен запускаться на production сервере"
    exit 1
fi

# Переход в директорию API
cd /opt/vnxORACLE_system/api

echo ""
echo "📦 Шаг 1: Создание виртуального окружения..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Виртуальное окружение создано"
else
    echo "⚠️  Виртуальное окружение уже существует"
fi

echo ""
echo "📚 Шаг 2: Установка зависимостей..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Зависимости установлены"

echo ""
echo "🔐 Шаг 3: Проверка .env файла..."
if [ ! -f ".env" ]; then
    echo "❌ Файл .env не найден!"
    echo "Скопируйте .env.example и заполните ключи:"
    echo "  cp .env.example .env"
    echo "  nano .env"
    exit 1
fi

# Проверка обязательных переменных
required_vars=("OPENROUTER_API_KEY_START" "GOOGLE_CREDENTIALS_JSON" "SPREADSHEET_ID")
missing_vars=()

for var in "${required_vars[@]}"; do
    if ! grep -q "^${var}=" .env || grep -q "^${var}=$" .env; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -ne 0 ]; then
    echo "⚠️  Внимание: Не заполнены переменные в .env:"
    printf '   - %s\n' "${missing_vars[@]}"
    read -p "Продолжить установку? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Установка отменена"
        exit 1
    fi
else
    echo "✅ .env файл корректен"
fi

echo ""
echo "📁 Шаг 4: Создание директории для логов..."
sudo mkdir -p /var/log/vnxoracle-api
sudo chown $USER:$USER /var/log/vnxoracle-api
echo "✅ Директория создана"

echo ""
echo "🔧 Шаг 5: Установка systemd service..."
sudo cp deploy/vnx-oracle-api.service /etc/systemd/system/
sudo systemctl daemon-reload
echo "✅ Service установлен"

echo ""
echo "🌐 Шаг 6: Проверка nginx конфигурации..."
if [ -f "/etc/nginx/sites-available/vnxoracle-api" ]; then
    echo "⚠️  Конфигурация nginx уже существует"
else
    echo "📝 Создайте конфигурацию nginx вручную:"
    echo ""
    echo "sudo nano /etc/nginx/sites-available/vnxoracle-api"
    echo ""
    cat deploy/nginx.conf
    echo ""
    echo "Затем выполните:"
    echo "  sudo ln -s /etc/nginx/sites-available/vnxoracle-api /etc/nginx/sites-enabled/"
    echo "  sudo nginx -t"
    echo "  sudo systemctl reload nginx"
fi

echo ""
echo "🧪 Шаг 7: Тестовый запуск API..."
echo "Проверяем, что API может запуститься..."
timeout 5 venv/bin/uvicorn main:app --host 127.0.0.1 --port 8001 || true
echo "✅ Тест завершен"

echo ""
echo "=========================================="
echo "✅ Установка завершена!"
echo "=========================================="
echo ""
echo "📋 Следующие шаги:"
echo ""
echo "1. Запустить API:"
echo "   sudo systemctl start vnx-oracle-api"
echo ""
echo "2. Проверить статус:"
echo "   sudo systemctl status vnx-oracle-api"
echo ""
echo "3. Посмотреть логи:"
echo "   sudo journalctl -u vnx-oracle-api -f"
echo ""
echo "4. Включить автозапуск:"
echo "   sudo systemctl enable vnx-oracle-api"
echo ""
echo "5. Добавить в .bashrc алиасы:"
echo "   alias oracle-api-restart='systemctl restart vnx-oracle-api && journalctl -u vnx-oracle-api -f'"
echo "   alias oracle-api-logs='journalctl -u vnx-oracle-api -f'"
echo "   alias oracle-api-stop='systemctl stop vnx-oracle-api'"
echo "   alias oracle-api-start='systemctl start vnx-oracle-api'"
echo ""
echo "=========================================="
echo "🎯 API будет доступен на http://localhost:8000"
echo "📖 Документация: http://localhost:8000/docs"
echo "=========================================="
