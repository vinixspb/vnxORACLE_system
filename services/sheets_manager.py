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

    def get_user_tariff(self, tg_id):
        """
        Проверяет подписку и возвращает ТАРИФ (START, PRO, NEO).
        Если подписки нет или она не Active -> возвращает None.
        """
        if not self.client: 
            self._authenticate()
            if not self.client: return None

        try:
            sheet = self.client.open_by_key(self.sheet_id)
            worksheet = sheet.worksheet("Clients")
            records = worksheet.get_all_records()
            
            target_id = str(tg_id).strip()
            
            for row in reversed(records):
                # 1. Ищем по telegram_id
                row_tg_id = str(row.get('telegram_id', '')).strip()
                
                if row_tg_id == target_id:
                    # 2. Проверяем активность (AI_Access)
                    ai_status = str(row.get('AI_Access', '')).strip()
                    
                    if ai_status == 'Active':
                        # 3. Возвращаем тариф (Колонка E - tariff)
                        # Если в ячейке пусто или странное, ставим START по умолчанию
                        tariff = str(row.get('tariff', 'START')).strip().upper()
                        
                        # Если там написано что-то сложное (напр. "Индивидуальный"), 
                        # мапим это в наши тарифы, или возвращаем как есть.
                        # Для простоты считаем, что в таблице будет написано START, PRO или NEO.
                        if tariff not in ['PRO', 'NEO']:
                            tariff = 'START'
                            
                        return tariff
            
            return None # Не найден или не активен

        except Exception as e:
            logger.error(f"❌ Check Tariff Error: {e}")
            return None
