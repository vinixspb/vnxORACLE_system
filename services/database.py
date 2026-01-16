import sqlite3
import logging

logger = logging.getLogger(__name__)

DB_NAME = "oracle.db"

class Database:
    def __init__(self):
        self.conn = None
        self.create_tables()

    def connect(self):
        """Подключение к файлу базы данных"""
        try:
            self.conn = sqlite3.connect(DB_NAME, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row # Позволяет обращаться к полям по имени
        except Exception as e:
            logger.error(f"❌ DB Connect Error: {e}")

    def create_tables(self):
        """Создание таблиц, если их нет"""
        self.connect()
        try:
            cursor = self.conn.cursor()
            
            # Таблица сообщений (Кто, что сказал, когда)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    role TEXT,
                    content TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            self.conn.commit()
            logger.info("✅ Database connected.")
        except Exception as e:
            logger.error(f"❌ DB Create Tables Error: {e}")

    # --- МЕТОДЫ ---

    def add_message(self, user_id, role, content):
        """Запоминаем сообщение"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO messages (user_id, role, content) VALUES (?, ?, ?)",
                (user_id, role, content)
            )
            self.conn.commit()
        except Exception as e:
            logger.error(f"❌ DB Add Message Error: {e}")

    def get_history(self, user_id, limit=10):
        """Достаем переписку для контекста ИИ"""
        try:
            cursor = self.conn.cursor()
            # Берем последние N сообщений
            query = f"""
                SELECT role, content FROM (
                    SELECT role, content, id FROM messages 
                    WHERE user_id = ? 
                    ORDER BY id DESC LIMIT ?
                ) ORDER BY id ASC
            """
            cursor.execute(query, (user_id, limit))
            rows = cursor.fetchall()
            
            # Превращаем в формат для OpenAI
            return [{"role": row['role'], "content": row['content']} for row in rows]
        except Exception as e:
            logger.error(f"❌ DB Get History Error: {e}")
            return []

    def clear_history(self, user_id):
        """Очищаем память (Удаляем сообщения юзера)"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM messages WHERE user_id = ?", (user_id,))
            self.conn.commit()
        except Exception as e:
            logger.error(f"❌ DB Clear History Error: {e}")
