import logging
import json
import config
from curl_cffi.requests import AsyncSession 

logger = logging.getLogger(__name__)

class AudioStudio:
    def __init__(self):
        self.api_key = config.ELEVENLABS_API_KEY
        self.base_url = "https://api.elevenlabs.io/v1"
        
        # Обновленные заголовки: притворяемся, что мы на сайте
        self.headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
            "Origin": "https://elevenlabs.io",
            "Referer": "https://elevenlabs.io/"
        }
        
        if not self.api_key:
            logger.warning("⚠️ ElevenLabs API Key не найден. Аудио-студия недоступна.")
    
    async def text_to_speech(self, text, voice_id):
        """Превращает текст в голосовое сообщение (MP3) с усиленной маскировкой"""
        if not self.api_key: return None
        
        url = f"{self.base_url}/text-to-speech/{voice_id}?output_format=mp3_44100_128"
        
        payload = {
            "text": text,
            "model_id": "eleven_multilingual_v2", 
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }
        
        try:
            # ИСПОЛЬЗУЕМ CHROME 124 (Самый свежий и надежный отпечаток)
            async with AsyncSession(impersonate="chrome124") as session:
                resp = await session.post(url, json=payload, headers=self.headers)
                
                if resp.status_code == 200:
                    content_bytes = resp.content
                    
                    # --- ПРОВЕРКИ ---
                    # 1. JSON-ошибка от API
                    if content_bytes.strip().startswith(b"{"):
                        try:
                            error_json = resp.json()
                            logger.error(f"TTS Logic Error: {error_json}")
                        except:
                            logger.error(f"TTS Logic Error: {content_bytes[:100]}")
                        return None
                        
                    # 2. HTML-капча от Cloudflare
                    if content_bytes.strip().startswith(b"<"):
                        logger.error("TTS Error: Cloudflare sent HTML CAPTCHA. IP Reputation issue.")
                        return None
                    
                    # 3. Размер
                    if len(content_bytes) < 100:
                        logger.error(f"TTS Error: File too small ({len(content_bytes)} bytes)")
                        return None

                    logger.info(f"✅ TTS Success: Valid Audio received ({len(content_bytes)} bytes)")
                    return content_bytes
                
                else:
                    logger.error(f"TTS HTTP Error {resp.status_code}: {resp.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Audio Studio Connection Error: {e}")
            return None

    async def generate_sfx(self, description, duration_seconds=None):
        """Генерация звуковых эффектов (SFX)"""
        if not self.api_key: return None
        
        url = f"{self.base_url}/sound-generation"
        payload = {
            "text": description, 
            "duration_seconds": duration_seconds,
            "prompt_influence": 0.3
        }
        
        try:
            async with AsyncSession(impersonate="chrome124") as session:
                resp = await session.post(url, json=payload, headers=self.headers)
                
                if resp.status_code == 200:
                    if resp.content.startswith(b"{") or resp.content.startswith(b"<"):
                         logger.error("SFX Error: Not an audio file")
                         return None
                    return resp.content
                else:
                    logger.error(f"SFX Error {resp.status_code}: {resp.text}")
                    return None
        except Exception as e:
            logger.error(f"SFX Exception: {e}")
            return None

# Создаем синглтон
audio_studio = AudioStudio()
