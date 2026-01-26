import logging
import aiohttp
import json
import config

logger = logging.getLogger(__name__)

class AudioStudio:
    def __init__(self):
        self.api_key = config.ELEVENLABS_API_KEY
        self.base_url = "https://api.elevenlabs.io/v1"
        
        if not self.api_key:
            logger.warning("⚠️ ElevenLabs API Key не найден. Аудио-студия недоступна.")
    
    async def text_to_speech(self, text, voice_id=config.DEFAULT_VOICE):
        """Превращает текст в голосовое сообщение (MP3)"""
        if not self.api_key: return None
        
        url = f"{self.base_url}/text-to-speech/{voice_id}"
        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "text": text,
            "model_id": "eleven_multilingual_v2", # Поддерживает русский язык идеально
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as resp:
                    if resp.status == 200:
                        return await resp.read() # Возвращаем байты аудиофайла
                    else:
                        error_text = await resp.text()
                        logger.error(f"TTS Error {resp.status}: {error_text}")
                        return None
        except Exception as e:
            logger.error(f"Audio Studio Connection Error: {e}")
            return None

    async def generate_sfx(self, description, duration_seconds=None):
        """Генерация звуковых эффектов (SFX)"""
        if not self.api_key: return None
        
        url = f"{self.base_url}/sound-generation"
        headers = {"xi-api-key": self.api_key, "Content-Type": "application/json"}
        payload = {
            "text": description, # Описание звука (напр. "Laser blast in space")
            "duration_seconds": duration_seconds,
            "prompt_influence": 0.3
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as resp:
                    if resp.status == 200:
                        return await resp.read()
                    else:
                        logger.error(f"SFX Error: {await resp.text()}")
                        return None
        except Exception as e:
            logger.error(f"SFX Exception: {e}")
            return None

# Создаем синглтон (как sheets_mgr)
audio_studio = AudioStudio()
