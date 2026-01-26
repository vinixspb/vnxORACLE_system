import logging
import json
import config
import aiohttp
from curl_cffi.requests import AsyncSession 

logger = logging.getLogger(__name__)

class AudioStudio:
    def __init__(self):
        self.eleven_key = config.ELEVENLABS_API_KEY
        self.openai_key = config.OPENAI_API_KEY
        
        self.eleven_url = "https://api.elevenlabs.io/v1"
        self.openai_url = "https://api.openai.com/v1/audio/speech"
        
        # Заголовки маскировки для ElevenLabs
        self.headers_eleven = {
            "xi-api-key": self.eleven_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
            "Origin": "https://elevenlabs.io",
            "Referer": "https://elevenlabs.io/"
        }

        # Карта соответствия голосов (ElevenLabs -> OpenAI)
        # Мы подобрали аналоги, максимально близкие по тембру
        self.voice_map = {
            config.VOICE_ADAM: "onyx",    # Мужской глубокий
            config.VOICE_RACHEL: "alloy",  # Женский нейтральный
            config.VOICE_FIN: "echo",     # Мужской энергичный
            config.VOICE_MIMI: "shimmer"  # Высокий/Эмоциональный
        }
        
    async def text_to_speech(self, text, voice_id):
        """
        Пробует ElevenLabs, если Cloudflare блокирует — переключается на OpenAI.
        Возвращает: (байты_аудио, название_движка, is_fallback)
        """
        
        # 1. Попытка через ElevenLabs
        if self.eleven_key:
            audio = await self._try_elevenlabs(text, voice_id)
            if audio: 
                return audio, "ElevenLabs", False
            
        # 2. Если ElevenLabs выдал капчу или ошибку — идем в OpenAI
        logger.warning("⚠️ ElevenLabs Blocked. Switching to OpenAI Fallback...")
        audio_fallback = await self._try_openai(text, voice_id)
        
        if audio_fallback:
            return audio_fallback, "OpenAI", True # True указывает, что это резервный канал
            
        return None, None, False

    async def _try_elevenlabs(self, text, voice_id):
        url = f"{self.eleven_url}/text-to-speech/{voice_id}?output_format=mp3_44100_128"
        payload = {
            "text": text,
            "model_id": "eleven_multilingual_v2", 
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
        }
        
        try:
            # Используем curl_cffi для имитации браузера Chrome 124
            async with AsyncSession(impersonate="chrome124") as session:
                resp = await session.post(url, json=payload, headers=self.headers_eleven)
                if resp.status_code == 200:
                    content = resp.content
                    # Проверка: если Cloudflare подсунул HTML-капчу вместо MP3
                    if content.strip().startswith(b"<") or len(content) < 500:
                        logger.error("ElevenLabs: Cloudflare Captcha or empty response.")
                        return None
                    return content
                return None
        except Exception as e:
            logger.error(f"ElevenLabs Connection Error: {e}")
            return None

    async def _try_openai(self, text, eleven_voice_id):
        """Резервная озвучка через OpenAI"""
        if not self.openai_key: 
            logger.error("OpenAI API Key missing for TTS fallback")
            return None
            
        # Подбираем голос OpenAI на основе выбранного голоса ElevenLabs
        openai_voice = self.voice_map.get(eleven_voice_id, "alloy")
        
        headers = {
            "Authorization": f"Bearer {self.openai_key}", 
            "Content-Type": "application/json"
        }
        payload = {
            "model": "tts-1", 
            "input": text, 
            "voice": openai_voice
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.openai_url, json=payload, headers=headers) as resp:
                    if resp.status == 200:
                        return await resp.read()
                    else:
                        err = await resp.text()
                        logger.error(f"OpenAI TTS Error: {err}")
                        return None
        except Exception as e:
            logger.error(f"OpenAI TTS Critical: {e}")
            return None

    async def generate_sfx(self, description, duration_seconds=None):
        """SFX пока только через ElevenLabs"""
        if not self.eleven_key: return None
        url = f"{self.eleven_url}/sound-generation"
        payload = {
            "text": description, 
            "duration_seconds": duration_seconds, 
            "prompt_influence": 0.3
        }
        try:
            async with AsyncSession(impersonate="chrome124") as session:
                resp = await session.post(url, json=payload, headers=self.headers_eleven)
                if resp.status_code == 200 and not resp.content.startswith(b"<"):
                    return resp.content
                return None
        except Exception:
            return None

# Инициализация синглтона
audio_studio = AudioStudio()
