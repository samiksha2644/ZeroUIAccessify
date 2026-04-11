"""
Firebase Firestore client helper.

Initializes the Firebase Admin SDK once and exposes thin wrappers
for reading bus stops, routes, and live-bus data from Firestore.
If Firebase credentials are not configured the module falls back to
an in-memory dataset so the backend can still run standalone.
"""

import os
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# In-memory fallback data (mirrors seed_data.py)
# ---------------------------------------------------------------------------
_FALLBACK_STOPS: List[Dict] = [
    {"id": "swargate",         "name": "Swargate",         "lat": 18.5018, "lng": 73.8636, "routes": ["route_156", "route_11"]},
    {"id": "shivajinagar",     "name": "Shivajinagar",     "lat": 18.5308, "lng": 73.8474, "routes": ["route_156"]},
    {"id": "deccan_gymkhana",  "name": "Deccan Gymkhana",  "lat": 18.5156, "lng": 73.8404, "routes": ["route_156"]},
    {"id": "pune_station",     "name": "Pune Station",     "lat": 18.5297, "lng": 73.8743, "routes": ["route_156", "route_50"]},
    {"id": "katraj",           "name": "Katraj",           "lat": 18.4529, "lng": 73.8682, "routes": ["route_11"]},
    {"id": "hadapsar",         "name": "Hadapsar",         "lat": 18.5018, "lng": 73.9252, "routes": ["route_50"]},
    {"id": "kothrud_depot",    "name": "Kothrud Depot",    "lat": 18.5074, "lng": 73.8077, "routes": ["route_11"]},
    {"id": "wakad",            "name": "Wakad",            "lat": 18.5991, "lng": 73.7601, "routes": []},
    {"id": "hinjewadi",        "name": "Hinjewadi",        "lat": 18.5912, "lng": 73.7389, "routes": ["route_50"]},
    {"id": "warje",            "name": "Warje",            "lat": 18.4849, "lng": 73.8007, "routes": ["route_11"]},
]

_FALLBACK_ROUTES: List[Dict] = [
    {
        "id": "route_156",
        "name": "Route 156",
        "stops": ["swargate", "deccan_gymkhana", "shivajinagar", "pune_station"],
        "frequency_minutes": 15,
    },
    {
        "id": "route_11",
        "name": "Route 11",
        "stops": ["katraj", "swargate", "warje", "kothrud_depot"],
        "frequency_minutes": 20,
    },
    {
        "id": "route_50",
        "name": "Route 50",
        "stops": ["pune_station", "hadapsar", "hinjewadi"],
        "frequency_minutes": 25,
    },
]

_FALLBACK_LIVE_BUSES: List[Dict] = [
    {"id": "bus_156_a", "route_id": "route_156", "current_stop_index": 1, "last_updated": "2026-04-11T07:00:00Z"},
    {"id": "bus_11_a",  "route_id": "route_11",  "current_stop_index": 0, "last_updated": "2026-04-11T07:00:00Z"},
    {"id": "bus_50_a",  "route_id": "route_50",  "current_stop_index": 0, "last_updated": "2026-04-11T07:00:00Z"},
]


# ---------------------------------------------------------------------------
# Firebase initialisation
# ---------------------------------------------------------------------------
_db = None  # Firestore client (lazy)
_USE_FIREBASE = False

def _init_firebase() -> None:
    global _db, _USE_FIREBASE
    cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
    if not cred_path or not os.path.isfile(cred_path):
        print("[firebase_client] No valid FIREBASE_CREDENTIALS_PATH found — using in-memory fallback data.")
        return

    try:
        import firebase_admin
        from firebase_admin import credentials, firestore as fs

        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)

        _db = fs.client()
        _USE_FIREBASE = True
        print("[firebase_client] Firestore connected successfully.")
    except Exception as exc:
        print(f"[firebase_client] Firebase init failed ({exc}) — using in-memory fallback.")


_init_firebase()


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

def get_all_stops() -> List[Dict]:
    """Return every document in the bus_stops collection."""
    if _USE_FIREBASE and _db:
        docs = _db.collection("bus_stops").stream()
        return [{"id": d.id, **d.to_dict()} for d in docs]
    return _FALLBACK_STOPS


def get_all_routes() -> List[Dict]:
    if _USE_FIREBASE and _db:
        docs = _db.collection("bus_routes").stream()
        return [{"id": d.id, **d.to_dict()} for d in docs]
    return _FALLBACK_ROUTES


def get_route_by_id(route_id: str) -> Optional[Dict]:
    if _USE_FIREBASE and _db:
        doc = _db.collection("bus_routes").document(route_id).get()
        if doc.exists:
            return {"id": doc.id, **doc.to_dict()}
        return None

    for r in _FALLBACK_ROUTES:
        if r["id"] == route_id:
            return r
    return None


def get_live_buses(route_id: str) -> List[Dict]:
    """Return live bus documents for a given route_id."""
    if _USE_FIREBASE and _db:
        docs = (
            _db.collection("live_buses")
            .where("route_id", "==", route_id)
            .stream()
        )
        return [{"id": d.id, **d.to_dict()} for d in docs]

    return [b for b in _FALLBACK_LIVE_BUSES if b["route_id"] == route_id]


def get_stop_by_id(stop_id: str) -> Optional[Dict]:
    if _USE_FIREBASE and _db:
        doc = _db.collection("bus_stops").document(stop_id).get()
        if doc.exists:
            return {"id": doc.id, **doc.to_dict()}
        return None

    for s in _FALLBACK_STOPS:
        if s["id"] == stop_id:
            return s
    return None
