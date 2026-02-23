import logging
import asyncio
import os
import html
import config  # Используем глобальные настройки
import datetime

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

    async def execute_task(self, task_description: str, user_id: int, user_display_name: str = "User", brave_key: str = None):
        """
        Выполнение задачи. 
        Для Админа — полный доступ. 
        Для Юзера — режим Read-Only.
        """
        is_admin = (user_id == self.admin_id)
        current_year = datetime.datetime.now().year
        
        # 🧠 Формируем контекст безопасности и правила анти-SEO
        if not is_admin:
            instruction = (
                f"SYSTEM RULES for {user_display_name}. CURRENT YEAR: {current_year}. "
                "1. SEARCH PROTOCOL (CRITICAL): Use your built-in web search tool (Brave). DO NOT write Python or Bash scripts for regular searches. Answer in Russian. "
                "2. DATA EXTRACTION: When searching for flights, hotels, or products, DO NOT quote generic SEO texts or 'from X prices' from aggregators like Aviasales or UniTicket. "
                "You MUST dig deeper and extract structured data: exact Airline names, exact flight times, flight durations, and specific prices. Format the output clearly as a list. "
                "3. FILE SYSTEM PROTOCOL: You have READ-ONLY access to the server. "
                "4. SERVER TASKS: If explicitly asked to write a script for server administration, use `/tmp/` and delete it immediately. "
                f"USER REQUEST: {task_description}"
            )
        else:
            instruction = f"ADMIN COMMAND from {user_display_name}. CURRENT YEAR: {current_year}. REQUEST: {task_description}"

        try:
            # Подготовка окружения
            env = os.environ.copy()
            env["PATH"] = "/usr/local/bin:/usr/bin:/bin:/opt/node/bin:" + env.get("PATH", "")
            
            # 💉 ВПРЫСКИВАЕМ КЛЮЧИ НАПРЯМУЮ ИЗ КОНФИГА:
            env["OPENROUTER_API_KEY"] = config.KEY_NEO
            
            # Передаем ключ браузера
            if brave_key:
                env["BRAVE_API_KEY"] = brave_key
            
            # Экранируем кавычки
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
            
            # Собираем вывод
            raw_result = stdout.decode().strip() or stderr.decode().strip()
            
            if not raw_result:
                return "🦞 <b>Агент:</b> Задача выполнена в фоновом режиме."

            # Экранируем HTML для безопасности Telegram (чтобы < и > не сломали разметку)
            safe_output = html.escape(raw_result)
            
            # 🛠 УБРАЛИ ТЕГИ <code>, ТЕПЕРЬ ТЕКСТ НЕ КОПИРУЕТСЯ ПО КЛИКУ, А ССЫЛКИ КЛИКАБЕЛЬНЫ
            return f"🦞 <b>Отчет Агента:</b>\n\n{safe_output}"
            
        except Exception as e:
            logger.error(f"Execution error: {e}")
            return f"⚠️ <b>Критическая ошибка моста:</b>\n<code>{html.escape(str(e))}</code>"

# Глобальный инстанс
claw_manager = OpenClawManager()
