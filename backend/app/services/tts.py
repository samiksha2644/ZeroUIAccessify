import openai
from app.config import Config
import tempfile
import aiofiles
import httpx

client = openai.AsyncOpenAI(api_key=Config.OPENAI_API_KEY)

async def speak(text: str, language: str = "en") -> bytes:
    """
    Calls OpenAI tts-1 model using the 'nova' voice to generate spoken audio.
    Returns the MP3 bytes.
    Note: 'language' parameter can influence text formulation prior to this, 
    but TTS model automatically speaks in the language of the provided text.
    """
    response = await client.audio.speech.create(
        model="tts-1",
        voice="nova",
        input=text
    )
    
    # Return raw bytes
    return response.read()
