import os
import chainlit as cl
from openai import AsyncOpenAI
import httpx

class SpeechHandler:
    def __init__(self):
        self.client = AsyncOpenAI()
        self.elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
        self.elevenlabs_voice_id = os.getenv("ELEVENLABS_VOICE_ID")

    async def speech_to_text(self, audio: cl.Audio):
        audio_file = open(audio.path, "rb")
        transcript = await self.client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file
        )
        return transcript.text

    async def text_to_speech(self, text: str):
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.elevenlabs_voice_id}"
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.elevenlabs_api_key
        }
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5
            }
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data, headers=headers)
            response.raise_for_status()

        audio_content = response.content
        audio = cl.Audio(content=audio_content, name="response.mp3")
        return audio