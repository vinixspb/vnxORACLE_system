import logging
import json
import config
# 👇 Импортируем "магию" для обхода Cloudflare
from curl_cffi.requests import AsyncSession 

logger = logging.getLogger(__name__)

class AudioStudio:
    def __init__(self):
        self.api_key = config.ELEVENLABS_API_KEY
        self.base_url = "https://api.elevenlabs.io/v1"
        
        self.headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg"
        }
        
        if not self.api_key:
            logger.warning("⚠️ ElevenLabs API Key не найден. Аудио-студия недоступна.")
    
    async def text_to_speech(self, text, voice_id):
        """Превращает текст в голосовое сообщение (MP3) с обходом Cloudflare"""
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
            # 👇 ИСПОЛЬЗУЕМ AsyncSession ИЗ curl_cffi ВМЕСТО aiohttp
            # impersonate="chrome110" заставляет сервер думать, что мы - настоящий браузер
            async with AsyncSession(impersonate="chrome110") as session:
                resp = await session.post(url, json=payload, headers=self.headers)
                
                if resp.status_code == 200:
                    logger.info("✅ TTS Success: Audio received")
                    return resp.content # Возвращаем байты
                else:
                    logger.error(f"TTS Error {resp.status_code}: {resp.text}")
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
            # Тоже используем curl_cffi для надежности
            async with AsyncSession(impersonate="chrome110") as session:
                resp = await session.post(url, json=payload, headers=self.headers)
                
                if resp.status_code == 200:
                    return resp.content
                else:
                    logger.error(f"SFX Error {resp.status_code}: {resp.text}")
                    return None
        except Exception as e:
            logger.error(f"SFX Exception: {e}")
            return None

# Создаем синглтон
audio_studio = AudioStudio()
