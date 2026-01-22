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
        Сканирует ВСЮ таблицу и ищет НАИВЫСШИЙ активный тариф пользователя.
        Приоритет: NEO > PRO > START.
        """
        if not self.client: 
            self._authenticate()
            if not self.client: return None

        try:
            sheet = self.client.open_by_key(self.sheet_id)
            worksheet = sheet.worksheet("Clients")
            records = worksheet.get_all_records()
            
            target_id = str(tg_id).strip()
            
            # Собираем все найденные активные тарифы в список
            found_tariffs = set()
            
            for row in records:
                # 1. Сверяем ID (по столбцу telegram_id)
                row_tg_id = str(row.get('telegram_id', '')).strip()
                
                if row_tg_id == target_id:
                    # 2. Проверяем, активна ли подписка
                    ai_status = str(row.get('AI_Access', '')).strip()
                    
                    if ai_status == 'Active':
                        # 3. Читаем тариф и нормализуем его (в верхний регистр)
                        raw_tariff = str(row.get('tariff', '')).strip().upper()
                        found_tariffs.add(raw_tariff)

            # --- ЛОГИКА ПРИОРИТЕТОВ ---
            
            # Если ничего активного не нашли
            if not found_tariffs:
                return None
            
            # Если нашли, выбираем самый крутой
            if 'NEO' in found_tariffs:
                return 'NEO'
            elif 'PRO' in found_tariffs:
                return 'PRO'
            else:
                # Если написано START, Индивидуальный, VIP, Partner или пусто — считаем за START
                return 'START'

        except Exception as e:
            logger.error(f"❌ Check Tariff Error: {e}")
            return None
