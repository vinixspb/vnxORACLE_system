import logging
import asyncio
import os
import html
import config  # Используем глобальные настройки

logger = logging.getLogger(__name__)

class OpenClawManager:
    def __init__(self):
        # Теперь ID админа берется прямо из config.py
        self.admin_id = config.ADMIN_ID

    async def check_status(self):
        """Проверка активности процесса лобстера"""
        try:
            process = await asyncio.create_subprocess_shell(
                "pgrep -f 'openclaw'", 
                stdout=asyncio.subprocess.PIPE
            )
            stdout, _ = await process.communicate()
            if stdout.decode().strip():
                return "✅ <b>OpenClaw ONLINE</b>\n🦞 Агент синхронизирован с ядром."
            return "💤 <b>OpenClaw OFFLINE</b>\nДемон не найден в системе."
        except Exception as e:
            logger.error(f"Status check error: {e}")
            return "⚠️ Ошибка связи с системной шиной."

    # 👇 ДОБАВИЛИ ПАРАМЕТР brave_key
    async def execute_task(self, task_description: str, user_id: int, user_display_name: str = "User", brave_key: str = None):
        """
        Выполнение задачи. 
        Для Админа — полный доступ. 
        Для Юзера — режим Read-Only.
        """
        is_admin = (user_id == self.admin_id)
        
        # 🧠 Защита от галлюцинаций (даем агенту понимание времени)
        import datetime
        current_year = datetime.datetime.now().year
        
        # Формируем контекст безопасности и правила поведения
        if not is_admin:
            instruction = (
                f"SYSTEM RULES for {user_display_name}. CURRENT YEAR: {current_year}. "
                "1. SEARCH PROTOCOL (CRITICAL): To find information, flights, weather, or news, you MUST use your built-in web search tool (Brave). DO NOT write Python or Bash scripts. DO NOT use curl for web searches. Answer the user directly in Russian. "
                "2. FILE SYSTEM PROTOCOL: You have READ-ONLY access to the server. "
                "3. SERVER TASKS ONLY: If the user explicitly asks to write a script for server administration, use `/tmp/` and delete it immediately after execution. "
                f"USER REQUEST: {task_description}"
            )
        else:
            # Для тебя — полная свобода действий, но с указанием года
            instruction = f"ADMIN COMMAND from {user_display_name}. CURRENT YEAR: {current_year}. REQUEST: {task_description}"

        try:
# ... ДАЛЬШЕ КОД ОСТАЕТСЯ БЕЗ ИЗМЕНЕНИЙ (env = os.environ.copy() и т.д.) ...
            # Подготовка окружения (пути к Node.js и OpenClaw)
            env = os.environ.copy()
            env["PATH"] = "/usr/local/bin:/usr/bin:/bin:/opt/node/bin:" + env.get("PATH", "")
            
            # 💉 ВПРЫСКИВАЕМ КЛЮЧИ НАПРЯМУЮ ИЗ КОНФИГА И ПАРАМЕТРОВ:
            env["OPENROUTER_API_KEY"] = config.KEY_NEO
            
            # 👇 ПЕРЕДАЕМ КЛЮЧ БРАУЗЕРА (ЕСЛИ ЕСТЬ) В ОКРУЖЕНИЕ АГЕНТА
            if brave_key:
                env["BRAVE_API_KEY"] = brave_key
            
            # Экранируем только кавычки для bash-команды
            safe_task = instruction.replace('"', '\\"')
            
            # Запуск агента
            cmd = f'openclaw agent --message "{safe_task}" --session-id "tg_{user_id}"'
            
            process = await asyncio.create_subprocess_shell(
                cmd, 
                stdout=asyncio.subprocess.PIPE, 
                stderr=asyncio.subprocess.PIPE, 
                env=env
            )
            
            stdout, stderr = await process.communicate()
            
            # Собираем вывод и очищаем его для Telegram
            raw_result = stdout.decode().strip() or stderr.decode().strip()
            
            if not raw_result:
                return "🦞 <b>Агент:</b> Задача выполнена в фоновом режиме."

            # Экранируем HTML, чтобы спецсимволы (<, >) не ломали сообщение
            safe_output = html.escape(raw_result)
            
            return f"🦞 <b>Отчет Агента:</b>\n\n<code>{safe_output}</code>"
            
        except Exception as e:
            logger.error(f"Execution error: {e}")
            return f"⚠️ <b>Критическая ошибка моста:</b>\n<code>{html.escape(str(e))}</code>"

# Глобальный инстанс для использования в хендлерах
claw_manager = OpenClawManager()
