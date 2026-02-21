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

    async def execute_task(self, task_description: str, user_id: int, user_display_name: str = "User"):
        """
        Выполнение задачи. 
        Для Админа — полный доступ. 
        Для Юзера — режим Read-Only.
        """
        is_admin = (user_id == self.admin_id)
        
        # Формируем контекст безопасности
        if not is_admin:
            # Жесткая системная установка для обычных пользователей
            instruction = (
                f"SYSTEM RULES for user {user_display_name}: You are in READ-ONLY mode. "
                "You can only: list files, read content of files, check system status, answer questions. "
                "STRICTLY FORBIDDEN: create, delete, edit files, install packages, change settings. "
                "If user asks for forbidden action, politely explain your security limitations. "
                f"USER REQUEST: {task_description}"
            )
        else:
            # Для тебя — полная свобода действий
            instruction = f"ADMIN COMMAND from {user_display_name}: {task_description}"

        try:
            # Подготовка окружения (пути к Node.js и OpenClaw)
            env = os.environ.copy()
            env["PATH"] = "/usr/local/bin:/usr/bin:/bin:/opt/node/bin:" + env.get("PATH", "")
            
            # Экранируем только кавычки для bash-команды
            safe_task = instruction.replace('"', '\\"')
            
            # Запуск агента с уникальной сессией для каждого юзера
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
