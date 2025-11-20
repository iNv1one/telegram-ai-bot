import logging
import httpx
import os
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import database
import google_sheets

# Загружаем переменные окружения из .env файла
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Загружаем конфигурацию из переменных окружения
TOKEN = os.getenv('BOT_TOKEN')
GROK_API_KEY = os.getenv('GROK_API_KEY')
ADMIN_ID = int(os.getenv('ADMIN_ID', '0'))

# Google Sheets конфигурация
GOOGLE_CREDENTIALS_FILE = os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')
GOOGLE_SPREADSHEET_ID = os.getenv('GOOGLE_SPREADSHEET_ID', '')

# Состояния для обработки заявки
WAITING_FOR_PHONE = 1


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start - приветствует пользователя и показывает клавиатуру"""
    user = update.effective_user
    
    # Сохраняем информацию о пользователе
    database.save_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name
    )
    
    # Логируем действие
    database.log_action(user.id, 'start')
    
    # Создаем кнопки клавиатуры
    keyboard = [
        [KeyboardButton("О нас"), KeyboardButton("Кейсы")],
        [KeyboardButton("👤 Руководитель"), KeyboardButton("📞 Номер телефона")]
    ]
    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,  # Подстраивает размер кнопок под экран
        one_time_keyboard=False  # Клавиатура не исчезает после нажатия
    )
    
    # Приветствие пользователя
    await update.message.reply_text(
        f'Привет, {user.first_name}! 👋\n\n'
        f'Я бот-помощник. Выберите интересующий раздел:',
        reply_markup=reply_markup
    )


async def ask_grok(question: str) -> str:
    """Отправка вопроса к Grok AI и получение ответа"""
    try:
        # Получаем системный промпт из Google Sheets
        sheets_manager = google_sheets.get_sheets_manager()
        if sheets_manager:
            system_prompt = sheets_manager.get_system_prompt()
            ai_params = sheets_manager.get_ai_parameters()
        else:
            # Значения по умолчанию, если Google Sheets недоступен
            system_prompt = "Ты helpful AI-ассистент. Отвечай на русском языке кратко и по делу."
            ai_params = {
                'model': 'grok-beta',
                'temperature': 0.7
            }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.x.ai/v1/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {GROK_API_KEY}"
                },
                json={
                    "messages": [
                        {
                            "role": "system",
                            "content": system_prompt
                        },
                        {
                            "role": "user",
                            "content": question
                        }
                    ],
                    "model": ai_params.get('model', 'grok-3-mini'),
                    "stream": False,
                    "temperature": ai_params.get('temperature', 0.7)
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return data['choices'][0]['message']['content']
            else:
                logger.error(f"Grok API error: {response.status_code} - {response.text}")
                return "Извините, произошла ошибка при обработке вашего вопроса. Попробуйте позже."
                
    except Exception as e:
        logger.error(f"Error calling Grok API: {e}")
        return "Произошла ошибка при связи с AI. Пожалуйста, попробуйте позже."


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /stats - показывает статистику администратору"""
    user = update.effective_user
    
    # Проверяем права доступа
    if user.id == ADMIN_ID:
        database.log_action(user.id, 'view_statistics')
        stats_data = database.get_statistics()
        
        # Формируем сообщение со статистикой
        message = "📊 *СТАТИСТИКА БОТА*\n\n"
        message += f"👥 Всего пользователей: *{stats_data['total_users']}*\n\n"
        
        if stats_data['actions_stats']:
            message += "📈 *Действия:*\n"
            total_actions = sum(count for _, count in stats_data['actions_stats'])
            action_names = {
                'start': '🚀 /start',
                'button_about': '📌 О нас',
                'button_cases': '💼 Кейсы',
                'view_statistics': '📊 Статистика'
            }
            for action_type, count in stats_data['actions_stats']:
                action_name = action_names.get(action_type, action_type)
                percentage = (count / total_actions * 100) if total_actions > 0 else 0
                message += f"  • {action_name}: {count} ({percentage:.1f}%)\n"
            message += f"\n✅ Всего действий: *{total_actions}*\n\n"
        
        if stats_data['top_users']:
            message += "🏆 *ТОП-5 пользователей:*\n"
            for i, (user_id, first_name, username, action_count) in enumerate(stats_data['top_users'][:5], 1):
                username_str = f"@{username}" if username else "без username"
                message += f"{i}. {first_name} ({username_str}) - {action_count} действий\n"
        
        await update.message.reply_text(message, parse_mode='Markdown')
    else:
        # Для обычных пользователей статистика недоступна
        await update.message.reply_text(
            "У вас нет доступа к этой команде."
        )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик текстовых сообщений (нажатий на кнопки)"""
    text = update.message.text
    user = update.effective_user
    
    if text == "О нас":
        database.log_action(user.id, 'button_about')
        await update.message.reply_text(
            "📌 *О нас*\n\n"
            "Мы - команда профессионалов, которая занимается разработкой "
            "инновационных решений для вашего бизнеса.\n\n"
            "Наша миссия - делать мир лучше с помощью технологий!",
            parse_mode='Markdown'
        )
    elif text == "Кейсы":
        database.log_action(user.id, 'button_cases')
        
        # Клавиатура с кнопкой для заявки
        keyboard = [
            [KeyboardButton("📞 Оставить заявку")],
            [KeyboardButton("⬅️ Назад в меню")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(
            "💼 *Наши кейсы*\n\n"
            "1 Разработка мобильного приложения для доставки\n"
            "2 Создание CRM-системы для автоматизации продаж\n"
            "3 Внедрение AI-чатбота для службы поддержки\n\n"
            "Более 100 успешных проектов реализовано!\n\n"
            "🎁 *Хотите получить наш продукт?*\n"
            "Оставьте заявку, и мы свяжемся с вами!",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    elif text == "Руководитель":
        database.log_action(user.id, 'button_director')
        
        # Путь к фото руководителя
        photo_path = 'director.jpg'
        
        # Описание руководителя
        caption = (
            "👤 *Наш руководитель*\n\n"
            "*Иван Иванов*\n"
            "Генеральный директор\n\n"
            "• 15+ лет опыта в IT-индустрии\n"
            "• Управляет командой из 50+ специалистов\n"
            "• Реализовал более 200 успешных проектов\n\n"
            "_\"Наша цель - создавать решения, которые меняют бизнес к лучшему!\"_"
        )
        
        try:
            # Отправляем фото с описанием
            with open(photo_path, 'rb') as photo:
                await update.message.reply_photo(
                    photo=photo,
                    caption=caption,
                    parse_mode='Markdown'
                )
        except FileNotFoundError:
            # Если фото не найдено, отправляем только текст
            await update.message.reply_text(
                f"{caption}\n\n⚠️ _Фото временно недоступно_",
                parse_mode='Markdown'
            )
    elif text == "📞 Номер телефона":
        database.log_action(user.id, 'button_phone')
        await update.message.reply_text(
            "📞 *Наш контактный номер телефона:*\n\n"
            "`88005553535351312`\n\n"
            "Звоните в любое время! Мы работаем 24/7 🕐",
            parse_mode='Markdown'
        )
    elif text == "⬅️ Назад в меню":
        # Возвращаем основное меню
        keyboard = [
            [KeyboardButton("О нас"), KeyboardButton("Кейсы")],
            [KeyboardButton("👤 Руководитель"), KeyboardButton("📞 Номер телефона")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(
            "Главное меню:",
            reply_markup=reply_markup
        )
    else:
        # Если сообщение не соответствует кнопкам, отправляем вопрос в Grok AI
        database.log_action(user.id, 'ai_question')
        
        # Отправляем индикатор печатания
        await update.message.chat.send_action("typing")
        
        # Получаем ответ от Grok
        ai_response = await ask_grok(text)
        
        # Отправляем ответ пользователю
        await update.message.reply_text(
            f"🤖 *Grok AI отвечает:*\n\n{ai_response}",
            parse_mode='Markdown'
        )


async def request_application(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начало процесса оформления заявки"""
    user = update.effective_user
    database.log_action(user.id, 'start_application')
    
    await update.message.reply_text(
        "📞 *Оставить заявку*\n\n"
        "Отлично! Чтобы мы могли с вами связаться, "
        "пожалуйста, отправьте ваш номер телефона.\n\n"
        "Формат: +7XXXXXXXXXX или 8XXXXXXXXXX\n\n"
        "Или нажмите \"Отмена\" для возврата в меню.",
        parse_mode='Markdown',
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton("❌ Отмена")]],
            resize_keyboard=True
        )
    )
    return WAITING_FOR_PHONE


async def receive_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка полученного номера телефона"""
    user = update.effective_user
    phone = update.message.text
    
    # Проверка на отмену
    if phone == "❌ Отмена":
        return await cancel_application(update, context)
    
    # Базовая валидация номера телефона
    import re
    phone_clean = re.sub(r'[^\d+]', '', phone)
    
    if len(phone_clean) < 11 or not (phone_clean.startswith('+7') or phone_clean.startswith('8') or phone_clean.startswith('7')):
        await update.message.reply_text(
            "❌ Неверный формат номера телефона.\n\n"
            "Пожалуйста, введите номер в формате:\n"
            "+7XXXXXXXXXX или 8XXXXXXXXXX"
        )
        return WAITING_FOR_PHONE
    
    # Сохраняем заявку в базу данных
    database.save_application(user.id, phone)
    database.log_action(user.id, 'application_submitted')
    
    # Отправляем уведомление администратору
    try:
        user_info = database.get_user_info(user.id)
        if user_info:
            _, username, first_name, last_name = user_info
            username_str = f"@{username}" if username else "без username"
            full_name = f"{first_name} {last_name or ''}".strip()
            
            admin_message = (
                "🔔 *НОВАЯ ЗАЯВКА!*\n\n"
                f"👤 Клиент: {full_name}\n"
                f"🆔 Username: {username_str}\n"
                f"🆔 User ID: {user.id}\n"
                f"📞 Телефон: `{phone}`\n\n"
                "Свяжитесь с клиентом как можно скорее!"
            )
            
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=admin_message,
                parse_mode='Markdown'
            )
    except Exception as e:
        logger.error(f"Ошибка отправки уведомления админу: {e}")
    
    # Благодарим пользователя
    keyboard = [
        [KeyboardButton("О нас"), KeyboardButton("Кейсы")],
        [KeyboardButton("👤 Руководитель"), KeyboardButton("📞 Номер телефона")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "✅ *Спасибо за вашу заявку!*\n\n"
        f"Мы получили ваш номер телефона: {phone}\n\n"
        "Наш менеджер свяжется с вами в ближайшее время.\n"
        "Обычно это занимает не более 15 минут! 🚀",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )
    
    return ConversationHandler.END


async def cancel_application(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отмена оформления заявки"""
    keyboard = [
        [KeyboardButton("О нас"), KeyboardButton("Кейсы")],
        [KeyboardButton("👤 Руководитель"), KeyboardButton("📞 Номер телефона")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "Заявка отменена. Возвращаю вас в главное меню.",
        reply_markup=reply_markup
    )
    
    return ConversationHandler.END


def main() -> None:
    """Запуск бота"""
    # Инициализируем базу данных
    database.init_database()
    
    # Инициализируем Google Sheets (опционально)
    if GOOGLE_SPREADSHEET_ID and os.path.exists(GOOGLE_CREDENTIALS_FILE):
        sheets_manager = google_sheets.init_sheets_manager(
            GOOGLE_CREDENTIALS_FILE,
            GOOGLE_SPREADSHEET_ID
        )
        if sheets_manager:
            logger.info("✅ Google Sheets успешно подключен")
        else:
            logger.warning("⚠️ Google Sheets не подключен, используются значения по умолчанию")
    else:
        logger.warning("⚠️ Google Sheets не настроен, используются значения по умолчанию")
    
    # Создаем приложение
    application = Application.builder().token(TOKEN).build()
    
    # ConversationHandler для обработки заявок
    application_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex('^📞 Оставить заявку$'), request_application)
        ],
        states={
            WAITING_FOR_PHONE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_phone)
            ]
        },
        fallbacks=[
            MessageHandler(filters.Regex('^❌ Отмена$'), cancel_application)
        ]
    )
    
    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(application_handler)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Запускаем бота
    logger.info("Бот запущен!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
