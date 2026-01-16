import sqlite3
import logging
import json
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

DB_NAME = "oracle.db"

class Database:
    def __init__(self):
        self.conn = None
        self.create_tables()

    def connect(self):
        try:
            # check_same_thread=False нужен, так как Telegram работает в многопотоке
            self.conn = sqlite3.connect(DB_NAME, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row # Чтобы обращаться к полям по имени
        except Exception as e:
            logger.error(f"❌ DB Connection Error: {e}")

    def create_tables(self):
        """Создает структуру базы данных, если её нет"""
        self.connect()
        try:
            cursor = self.conn.cursor()
            
            # Таблица пользователей (храним тариф и лимиты)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    tariff TEXT DEFAULT 'START',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Таблица истории сообщений
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    role TEXT, -- 'user' или 'assistant'
                    content TEXT,
                    model_used TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            self.conn.commit()
            logger.info("✅ Database tables checked/created.")
        except Exception as e:
            logger.error(f"❌ DB Creation Error: {e}")

    # --- РАБОТА С ЮЗЕРОМ ---
    
    def register_user(self, user_id, username):
        """Регистрирует юзера, если его нет"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", 
                (user_id, username)
            )
            self.conn.commit()
        except Exception as e:
            logger.error(f"DB Register User Error: {e}")

    def get_user_tariff(self, user_id):
        """Узнаем тариф пользователя"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT tariff FROM users WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            return result['tariff'] if result else 'START'
        except Exception:
            return 'START'

    # --- РАБОТА С ИСТОРИЕЙ ---

    def add_message(self, user_id, role, content, model=""):
        """Записывает сообщение в историю"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO messages (user_id, role, content, model_used) VALUES (?, ?, ?, ?)",
                (user_id, role, content, model)
            )
            self.conn.commit()
        except Exception as e:
            logger.error(f"DB Add Message Error: {e}")

    def get_history(self, user_id, limit=10):
        """
        Достает последние N сообщений для контекста.
        Возвращает в формате списка словарей для OpenAI.
        """
        try:
            cursor = self.conn.cursor()
            # Берем последние N сообщений, но сортируем их в правильном порядке (от старых к новым)
            query = f"""
                SELECT * FROM (
                    SELECT role, content 
                    FROM messages 
                    WHERE user_id = ? 
                    ORDER BY id DESC 
                    LIMIT ?
                ) ORDER BY id ASC
            """
            cursor.execute(query, (user_id, limit))
            rows = cursor.fetchall()
            
            history = [{"role": row['role'], "content": row['content']} for row in rows]
            return history
        except Exception as e:
            logger.error(f"DB Get History Error: {e}")
            return []

    def clear_history(self, user_id):
        """Очищает историю (мягкое удаление или просто флаг, пока удаляем физически)"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM messages WHERE user_id = ?", (user_id,))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"DB Clear History Error: {e}")
            return False
