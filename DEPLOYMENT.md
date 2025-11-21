# 🚀 Развертывание бота на Ubuntu сервере

## 📋 Информация о сервере
- **IP:** 144.124.247.81
- **ОС:** Ubuntu
- **Бот:** Telegram AI Bot с Grok и Google Sheets

---

## 🔧 Шаг 1: Подключение к серверу

### Через SSH:
```bash
ssh root@144.124.247.81
```

Или если у вас есть пользователь:
```bash
ssh username@144.124.247.81
```

---

## 📦 Шаг 2: Установка необходимого ПО

### 1. Обновите систему:
```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Установите Python 3.11+ и pip:
```bash
sudo apt install python3 python3-pip python3-venv -y
```

### 3. Установите Git:
```bash
sudo apt install git -y
```

### 4. Установите screen (для фонового запуска):
```bash
sudo apt install screen -y
```

---

## 📥 Шаг 3: Клонирование проекта

### 1. Создайте директорию для проектов:
```bash
mkdir -p /opt/bots
cd /opt/bots
```

### 2. Клонируйте репозиторий:
```bash
git clone https://github.com/iNv1one/telegram-ai-bot.git
cd telegram-ai-bot
```

---

## ⚙️ Шаг 4: Настройка окружения

### 1. Создайте виртуальное окружение:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Установите зависимости:
```bash
pip install -r requirements.txt
```

### 3. Создайте файл .env:
```bash
nano .env
```

Вставьте ваши настройки:
```env
# Telegram Bot Configuration
BOT_TOKEN=your_bot_token_here

# Grok AI Configuration
GROK_API_KEY=your_grok_api_key_here

# Admin Configuration
ADMIN_ID=your_telegram_user_id

# Google Sheets Configuration
GOOGLE_CREDENTIALS_FILE=credentials.json
GOOGLE_SPREADSHEET_ID=your_spreadsheet_id_here
```

Сохраните: `Ctrl+O`, `Enter`, `Ctrl+X`

### 4. Загрузите credentials.json:

**Вариант 1: Через nano**
```bash
nano credentials.json
```
Вставьте содержимое вашего credentials.json

**Вариант 2: Через SCP (с вашего компьютера)**
```bash
scp C:\vibe\bot\credentials.json root@144.124.247.81:/opt/bots/telegram-ai-bot/
```

### 5. Загрузите фото руководителя (если есть):
```bash
scp C:\vibe\bot\director.jpg root@144.124.247.81:/opt/bots/telegram-ai-bot/
```

---

## 🚀 Шаг 5: Запуск бота

### Вариант 1: Простой запуск (для теста)
```bash
cd /opt/bots/telegram-ai-bot
source .venv/bin/activate
python3 bot.py
```

### Вариант 2: Запуск в фоне с screen
```bash
screen -S telegram-bot
cd /opt/bots/telegram-ai-bot
source .venv/bin/activate
python3 bot.py
```

Выйти из screen: `Ctrl+A`, затем `D`

Вернуться к боту: `screen -r telegram-bot`

Список screen сессий: `screen -ls`

---

## 🔄 Шаг 6: Автозапуск с systemd (рекомендуется)

### 1. Создайте systemd service файл:
```bash
sudo nano /etc/systemd/system/telegram-bot.service
```

### 2. Вставьте следующую конфигурацию:
```ini
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
```

### 3. Активируйте и запустите сервис:
```bash
sudo systemctl daemon-reload
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot
```

### 4. Проверьте статус:
```bash
sudo systemctl status telegram-bot
```

### 5. Просмотр логов:
```bash
sudo journalctl -u telegram-bot -f
```

---

## 📊 Управление ботом

### Остановить бота:
```bash
sudo systemctl stop telegram-bot
```

### Запустить бота:
```bash
sudo systemctl start telegram-bot
```

### Перезапустить бота:
```bash
sudo systemctl restart telegram-bot
```

### Отключить автозапуск:
```bash
sudo systemctl disable telegram-bot
```

---

## 🔄 Обновление бота

### 1. Остановите бота:
```bash
sudo systemctl stop telegram-bot
```

### 2. Обновите код:
```bash
cd /opt/bots/telegram-ai-bot
git pull origin main
```

### 3. Обновите зависимости (если изменились):
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### 4. Запустите бота:
```bash
sudo systemctl start telegram-bot
```

---

## 🔒 Безопасность

### 1. Создайте отдельного пользователя (рекомендуется):
```bash
sudo adduser botuser
sudo usermod -aG sudo botuser
```

### 2. Переместите проект:
```bash
sudo mv /opt/bots /home/botuser/
sudo chown -R botuser:botuser /home/botuser/bots
```

### 3. Обновите service файл (замените User=root на User=botuser)

### 4. Настройте файрволл:
```bash
sudo ufw allow ssh
sudo ufw enable
```

---

## 🐛 Решение проблем

### Бот не запускается:
```bash
# Проверьте логи
sudo journalctl -u telegram-bot -n 50

# Проверьте .env файл
cat /opt/bots/telegram-ai-bot/.env

# Проверьте права доступа
ls -la /opt/bots/telegram-ai-bot/
```

### База данных не создается:
```bash
# Проверьте права на запись
chmod 755 /opt/bots/telegram-ai-bot/
```

### Google Sheets не подключается:
```bash
# Проверьте credentials.json
cat /opt/bots/telegram-ai-bot/credentials.json

# Проверьте GOOGLE_SPREADSHEET_ID в .env
```

---

## 📝 Полезные команды

### Мониторинг ресурсов:
```bash
htop
```

### Проверка свободного места:
```bash
df -h
```

### Проверка сетевых подключений:
```bash
netstat -tulpn | grep python
```

---

## ✅ Готово!

Ваш бот теперь работает на сервере 24/7!

### Проверьте:
1. Откройте бота в Telegram
2. Отправьте `/start`
3. Проверьте все кнопки
4. Задайте вопрос AI

---

## 📞 Быстрая справка

```bash
# Статус бота
sudo systemctl status telegram-bot

# Логи в реальном времени
sudo journalctl -u telegram-bot -f

# Перезапуск
sudo systemctl restart telegram-bot

# Обновление
cd /opt/bots/telegram-ai-bot && git pull && sudo systemctl restart telegram-bot
```
