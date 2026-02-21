import logging
import asyncio
import os
import html
import config # Импортируем конфиг, чтобы знать ID админа

logger = logging.getLogger(__name__)

class OpenClawManager:
    def __init__(self):
        # Укажи здесь свой Telegram ID (или возьми из config.ADMIN_ID)
        self.admin_id = 262147628 # Твой ID из логов

    async def check_status(self):
        try:
            process = await asyncio.create_subprocess_shell("pgrep -f 'openclaw'", stdout=asyncio.subprocess.PIPE)
            stdout, _ = await process.communicate()
            if stdout.decode().strip():
                return "✅ <b>OpenClaw ONLINE</b>\n🦞 Агент готов к работе."
            return "💤 <b>OpenClaw OFFLINE</b>"
        except: return "⚠️ Ошибка связи."

    async def execute_task(self, task_description: str, user_id: int):
        is_admin = (user_id == self.admin_id)
        
        # Если не админ — жестко ограничиваем промпт
        if not is_admin:
            instruction = (
                "SYSTEM RULES: You are in READ-ONLY mode. "
                "Forbidden: creating files, deleting, renaming, executing bash scripts that modify the system, installing packages. "
                "Allowed: ONLY reading information, answering questions, analyzing existing logs. "
                "If user asks for forbidden action, say you don't have permissions. "
                f"USER TASK: {task_description}"
            )
        else:
            instruction = task_description

        try:
            safe_task = instruction.replace('"', '\\"')
            env = os.environ.copy()
            env["PATH"] = "/usr/local/bin:/usr/bin:/bin:/opt/node/bin:" + env.get("PATH", "")
            
            # Запускаем агента с изоляцией сессии
            cmd = f'openclaw agent --message "{safe_task}" --session-id "tg_{user_id}"'
            
            process = await asyncio.create_subprocess_shell(
                cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, env=env
            )
            
            stdout, stderr = await process.communicate()
            # Глубокая очистка вывода от HTML-тегов, которые может вернуть AI
            raw_output = stdout.decode().strip() or stderr.decode().strip()
            safe_output = html.escape(raw_output)
                
            return f"🦞 <b>Отчет Агента:</b>\n\n<code>{safe_output}</code>"
            
        except Exception as e:
            return f"⚠️ Ошибка моста: {html.escape(str(e))}"

claw_manager = OpenClawManager()
