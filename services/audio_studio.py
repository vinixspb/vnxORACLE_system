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
        
        self.voice_map = {
            config.VOICE_ADAM: "onyx",
            config.VOICE_RACHEL: "alloy",
            config.VOICE_FIN: "echo",
            config.VOICE_MIMI: "shimmer"
        }

    def _get_eleven_headers(self):
        return {
            "xi-api-key": self.eleven_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Origin": "https://elevenlabs.io",
            "Referer": "https://elevenlabs.io/",
            "sec-ch-ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"'
        }

    async def text_to_speech(self, text: str, voice_id: str):
        if not text or not text.strip():
            return None, "System", False

        if self.eleven_key:
            audio = await self._try_elevenlabs(text.strip(), voice_id)
            if audio: 
                return audio, "ElevenLabs", False
            
        logger.warning("🔮 Fallback: ElevenLabs недоступен. Переключаюсь на OpenAI...")
        audio_fallback = await self._try_openai(text.strip(), voice_id)
        
        if audio_fallback:
            return audio_fallback, "OpenAI", True 
            
        return None, "Error", False

    async def _try_elevenlabs(self, text, voice_id):
        url = f"{self.eleven_url}/text-to-speech/{voice_id}?output_format=mp3_44100_128"
        payload = {
            "text": text,
            "model_id": "eleven_multilingual_v2", 
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
        }
        try:
            async with AsyncSession(impersonate="chrome124") as session:
                resp = await session.post(url, json=payload, headers=self._get_eleven_headers(), timeout=45)
                if resp.status_code == 200:
                    content = resp.content
                    if content.startswith(b"<html") or len(content) < 1000:
                        return None
                    return content
                return None
        except Exception as e:
            logger.error(f"ElevenLabs Error: {e}")
            return None

    async def _try_openai(self, text, eleven_voice_id):
        if not self.openai_key: return None
        openai_voice = self.voice_map.get(eleven_voice_id, "alloy")
        headers = {"Authorization": f"Bearer {self.openai_key}"}
        payload = {"model": "tts-1", "input": text, "voice": openai_voice}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.openai_url, json=payload, headers=headers) as resp:
                    if resp.status == 200: return await resp.read()
                    return None
        except Exception: return None

    async def generate_sfx(self, description: str, duration_seconds=None):
        if not self.eleven_key or not description: return None
        url = f"{self.eleven_url}/sound-generation"
        payload = {"text": description, "duration_seconds": duration_seconds, "prompt_influence": 0.3}
        try:
            async with AsyncSession(impersonate="chrome124") as session:
                resp = await session.post(url, json=payload, headers=self._get_eleven_headers(), timeout=60)
                if resp.status_code == 200 and not resp.content.startswith(b"<html"):
                    return resp.content
                return None
        except Exception: return None

# 👇 ВАЖНО: Инициализация синглтона для импорта в loader.py
audio_studio = AudioStudio()
