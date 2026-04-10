import openai
from app.config import Config

client = openai.AsyncOpenAI(api_key=Config.OPENAI_API_KEY)

async def transcribe(audio_file_path: str) -> str:
    """
    Sends the audio file to OpenAI Whisper API and returns the transcript string.
    """
    with open(audio_file_path, "rb") as audio_file:
        transcript = await client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file
        )
    return transcript.text
