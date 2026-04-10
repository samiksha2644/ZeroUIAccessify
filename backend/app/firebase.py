import firebase_admin
from firebase_admin import credentials, firestore, db
from app.config import Config
import logging

logger = logging.getLogger(__name__)

# Singleton wrapper for Firebase apps
_firebase_initialized = False

def initialize_firebase():
    global _firebase_initialized
    if not _firebase_initialized:
        try:
            cred = credentials.Certificate(Config.FIREBASE_SERVICE_ACCOUNT_PATH)
            firebase_admin.initialize_app(cred, {
                'databaseURL': Config.FIREBASE_REALTIME_DB_URL
            })
            _firebase_initialized = True
            logger.info("Firebase Admin SDK initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {e}")
            raise e

def get_firestore():
    initialize_firebase()
    return firestore.client()

def get_realtime_db():
    initialize_firebase()
    return db.reference()
