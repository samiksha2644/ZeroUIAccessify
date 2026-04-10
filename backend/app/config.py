import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
    FIREBASE_SERVICE_ACCOUNT_PATH = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH", "serviceAccountKey.json")
    FIREBASE_REALTIME_DB_URL = os.getenv("FIREBASE_REALTIME_DB_URL")

    # Ensure required keys exist (optional but good for debugging)
    @classmethod
    def validate(cls):
        missing = []
        if not cls.FIREBASE_SERVICE_ACCOUNT_PATH:
            missing.append("FIREBASE_SERVICE_ACCOUNT_PATH")
        if not cls.FIREBASE_REALTIME_DB_URL:
            missing.append("FIREBASE_REALTIME_DB_URL")
        
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

Config.validate()
