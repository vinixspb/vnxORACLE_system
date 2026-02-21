import logging
import asyncio
import os
import html

logger = logging.getLogger(__name__)

class OpenClawManager:
    def __init__(self):
        self.is_installed = True

    async def check_status(self):
        try:
            process = await asyncio.create_subprocess_shell(
                "pgrep -f 'openclaw'",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await process.communicate()
            if stdout.decode().strip():
                return "✅ <b>OpenClaw ONLINE</b> (Порт: 18789)\n🦞 Агент готов к автономной работе."
            else:
                return "💤 <b>OpenClaw OFFLINE</b>\nПроцесс не запущен."
        except Exception as e:
            logger.error(f"OpenClaw Status Error: {e}")
            return "⚠️ Ошибка связи с ядром."

    async def execute_task(self, task_description: str, user_id: int):
        """
        Отправляет задачу лобстеру.
        user_id используется как session-id для изоляции задач.
        """
        logger.info(f"🦞 Запуск агента для {user_id}: {task_description}")
        
        try:
            safe_task = task_description.replace('"', '\\"')
            env = os.environ.copy()
            env["PATH"] = "/usr/local/bin:/usr/bin:/bin:/opt/node/bin:" + env.get("PATH", "")
            
            # Добавляем --session-id, чтобы лобстер не ругался на отсутствие сессии
            cmd = f'openclaw agent --message "{safe_task}" --session-id "tg_{user_id}"'
            
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env
            )
            
            stdout, stderr = await process.communicate()
            output = stdout.decode().strip()
            err = stderr.decode().strip()
            
            # Экранируем спецсимволы < > &, чтобы Telegram не выдавал BadRequest
            final_output = html.escape(output if process.returncode == 0 else (err or output))
            
            if process.returncode != 0:
                return f"⚠️ <b>Сбой Агента:</b>\n<code>{final_output}</code>"
                
            return f"🦞 <b>Отчет Агента:</b>\n\n<code>{final_output}</code>"
            
        except Exception as e:
            logger.error(f"OpenClaw Bridge Error: {e}")
            return f"⚠️ Ошибка моста: {html.escape(str(e))}"

# Глобальный инстанс
claw_manager = OpenClawManager()
