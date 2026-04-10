from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from fastapi.responses import Response
from app.services.whisper import transcribe
from app.services.tts import speak
from app.firebase import get_firestore
import tempfile
import os

router = APIRouter()

@router.post("/command")
async def voice_command(
    audio: UploadFile = File(...),
    user_id: str = Form(...)
):
    """
    1. Accept multipart audio file
    2. Whisper -> Text
    3. NLP Routing based on Text
    4. Text -> TTS Audio Stream
    """
    # 1. Save audio temp
    with tempfile.NamedTemporaryFile(delete=False, suffix=".m4a") as tmp_audio:
        tmp_audio.write(await audio.read())
        tmp_path = tmp_audio.name
        
    try:
        # 2. Whisper Transcribe
        transcript = await transcribe(tmp_path)
        transcript_lower = transcript.lower()
        
        response_text = "I did not understand your command."
        
        # 3. Dummy NLP routing
        if "nearest stop" in transcript_lower:
            # Fallback static response for demonstration, normally would hit the stops service 
            # with user's current GPS location which should be passed in Form(...)
            response_text = "The nearest stop is Shivaji Nagar, 200 meters away."
            
        elif "take me to" in transcript_lower:
            destination = transcript_lower.split("take me to")[-1].strip()
            response_text = f"Planning a journey to {destination}. Route 43 will take you there."
            
        elif "top up" in transcript_lower:
            response_text = "Please confirm the amount you want to top up."
            
        elif "my balance" in transcript_lower:
            # Example hit DB if we have user_id
            db = get_firestore()
            user_doc = db.collection("USERS").document(user_id).get()
            if user_doc.exists:
                balance = user_doc.to_dict().get("wallet_balance", 0)
                response_text = f"Your current balance is {balance} rupees."
            else:
                response_text = "I could not find your user record."
                
        elif "end trip" in transcript_lower:
            response_text = "Your trip has ended. 20 rupees have been deducted from your wallet."
            
        else:
            response_text = f"You said: {transcript}. I am still learning other commands."

        # 4. Generate TTS Stream Response
        audio_bytes = await speak(response_text)
        return Response(content=audio_bytes, media_type="audio/mpeg")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        os.unlink(tmp_path)
