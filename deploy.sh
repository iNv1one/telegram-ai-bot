#!/bin/bash

# 🚀 Скрипт автоматической установки Telegram AI Bot на Ubuntu
# Использование: bash deploy.sh

set -e

echo "🤖 Установка Telegram AI Bot"
echo "=============================="
echo ""

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Функция для вывода сообщений
info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 1. Обновление системы
info "Обновление системы..."
sudo apt update && sudo apt upgrade -y

# 2. Установка необходимого ПО
info "Установка Python, Git и screen..."
sudo apt install -y python3 python3-pip python3-venv git screen

# 3. Создание директории для бота
info "Создание директории для бота..."
sudo mkdir -p /opt/bots
cd /opt/bots

# 4. Клонирование репозитория
if [ -d "telegram-ai-bot" ]; then
    warn "Директория telegram-ai-bot уже существует. Обновляем..."
    cd telegram-ai-bot
    git pull origin main
else
    info "Клонирование репозитория..."
    sudo git clone https://github.com/iNv1one/telegram-ai-bot.git
    cd telegram-ai-bot
fi

# 5. Создание виртуального окружения
info "Создание виртуального окружения..."
python3 -m venv .venv
source .venv/bin/activate

# 6. Установка зависимостей
info "Установка зависимостей Python..."
pip install --upgrade pip
pip install -r requirements.txt

# 7. Создание .env файла (если не существует)
if [ ! -f ".env" ]; then
    warn ".env файл не найден. Создаю из примера..."
    cp .env.example .env
    error "⚠️  ВАЖНО: Отредактируйте .env файл и добавьте ваши токены!"
    echo ""
    echo "Используйте команду: sudo nano /opt/bots/telegram-ai-bot/.env"
else
    info ".env файл уже существует"
fi

# 8. Проверка credentials.json
if [ ! -f "credentials.json" ]; then
    warn "credentials.json не найден"
    warn "Загрузите его через: scp credentials.json root@YOUR_SERVER:/opt/bots/telegram-ai-bot/"
fi

# 9. Создание systemd service
info "Создание systemd service..."
sudo tee /etc/systemd/system/telegram-bot.service > /dev/null <<EOF
[Unit]
Description=Telegram AI Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/bots/telegram-ai-bot
Environment="PATH=/opt/bots/telegram-ai-bot/.venv/bin"
ExecStart=/opt/bots/telegram-ai-bot/.venv/bin/python3 bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 10. Активация и запуск сервиса
info "Активация сервиса..."
sudo systemctl daemon-reload
sudo systemctl enable telegram-bot

# 11. Установка прав доступа
info "Настройка прав доступа..."
sudo chmod 755 /opt/bots/telegram-ai-bot
sudo chmod 600 /opt/bots/telegram-ai-bot/.env 2>/dev/null || true

echo ""
echo "=============================="
echo -e "${GREEN}✅ Установка завершена!${NC}"
echo "=============================="
echo ""
echo "📝 Следующие шаги:"
echo ""
echo "1. Отредактируйте .env файл:"
echo "   sudo nano /opt/bots/telegram-ai-bot/.env"
echo ""
echo "2. Загрузите credentials.json (если используете Google Sheets):"
echo "   scp credentials.json root@YOUR_SERVER:/opt/bots/telegram-ai-bot/"
echo ""
echo "3. Запустите бота:"
echo "   sudo systemctl start telegram-bot"
echo ""
echo "4. Проверьте статус:"
echo "   sudo systemctl status telegram-bot"
echo ""
echo "5. Просмотр логов:"
echo "   sudo journalctl -u telegram-bot -f"
echo ""
echo "=============================="
