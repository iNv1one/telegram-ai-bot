# 🔧 Настройка Google Sheets

## Быстрая настройка

1. Создайте Google Cloud Project на https://console.cloud.google.com/
2. Включите Google Sheets API
3. Создайте Service Account и скачайте `credentials.json`
4. Создайте Google Таблицу с листом "Настройки"
5. Дайте доступ Service Account (email из credentials.json)
6. Добавьте ID таблицы в `.env`

## Формат таблицы

Лист "Настройки":

| A              | B                  |
|----------------|---------------------|
| System Prompt  | Ваш промпт для AI  |
| AI_Model       | grok-beta          |
| AI_Temperature | 0.7                |

Подробная инструкция: https://docs.google.com/document/d/your-doc-id
