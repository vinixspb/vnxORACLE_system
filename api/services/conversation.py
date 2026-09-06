import logging
from typing import Dict, List
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class ConversationManager:
    """
    Управление диалогами и сессиями.
    Хранит историю в памяти (для MVP), позже миграция на Redis/PostgreSQL.
    """

    def __init__(self):
        # {session_id: {messages: [], metadata: {}, created_at: ...}}
        self.sessions: Dict[str, dict] = {}

    def create_session(self, session_id: str = None) -> str:
        """Создать новую сессию"""
        if session_id is None:
            session_id = str(uuid.uuid4())

        self.sessions[session_id] = {
            "messages": [],
            "metadata": {},
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }

        logger.info(f"✅ Session created: {session_id}")
        return session_id

    def get_session(self, session_id: str) -> dict:
        """Получить сессию"""
        if session_id not in self.sessions:
            self.create_session(session_id)
        return self.sessions[session_id]

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str
    ):
        """Добавить сообщение в историю"""
        session = self.get_session(session_id)

        session["messages"].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })

        session["updated_at"] = datetime.now()

        # Лимит истории: последние 20 сообщений
        if len(session["messages"]) > 20:
            session["messages"] = session["messages"][-20:]

    def get_messages(self, session_id: str) -> List[dict]:
        """Получить историю сообщений для LLM (без timestamp)"""
        session = self.get_session(session_id)
        return [
            {"role": msg["role"], "content": msg["content"]}
            for msg in session["messages"]
        ]

    def get_full_history(self, session_id: str) -> List[dict]:
        """Получить полную историю с timestamp"""
        session = self.get_session(session_id)
        return session["messages"]

    def set_metadata(
        self,
        session_id: str,
        key: str,
        value: any
    ):
        """Установить метаданные сессии"""
        session = self.get_session(session_id)
        session["metadata"][key] = value

    def get_metadata(
        self,
        session_id: str,
        key: str
    ) -> any:
        """Получить метаданные"""
        session = self.get_session(session_id)
        return session["metadata"].get(key)

    def should_capture_contact(self, session_id: str) -> bool:
        """
        Проверить, нужно ли запросить контакт.
        Логика: после 2-3 осмысленных сообщений.
        """
        session = self.get_session(session_id)

        # Если контакт уже захвачен
        if session["metadata"].get("contact_captured"):
            return False

        # Подсчитываем user messages
        user_messages = [
            msg for msg in session["messages"]
            if msg["role"] == "user"
        ]

        # Запрашиваем после 2-3 сообщений
        return len(user_messages) >= 2

    def mark_contact_captured(self, session_id: str):
        """Отметить, что контакт захвачен"""
        self.set_metadata(session_id, "contact_captured", True)

    def clear_old_sessions(self, hours: int = 24):
        """Удалить старые сессии (для экономии памяти)"""
        now = datetime.now()
        to_delete = []

        for sid, session in self.sessions.items():
            age = (now - session["updated_at"]).total_seconds() / 3600
            if age > hours:
                to_delete.append(sid)

        for sid in to_delete:
            del self.sessions[sid]

        if to_delete:
            logger.info(f"🧹 Cleaned {len(to_delete)} old sessions")


# Глобальный экземпляр
conversation_manager = ConversationManager()
