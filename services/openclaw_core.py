import logging
import asyncio
import os

logger = logging.getLogger(__name__)

class OpenClawManager:
    """
    Боевой мост между Telegram-ботом vnxORACLE и агентом OpenClaw.
    """
    def __init__(self):
        self.is_installed = True

    async def check_status(self):
        """Проверяет, жив ли системный процесс лобстера (напрямую в ОЗУ)"""
        try:
            # pgrep ищет процесс по имени, игнорируя барьеры systemd
            process = await asyncio.create_subprocess_shell(
                "pgrep -f 'openclaw'",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await process.communicate()
            
            if stdout.decode().strip():
                return "✅ <b>OpenClaw ONLINE</b> (Порт: 18789)\n🦞 Агент подключен к ядру сервера и ожидает приказов."
            else:
                return "💤 <b>OpenClaw OFFLINE</b>\nПроцесс демона не найден в памяти."
        except Exception as e:
            logger.error(f"OpenClaw Status Error: {e}")
            return "⚠️ Ошибка связи с ядром."

    async def execute_task(self, task_description: str):
        """Отправляет прямую команду лобстеру через терминал"""
        logger.info(f"🦞 Запуск агента: {task_description}")
        
        try:
            safe_task = task_description.replace('"', '\\"')
            
            # ВАЖНО: Добавляем стандартные пути, так как системные демоны часто имеют "урезанный" PATH
            env = os.environ.copy()
            env["PATH"] = "/usr/local/bin:/usr/bin:/bin:/opt/node/bin:" + env.get("PATH", "")
            
            # Вызываем CLI лобстера
            cmd = f'openclaw agent --message "{safe_task}"'
            
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env
            )
            
            stdout, stderr = await process.communicate()
            output = stdout.decode().strip()
            err = stderr.decode().strip()
            
            # Если команда упала
            if process.returncode != 0:
                logger.error(f"OpenClaw Exec Error: {err}")
                return f"⚠️ <b>Сбой выполнения Агента:</b>\n<code>{err or output}</code>"
                
            return f"🦞 <b>Отчет Агента:</b>\n\n<code>{output}</code>"
            
        except Exception as e:
            logger.error(f"OpenClaw Bridge Error: {e}")
            return f"⚠️ Внутренняя ошибка моста: {e}"

# Глобальный инстанс
claw_manager = OpenClawManager()
