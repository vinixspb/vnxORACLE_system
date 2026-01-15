import os
from dotenv import load_dotenv

# Загрузка секретов
load_dotenv()

# --- СИСТЕМНЫЕ НАСТРОЙКИ ---
BOT_TOKEN_ORACLE = os.getenv("BOT_TOKEN_ORACLE")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY") 
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID") 
GOOGLE_CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS_JSON")

# --- UI / TEXTS (RUSSIAN CLEAN STYLE) ---
BTN_NEW_DIALOG = "⚡️ НОВЫЙ ДИАЛОГ"
BTN_MY_SESSIONS = "🗂 МОИ СЕССИИ"
BTN_CHANGE_MODEL = "🧠 СМЕНИТЬ МОДЕЛЬ"
BTN_PROFILE = "👤 СТАТУС ПОДПИСКИ"

MSG_WELCOME = (
    "👁 <b>vnxORACLE SYSTEM v1.0</b>\n\n"
    "Приветствую, Искатель.\n"
    "Я — интерфейс чистого знания.\n\n"
    "Доступ открыт через шлюз: @vnx_gateway_bot\n"
    "<i>Ожидание команды...</i>"
)
