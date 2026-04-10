from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from app.firebase import get_firestore
import logging

from app.routers import auth, stops, journey, trip, wallet, voice

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="TransitVoice API",
    description="Backend for the audio-only public transit assistant app.",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(stops.router, prefix="/stops", tags=["stops"])
api_router.include_router(journey.router, prefix="/journey", tags=["journey"])
api_router.include_router(trip.router, prefix="/trip", tags=["trip"])
api_router.include_router(wallet.router, prefix="/wallet", tags=["wallet"])
api_router.include_router(voice.router, prefix="/voice", tags=["voice"])

app.include_router(api_router)

@app.get("/health", tags=["system"])
async def health_check():
    """
    Pings Firestore to check backend and DB health.
    """
    status = "healthy"
    db_status = "ok"
    try:
        db = get_firestore()
        # Just check if we can query an arbitrary collection limit 1
        db.collection("SYSTEM_CONFIG").limit(1).get()
    except Exception as e:
        logger.error(f"Health check failed to ping DB: {e}")
        db_status = "error"
        status = "degraded"

    return {
        "status": status,
        "db": db_status
    }
