import logging
import aiohttp
import json
import config

logger = logging.getLogger(__name__)

class AudioStudio:
    def __init__(self):
        self.api_key = config.ELEVENLABS_API_KEY
        self.base_url = "https://api.elevenlabs.io/v1"
        
        # Обновленные заголовки для обхода блокировок
        self.headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "audio/mpeg"
        }
        
        if not self.api_key:
            logger.warning("⚠️ ElevenLabs API Key не найден. Аудио-студия недоступна.")
    
    async def text_to_speech(self, text, voice_id=config.DEFAULT_VOICE):
        """Превращает текст в голосовое сообщение (MP3)"""
        if not self.api_key: return None
        
        url = f"{self.base_url}/text-to-speech/{voice_id}"
        
        # Добавляем output_format, чтобы снизить задержку
        query_params = "?output_format=mp3_44100_128"
        full_url = url + query_params
        
        payload = {
            "text": text,
            "model_id": "eleven_multilingual_v2", 
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(full_url, json=payload, headers=self.headers) as resp:
                    if resp.status == 200:
                        logger.info("✅ TTS Success: Audio received")
                        return await resp.read()
                    else:
                        error_text = await resp.text()
                        # Логируем ошибку, но сокращаем HTML если это Cloudflare
                        if "<!DOCTYPE html>" in error_text:
                            logger.error(f"TTS Error {resp.status}: Cloudflare Blocked Request (Check Server IP/User-Agent)")
                        else:
                            logger.error(f"TTS Error {resp.status}: {error_text}")
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
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=self.headers) as resp:
                    if resp.status == 200:
                        return await resp.read()
                    else:
                        logger.error(f"SFX Error {resp.status}: {await resp.text()}")
                        return None
        except Exception as e:
            logger.error(f"SFX Exception: {e}")
            return None

# Создаем синглтон
audio_studio = AudioStudio()
