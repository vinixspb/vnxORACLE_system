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
        Выполнение задачи с интеграцией внешних API.
        """
        is_admin = (user_id == self.admin_id)
        current_year = datetime.datetime.now().year
        
        # ✈️ БАЗОВЫЕ ПРАВИЛА (Для всех)
        base_rules = (
            f"CURRENT YEAR: {current_year}. "
            "FLIGHT SEARCH PROTOCOL (CRITICAL): If the user asks for flights or tickets, DO NOT use Brave Search. "
            "You MUST use `curl` to query FlightAPI.io using the environment variable $FLIGHT_API_KEY. "
            "Format for roundtrip: `curl -s \"https://api.flightapi.io/roundtrip/$FLIGHT_API_KEY/{dep_iata}/{arr_iata}/{dep_date_YYYY-MM-DD}/{return_date_YYYY-MM-DD}/1/0/0/Economy/RUB\"`. "
            "Format for oneway: `curl -s \"https://api.flightapi.io/onewaytrip/$FLIGHT_API_KEY/{dep_iata}/{arr_iata}/{dep_date_YYYY-MM-DD}/1/0/0/Economy/RUB\"`. "
            "Extract data from the JSON response: exact Airlines, departure/arrival times, durations, and specific prices. "
            "Answer in Russian. Format as a clean, structured list. DO NOT invent prices or quote SEO texts. "
        )
        
        # 🧠 Распределение прав доступа
        if not is_admin:
            instruction = (
                f"SYSTEM RULES for {user_display_name}. {base_rules} "
                "GENERAL SEARCH: For non-flight queries (news, weather), use your built-in web search tool (Brave). "
                "DO NOT write Python/Bash scripts for regular searches. "
                "FILE SYSTEM: You have READ-ONLY access to the server. "
                f"USER REQUEST: {task_description}"
            )
        else:
            # Для Админа полная свобода действий на сервере, но с правилами поиска билетов
            instruction = (
                f"ADMIN COMMAND from {user_display_name}. {base_rules} "
                f"REQUEST: {task_description}"
            )

        try:
            # Подготовка окружения
            env = os.environ.copy()
            env["PATH"] = "/usr/local/bin:/usr/bin:/bin:/opt/node/bin:" + env.get("PATH", "")
            
            # 💉 ВПРЫСКИВАЕМ КЛЮЧИ:
            env["OPENROUTER_API_KEY"] = config.KEY_NEO
            
            if brave_key:
                env["BRAVE_API_KEY"] = brave_key
                
            # Передаем ключ для авиабилетов из config.py
            if hasattr(config, 'FLIGHT_API_KEY') and config.FLIGHT_API_KEY:
                env["FLIGHT_API_KEY"] = config.FLIGHT_API_KEY
            else:
                env["FLIGHT_API_KEY"] = "" # Защита от отсутствия ключа
            
            # Экранируем кавычки для bash
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

            # Экранируем HTML для безопасности Telegram
            safe_output = html.escape(raw_result)
            
            # Возвращаем чистый текст без копирования
            return f"🦞 <b>Отчет Агента:</b>\n\n{safe_output}"
            
        except Exception as e:
            logger.error(f"Execution error: {e}")
            return f"⚠️ <b>Критическая ошибка моста:</b>\n<code>{html.escape(str(e))}</code>"

# Глобальный инстанс
claw_manager = OpenClawManager()
