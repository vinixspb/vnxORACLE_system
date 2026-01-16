import logging
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import config

logger = logging.getLogger(__name__)

# Используем стандартные права доступа
SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

class GoogleSheetsManager:
    
    def __init__(self):
        self.client = None
        self.sheet_id = config.GOOGLE_SHEET_ID
        self._authenticate()

    def _authenticate(self):
        """
        Аутентификация. Пытаемся взять JSON из конфига (как в Matrix),
        если нет - ищем файл keys.json.
        """
        try:
            if config.GOOGLE_CREDENTIALS_JSON:
                # Загружаем из переменной окружения (String -> Dict)
                creds_dict = json.loads(config.GOOGLE_CREDENTIALS_JSON)
                creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPES)
            else:
                # Резерв: загружаем из файла
                creds = ServiceAccountCredentials.from_json_keyfile_name("keys.json", SCOPES)

            self.client = gspread.authorize(creds)
            logger.info("✅ ORACLE: Google Sheets Connected")
            
        except Exception as e:
            # Логируем ошибку, но не роняем бота сразу
            logger.error(f"❌ ORACLE Auth Error: {e}")

    # ==========================================================================
    # 1. ЛОГИКА ПРОВЕРКИ ДОСТУПА (READ ONLY)
    # ==========================================================================

    def check_ai_access(self, tg_id):
        """
        Проверяет, есть ли у пользователя статус Active в колонке AI_Access.
        Использует лист 'Clients'.
        """
        if not self.client: 
            self._authenticate()
            if not self.client: return False

        try:
            sheet = self.client.open_by_key(self.sheet_id)
            worksheet = sheet.worksheet("Clients")
            records = worksheet.get_all_records()
            
            target_id = str(tg_id).strip()
            
            for row in reversed(records):
                # !!! ИСПРАВЛЕНИЕ ЗДЕСЬ !!!
                # Используем 'telegram_id', так как так назван столбец C в таблице
                row_tg_id = str(row.get('telegram_id', '')).strip()
                
                if row_tg_id == target_id:
                    ai_status = str(row.get('AI_Access', '')).strip()
                    if ai_status == 'Active':
                        return True
                    else:
                        return False
            
            return False

        except Exception as e:
            logger.error(f"❌ Check Access Error: {e}")
            return False
