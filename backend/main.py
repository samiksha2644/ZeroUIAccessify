from fastapi import FastAPI
import firebase_admin
from firebase_admin import credentials, firestore
from wallet import router as wallet_router

cred = credentials.Certificate("firebase_credentials.json")
firebase_admin.initialize_app(cred)

app = FastAPI()
app.include_router(wallet_router)

@app.get("/")
def home():
    return {"message": "VoiceRoute Backend Running"}