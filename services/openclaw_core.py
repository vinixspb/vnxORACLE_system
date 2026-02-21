import logging
import asyncio
import subprocess

logger = logging.getLogger(__name__)

class OpenClawManager:
    """
    Боевой мост между Telegram-ботом vnxORACLE и агентом OpenClaw.
    """
    def __init__(self):
        self.is_installed = True

    async def check_status(self):
        """Проверяет, жив ли системный процесс лобстера"""
        try:
            process = await asyncio.create_subprocess_shell(
                "systemctl --user is-active openclaw-gateway.service",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await process.communicate()
            status = stdout.decode().strip()
            
            if status == "active":
                return "✅ <b>OpenClaw ONLINE</b> (Порт: 18789)\n🦞 Агент подключен к ядру сервера и ожидает приказов."
            else:
                return f"💤 <b>OpenClaw OFFLINE</b> ({status})\nСлужба остановлена."
        except Exception as e:
            logger.error(f"OpenClaw Status Error: {e}")
            return "⚠️ Ошибка связи с системной шиной."

    async def execute_task(self, task_description: str):
        """Отправляет прямую команду лобстеру через терминал"""
        logger.info(f"🦞 Запуск агента: {task_description}")
        
        try:
            # Безопасно экранируем кавычки, чтобы не сломать bash
            safe_task = task_description.replace('"', '\\"')
            
            # Команда: openclaw agent --message "Сделай то-то"
            cmd = f'openclaw agent --message "{safe_task}"'
            
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Ждем выполнения (агент может думать и писать код несколько секунд)
            stdout, stderr = await process.communicate()
            
            output = stdout.decode().strip()
            err = stderr.decode().strip()
            
            # Если команда упала (например, шлюз недоступен)
            if process.returncode != 0:
                logger.error(f"OpenClaw Exec Error: {err}")
                return f"⚠️ <b>Сбой выполнения Агента:</b>\n<code>{err or output}</code>"
                
            # Если всё ок, возвращаем ответ лобстера в Telegram
            return f"🦞 <b>Отчет Агента:</b>\n\n<code>{output}</code>"
            
        except Exception as e:
            logger.error(f"OpenClaw Bridge Error: {e}")
            return f"⚠️ Внутренняя ошибка моста: {e}"

# Глобальный инстанс
claw_manager = OpenClawManager()
