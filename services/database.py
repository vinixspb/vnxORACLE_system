import sqlite3
import logging

logger = logging.getLogger(__name__)

DB_NAME = "oracle.db"

class Database:
    def __init__(self):
        self.conn = None
        self.create_tables()

    def connect(self):
        try:
            self.conn = sqlite3.connect(DB_NAME, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row 
        except Exception as e:
            logger.error(f"❌ DB Connect Error: {e}")

    def create_tables(self):
        self.connect()
        try:
            cursor = self.conn.cursor()
            
            # 1. Таблица СЕССИЙ
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    title TEXT DEFAULT 'New Chat',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            ''')

            # 2. Таблица СООБЩЕНИЙ
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    role TEXT,
                    content TEXT,
                    model TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions (id)
                )
            ''')

            # 3. Таблица ПОЛЬЗОВАТЕЛЕЙ (Счетчик токенов)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    total_tokens INTEGER DEFAULT 0
                )
            ''')

            self.conn.commit()
            logger.info("✅ Database Structure OK.")
        except Exception as e:
            logger.error(f"❌ DB Create Tables Error: {e}")

    # --- УПРАВЛЕНИЕ ТОКЕНАМИ ---

    def update_tokens(self, user_id, tokens_spent):
        """Прибавляет токены к общему счету юзера"""
        try:
            cursor = self.conn.cursor()
            # Сначала убедимся, что юзер есть в базе
            cursor.execute("INSERT OR IGNORE INTO users (user_id, total_tokens) VALUES (?, 0)", (user_id,))
            # Обновляем счетчик
            cursor.execute("UPDATE users SET total_tokens = total_tokens + ? WHERE user_id = ?", (tokens_spent, user_id))
            self.conn.commit()
        except Exception as e:
            logger.error(f"DB Token Update Error: {e}")

    def get_total_tokens(self, user_id):
        """Возвращает сколько всего потрачено"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT total_tokens FROM users WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            return row['total_tokens'] if row else 0
        except Exception:
            return 0

    # --- УПРАВЛЕНИЕ СЕССИЯМИ ---

    def create_session(self, user_id, title="Новый диалог"):
        try:
            cursor = self.conn.cursor()
            cursor.execute("UPDATE sessions SET is_active = 0 WHERE user_id = ?", (user_id,))
            cursor.execute("INSERT INTO sessions (user_id, title) VALUES (?, ?)", (user_id, title))
            self.conn.commit()
            return cursor.lastrowid
        except Exception as e:
            logger.error(f"DB Create Session Error: {e}")
            return None

    def activate_session(self, user_id, session_id):
        try:
            cursor = self.conn.cursor()
            cursor.execute("UPDATE sessions SET is_active = 0 WHERE user_id = ?", (user_id,))
            cursor.execute("UPDATE sessions SET is_active = 1 WHERE id = ? AND user_id = ?", (session_id, user_id))
            self.conn.commit()
            return True
        except Exception:
            return False

    def get_active_session(self, user_id):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id FROM sessions WHERE user_id = ? AND is_active = 1 ORDER BY id DESC LIMIT 1", (user_id,))
            row = cursor.fetchone()
            if row: return row['id']
            else: return self.create_session(user_id)
        except Exception:
            return None

    def update_session_title(self, session_id, text):
        try:
            short_title = text[:30] + "..." if len(text) > 30 else text
            cursor = self.conn.cursor()
            cursor.execute("UPDATE sessions SET title = ? WHERE id = ?", (short_title, session_id))
            self.conn.commit()
        except Exception:
            pass

    def get_session_title(self, session_id):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT title FROM sessions WHERE id = ?", (session_id,))
            row = cursor.fetchone()
            return row['title'] if row else "Чат"
        except Exception:
            return "Чат"

    def get_user_sessions(self, user_id, limit=10):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id, title, created_at FROM sessions WHERE user_id = ? ORDER BY id DESC LIMIT ?", (user_id, limit))
            return cursor.fetchall()
        except Exception:
            return []

    # ... (Весь код тот же, добавляем этот метод в класс Database) ...

    def delete_session(self, user_id, session_id):
        """Удаляет сессию и все сообщения в ней"""
        try:
            cursor = self.conn.cursor()
            # 1. Удаляем сообщения этой сессии
            cursor.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
            # 2. Удаляем саму сессию (только если она принадлежит этому юзеру)
            cursor.execute("DELETE FROM sessions WHERE id = ? AND user_id = ?", (session_id, user_id))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"DB Delete Session Error: {e}")
            return False

    # --- УПРАВЛЕНИЕ СООБЩЕНИЯМИ ---

    def add_message(self, session_id, role, content, model=""):
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO messages (session_id, role, content, model) VALUES (?, ?, ?, ?)",
                (session_id, role, content, model)
            )
            self.conn.commit()
        except Exception as e:
            logger.error(f"DB Add Message Error: {e}")

    def get_history(self, session_id, limit=20):
        try:
            cursor = self.conn.cursor()
            query = f"SELECT role, content FROM (SELECT role, content, id FROM messages WHERE session_id = ? ORDER BY id DESC LIMIT ?) ORDER BY id ASC"
            cursor.execute(query, (session_id, limit))
            rows = cursor.fetchall()
            return [{"role": row['role'], "content": row['content']} for row in rows]
        except Exception:
            return []
