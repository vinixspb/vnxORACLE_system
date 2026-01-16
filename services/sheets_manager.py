import logging
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import config

logger = logging.getLogger(__name__)

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
        try:
            if config.GOOGLE_CREDENTIALS_JSON:
                creds_dict = json.loads(config.GOOGLE_CREDENTIALS_JSON)
                creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPES)
            else:
                creds = ServiceAccountCredentials.from_json_keyfile_name("keys.json", SCOPES)

            self.client = gspread.authorize(creds)
            logger.info("✅ ORACLE: Google Sheets Connected")
            
        except Exception as e:
            logger.error(f"❌ ORACLE Auth Error: {e}")

    def check_ai_access(self, tg_id):
        """
        Проверяет подписку.
        Логика: Ищем по всей таблице. Если есть ХОТЯ БЫ ОДНА строка
        с этим telegram_id и статусом Active — даем доступ.
        """
        if not self.client: 
            self._authenticate()
            if not self.client: return False

        try:
            sheet = self.client.open_by_key(self.sheet_id)
            worksheet = sheet.worksheet("Clients")
            records = worksheet.get_all_records()
            
            target_id = str(tg_id).strip()
            
            # Проходим по всем записям
            for row in records:
                # Получаем ID из строки (название столбца как в твоей таблице)
                row_tg_id = str(row.get('telegram_id', '')).strip()
                
                # Если ID совпал
                if row_tg_id == target_id:
                    # Проверяем статус
                    ai_status = str(row.get('AI_Access', '')).strip()
                    
                    # Если нашли Active — СРАЗУ возвращаем True (Ура, доступ есть!)
                    # Мы не смотрим остальные строки, одного Active достаточно.
                    if ai_status == 'Active':
                        return True
            
            # Если цикл закончился, а True мы так и не вернули — значит, активных подписок нет.
            return False

        except Exception as e:
            logger.error(f"❌ Check Access Error: {e}")
            return False
