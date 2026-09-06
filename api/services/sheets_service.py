import logging
from datetime import datetime
from typing import Optional
import os.path
from google.oauth2 import service_account
from googleapiclient.discovery import build
import config
import aiohttp

logger = logging.getLogger(__name__)

class SheetsService:
    """Сервис для работы с Google Sheets CRM"""

    def __init__(self):
        self.service = None
        self.spreadsheet_id = config.SPREADSHEET_ID

        if config.GOOGLE_CREDENTIALS_JSON and os.path.exists(config.GOOGLE_CREDENTIALS_JSON):
            try:
                creds = service_account.Credentials.from_service_account_file(
                    config.GOOGLE_CREDENTIALS_JSON,
                    scopes=['https://www.googleapis.com/auth/spreadsheets']
                )
                self.service = build('sheets', 'v4', credentials=creds)
                logger.info("✅ Google Sheets connected")
            except Exception as e:
                logger.error(f"❌ Google Sheets init failed: {e}")
        else:
            logger.warning("⚠️ Google Sheets credentials not found")

    async def save_lead(
        self,
        name: str,
        contact: str,
        company: str = "",
        problem: str = "",
        messages: list = None,
        session_id: str = ""
    ) -> Optional[str]:
        """
        Сохранить лида в Google Sheets.

        Returns:
            Row ID если успешно, None если ошибка
        """
        if not self.service or not self.spreadsheet_id:
            logger.warning("Google Sheets not configured")
            return None

        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            messages_str = " | ".join(messages[:3]) if messages else ""

            values = [[
                timestamp,
                name,
                contact,
                company,
                problem,
                messages_str,
                "NEW",
                "Связаться"
            ]]

            body = {'values': values}

            result = self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range='Sheet1!A:H',
                valueInputOption='RAW',
                body=body
            ).execute()

            updated_range = result.get('updates', {}).get('updatedRange', '')
            logger.info(f"✅ Lead saved to Sheets: {updated_range}")

            # Отправляем уведомление админу в Telegram
            await self._notify_admin(name, contact, company, problem)

            return updated_range

        except Exception as e:
            logger.error(f"❌ Failed to save lead: {e}")
            return None

    async def _notify_admin(
        self,
        name: str,
        contact: str,
        company: str,
        problem: str
    ):
        """Отправить уведомление админу в Telegram"""
        if not config.BOT_TOKEN_ORACLE or not config.ADMIN_ID:
            return

        try:
            text = (
                f"🆕 <b>Новый лид с сайта!</b>\n\n"
                f"👤 <b>Имя:</b> {name}\n"
                f"📱 <b>Контакт:</b> {contact}\n"
                f"🏢 <b>Компания:</b> {company or 'не указана'}\n"
                f"❓ <b>Проблема:</b> {problem[:200] if problem else 'не указана'}\n\n"
                f"💡 <i>Свяжитесь в течение 1 часа для максимальной конверсии!</i>"
            )

            url = f"https://api.telegram.org/bot{config.BOT_TOKEN_ORACLE}/sendMessage"
            payload = {
                "chat_id": config.ADMIN_ID,
                "text": text,
                "parse_mode": "HTML"
            }

            async with aiohttp.ClientSession() as session:
                await session.post(url, json=payload)

            logger.info("✅ Admin notified via Telegram")

        except Exception as e:
            logger.error(f"❌ Failed to notify admin: {e}")


# Глобальный экземпляр
sheets_service = SheetsService()
