import logging
import asyncio
import os
import html
import datetime
import config  # Используем глобальные настройки

logger = logging.getLogger(__name__)

class OpenClawManager:
    def __init__(self):
        self.admin_id = config.ADMIN_ID

    async def check_status(self):
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
        is_admin = (user_id == self.admin_id)
        current_year = datetime.datetime.now().year
        
        # ✈️ БАЗОВЫЕ ПРАВИЛА (Для всех) - ДОБАВЛЕНА ПАРТНЕРКА ЯНДЕКСА
        base_rules = (
            f"CURRENT YEAR: {current_year}. "
            "FLIGHT SEARCH PROTOCOL (CRITICAL): If the user asks for flights or tickets, DO NOT use Brave Search. "
            "You MUST use `curl` to query FlightAPI.io using the environment variable $FLIGHT_API_KEY. "
            "IATA RULE: ALWAYS convert city names to standard 3-letter IATA codes (e.g., Saint Petersburg to LED) BEFORE making the curl request. "
            "Format for roundtrip: `curl -s \"https://api.flightapi.io/roundtrip/$FLIGHT_API_KEY/{dep_iata}/{arr_iata}/{dep_date_YYYY-MM-DD}/{return_date_YYYY-MM-DD}/1/0/0/Economy/RUB\"`. "
            "ANTI-HALLUCINATION RULE: If the API returns an error, HTML instead of JSON, or an empty result, DO NOT invent flights. Reply exactly: '❌ Ошибка API: Актуальные рейсы не найдены или сервис недоступен'. "
            "DATA EXTRACTION: Extract real data from the JSON: Airlines, exact times, durations, and specific prices. "
            "URL GENERATION: You MUST generate 2 clickable booking links at the very end of the report: "
            "1. Aviasales: `https://www.aviasales.ru/search/{DEP_IATA}{DDMM}{ARR_IATA}{DDMM}1`. "
            "2. Яндекс Путешествия: `https://travel.yandex.ru/avia/search/result/?fromId={DEP_IATA}&toId={ARR_IATA}&when={DEP_YYYY-MM-DD}&return_date={RET_YYYY-MM-DD}&clid=$YANDEX_CLID`. "
            "Format the final output as a clean, structured list in Russian."
        )
        
        if not is_admin:
            instruction = (
                f"SYSTEM RULES for {user_display_name}. {base_rules} "
                "GENERAL SEARCH: For non-flight queries, use your built-in web search tool (Brave). "
                "FILE SYSTEM: You have READ-ONLY access to the server. "
                f"USER REQUEST: {task_description}"
            )
        else:
            instruction = (
                f"ADMIN COMMAND from {user_display_name}. {base_rules} "
                f"REQUEST: {task_description}"
            )

        try:
            # Подготовка окружения
            env = os.environ.copy()
            env["PATH"] = "/usr/local/bin:/usr/bin:/bin:/opt/node/bin:" + env.get("PATH", "")
            
            # ⚡️ СУПЕР-СКОРОСТЬ (Оптимизация запуска Node.js)
            env["NODE_COMPILE_CACHE"] = "/var/tmp/openclaw-compile-cache"
            env["OPENCLAW_NO_RESPAWN"] = "1"
            
            # 💉 ВПРЫСКИВАЕМ КЛЮЧИ:
            env["OPENROUTER_API_KEY"] = config.KEY_NEO
            
            if brave_key:
                env["BRAVE_API_KEY"] = brave_key
                
            if hasattr(config, 'FLIGHT_API_KEY') and config.FLIGHT_API_KEY:
                env["FLIGHT_API_KEY"] = config.FLIGHT_API_KEY
            else:
                env["FLIGHT_API_KEY"] = ""
                
            # Впрыскиваем партнерский ключ Яндекса
            if hasattr(config, 'YANDEX_CLID') and config.YANDEX_CLID:
                env["YANDEX_CLID"] = config.YANDEX_CLID
            else:
                env["YANDEX_CLID"] = "default" # Если ключ не прописан
            
            safe_task = instruction.replace('"', '\\"')
            cmd = f'openclaw agent --message "{safe_task}" --session-id "tg_{user_id}"'
            
            process = await asyncio.create_subprocess_shell(
                cmd, 
                stdout=asyncio.subprocess.PIPE, 
                stderr=asyncio.subprocess.PIPE, 
                env=env
            )
            
            stdout, stderr = await process.communicate()
            raw_result = stdout.decode().strip() or stderr.decode().strip()
            
            if not raw_result:
                return "🦞 <b>Агент:</b> Задача выполнена в фоновом режиме."

            safe_output = html.escape(raw_result)
            return f"🦞 <b>Отчет Агента:</b>\n\n{safe_output}"
            
        except Exception as e:
            logger.error(f"Execution error: {e}")
            return f"⚠️ <b>Критическая ошибка моста:</b>\n<code>{html.escape(str(e))}</code>"

claw_manager = OpenClawManager()
