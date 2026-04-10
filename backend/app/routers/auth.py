from fastapi import APIRouter, HTTPException
from app.models.schemas import UserRegistration, UserRegistrationResponse, UserProfile
from app.firebase import get_firestore
from google.cloud.firestore import firestore
import uuid

router = APIRouter()

@router.post("/register", response_model=UserRegistrationResponse)
async def register_user(user: UserRegistration):
    """
    Creates a USERS doc in Firestore with name, phone, language, home_lat, home_lng.
    Initializes wallet_balance to 0. Returns user_id.
    """
    db = get_firestore()
    user_id = str(uuid.uuid4())
    
    doc_ref = db.collection("USERS").document(user_id)
    
    try:
        doc_ref.set({
            "name": user.name,
            "phone": user.phone,
            "language": user.language,
            "home_lat": user.home_lat,
            "home_lng": user.home_lng,
            "wallet_balance": 0.0,
            "created_at": firestore.SERVER_TIMESTAMP
        })
        return {"user_id": user_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user/{user_id}", response_model=UserProfile)
async def get_user(user_id: str):
    """
    Fetch user profile by user_id.
    """
    db = get_firestore()
    doc_ref = db.collection("USERS").document(user_id)
    doc = doc_ref.get()
    
    if not doc.exists:
        raise HTTPException(status_code=404, detail="User not found")
        
    data = doc.to_dict()
    return {
        "user_id": user_id,
        "name": data.get("name", ""),
        "phone": data.get("phone", ""),
        "language": data.get("language", "en"),
        "wallet_balance": data.get("wallet_balance", 0.0),
        "home_lat": data.get("home_lat"),
        "home_lng": data.get("home_lng")
    }
