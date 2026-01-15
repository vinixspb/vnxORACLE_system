import logging
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import config

logger = logging.getLogger(__name__)

# Используем те же SCOPES, но для gspread
SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

class GoogleSheetsReader:
    
    def __init__(self):
        self.client = None
        self.sheet_id = config.GOOGLE_SHEET_ID
        self._authenticate()

    def _authenticate(self):
        """
        Аутентификация аналогична vnxMATRIX, но адаптирована под библиотеку gspread
        """
        try:
            # Пытаемся загрузить ключи из переменной окружения (как в Matrix)
            if config.GOOGLE_CREDENTIALS_JSON:
                creds_dict = json.loads(config.GOOGLE_CREDENTIALS_JSON)
                creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPES)
            else:
                # Резервный вариант: файл keys.json
                creds = ServiceAccountCredentials.from_json_keyfile_name("keys.json", SCOPES)

            self.client = gspread.authorize(creds)
            logger.info("✅ ORACLE: Google Sheets Connected")
            
        except Exception as e:
            logger.error(f"❌ ORACLE Auth Error: {e}")

    # ==========================================================================
    # 1. ЛОГИКА ДОСТУПА (Чтение Clients)
    # ==========================================================================

    def check_access(self, tg_id):
        """
        Проверяет, активна ли подписка на AI у пользователя.
        Ищет пользователя по TG ID и проверяет колонку 'AI_Access' (или 'Oracle_Status').
        """
        if not self.client: 
            self._authenticate()
            if not self.client: return False

        try:
            # Открываем таблицу и лист
            sheet = self.client.open_by_key(self.sheet_id)
            worksheet = sheet.worksheet("Clients")
            
            # Получаем все записи (это быстро для чтения)
            # gspread возвращает список словарей, где ключи - заголовки столбцов
            records = worksheet.get_all_records()
            
            target_id = str(tg_id).strip()
            
            # Ищем пользователя (аналог find_client_by_tg_id)
            # Перебираем с конца, чтобы найти актуальный статус
            for row in reversed(records):
                # Проверяем совпадение ID (ключ 'tg_id' должен совпадать с заголовком в таблице!)
                if str(row.get('tg_id', '')).strip() == target_id:
                    
                    # Проверяем колонку доступа к ИИ
                    # ВАЖНО: В таблице должен быть заголовок 'AI_Access'
                    ai_status = row.get('AI_Access', '').strip()
                    
                    if ai_status == 'Active':
                        return True
                    else:
                        # Если нашли пользователя, но статус не Active - доступ закрыт
                        return False
            
            # Если пользователь вообще не найден в таблице
            return False

        except Exception as e:
            logger.error(f"❌ Check Access Error: {e}")
            # При ошибке базы лучше запретить доступ, чтобы не тратить токены
            return False
