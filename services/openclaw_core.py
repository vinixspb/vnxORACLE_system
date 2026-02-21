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
        # Формируем контекст безопасности
        if not is_admin:
            instruction = (
                f"SYSTEM RULES for {user_display_name}: You are a Cloud Assistant with restricted access. "
                # ПРАВИЛА ФАЙЛОВОЙ СИСТЕМЫ (ЖЕСТКИЕ)
                "FILE SYSTEM PROTOCOL: "
                "1. You have READ-ONLY access to the server. DO NOT modify existing files. "
                "2. CRITICAL EXCEPTION: If a task REQUIRES creating a script or downloading data, "
                "you MUST create temporary files ONLY in the `/tmp/` directory. "
                "3. MANDATORY CLEANUP: You MUST include a command to DELETE any temporary files immediately after executing them. "
                "Example: `python3 /tmp/script.py && rm /tmp/script.py`. "
                "Leaving files on the server is a security violation. "
                # РАЗРЕШЕНИЯ НА СЕТЬ
                "NETWORK PROTOCOL: You are allowed to use internet resources (curl, public APIs) to fetch data for the user. "
                f"USER REQUEST: {task_description}"
            )
        else:
            # Для тебя — полная свобода действий
            instruction = f"ADMIN COMMAND from {user_display_name}: {task_description}"

        try:
            # Подготовка окружения (пути к Node.js и OpenClaw)
            env = os.environ.copy()
            env["PATH"] = "/usr/local/bin:/usr/bin:/bin:/opt/node/bin:" + env.get("PATH", "")
            
            # 💉 ВПРЫСКИВАЕМ КЛЮЧИ НАПРЯМУЮ ИЗ КОНФИГА:
            env["OPENROUTER_API_KEY"] = config.KEY_NEO
            
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
