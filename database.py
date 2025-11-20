import sqlite3
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

DB_FILE = 'bot_analytics.db'


def init_database():
    """Инициализация базы данных и создание таблиц"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Таблица пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            first_seen TIMESTAMP,
            last_seen TIMESTAMP
        )
    ''')
    
    # Таблица действий (нажатия кнопок)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS actions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action_type TEXT,
            timestamp TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    
    # Таблица заявок
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            phone_number TEXT,
            timestamp TIMESTAMP,
            status TEXT DEFAULT 'new',
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    
    conn.commit()
    conn.close()
    logger.info("База данных инициализирована")


def save_user(user_id, username, first_name, last_name):
    """Сохранение или обновление информации о пользователе"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Проверяем, есть ли пользователь в БД
    cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
    existing_user = cursor.fetchone()
    
    current_time = datetime.now()
    
    if existing_user:
        # Обновляем last_seen
        cursor.execute('''
            UPDATE users 
            SET username = ?, first_name = ?, last_name = ?, last_seen = ?
            WHERE user_id = ?
        ''', (username, first_name, last_name, current_time, user_id))
    else:
        # Добавляем нового пользователя
        cursor.execute('''
            INSERT INTO users (user_id, username, first_name, last_name, first_seen, last_seen)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, username, first_name, last_name, current_time, current_time))
        logger.info(f"Новый пользователь: {user_id} ({first_name})")
    
    conn.commit()
    conn.close()


def log_action(user_id, action_type):
    """Логирование действия пользователя"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO actions (user_id, action_type, timestamp)
        VALUES (?, ?, ?)
    ''', (user_id, action_type, datetime.now()))
    
    conn.commit()
    conn.close()
    logger.info(f"Действие: {action_type} от пользователя {user_id}")


def get_statistics():
    """Получение статистики использования бота"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Общее количество пользователей
    cursor.execute('SELECT COUNT(*) FROM users')
    total_users = cursor.fetchone()[0]
    
    # Количество действий по типам
    cursor.execute('''
        SELECT action_type, COUNT(*) as count 
        FROM actions 
        GROUP BY action_type 
        ORDER BY count DESC
    ''')
    actions_stats = cursor.fetchall()
    
    # Топ активных пользователей
    cursor.execute('''
        SELECT u.user_id, u.first_name, u.username, COUNT(a.id) as action_count
        FROM users u
        LEFT JOIN actions a ON u.user_id = a.user_id
        GROUP BY u.user_id
        ORDER BY action_count DESC
        LIMIT 10
    ''')
    top_users = cursor.fetchall()
    
    conn.close()
    
    return {
        'total_users': total_users,
        'actions_stats': actions_stats,
        'top_users': top_users
    }


def save_application(user_id, phone_number):
    """Сохранение заявки с номером телефона"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO applications (user_id, phone_number, timestamp)
        VALUES (?, ?, ?)
    ''', (user_id, phone_number, datetime.now()))
    
    conn.commit()
    conn.close()
    logger.info(f"Новая заявка от пользователя {user_id}: {phone_number}")


def get_user_info(user_id):
    """Получение информации о пользователе"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT user_id, username, first_name, last_name
        FROM users
        WHERE user_id = ?
    ''', (user_id,))
    
    user_info = cursor.fetchone()
    conn.close()
    
    return user_info
