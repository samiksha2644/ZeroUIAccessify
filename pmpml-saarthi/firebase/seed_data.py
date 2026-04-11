#!/usr/bin/env python3
"""
seed_data.py — Populate Firestore with sample PMPML stops, routes, and live buses.

Usage:
    1. Set FIREBASE_CREDENTIALS_PATH in .env (or export it).
    2. pip install firebase-admin python-dotenv
    3. python firebase/seed_data.py
"""

import os
import sys
from datetime import datetime, timezone

from dotenv import load_dotenv

# Load .env from repository root (one level up from /firebase/)
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))


def get_firestore_client():
    import firebase_admin
    from firebase_admin import credentials, firestore

    cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
    if not cred_path or not os.path.isfile(cred_path):
        print(
            "ERROR: FIREBASE_CREDENTIALS_PATH is not set or file does not exist.\n"
            "       Please create a .env file with:\n"
            "         FIREBASE_CREDENTIALS_PATH=./firebase/firebase-credentials.json"
        )
        sys.exit(1)

    if not firebase_admin._apps:
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)

    return firestore.client()


# ---------------------------------------------------------------------------
# Sample data
# ---------------------------------------------------------------------------

BUS_STOPS = [
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

BUS_ROUTES = [
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

LIVE_BUSES = [
    {"id": "bus_156_a", "route_id": "route_156", "current_stop_index": 1,
     "last_updated": datetime.now(timezone.utc).isoformat()},
    {"id": "bus_11_a",  "route_id": "route_11",  "current_stop_index": 0,
     "last_updated": datetime.now(timezone.utc).isoformat()},
    {"id": "bus_50_a",  "route_id": "route_50",  "current_stop_index": 0,
     "last_updated": datetime.now(timezone.utc).isoformat()},
]


def seed():
    db = get_firestore_client()

    print("Seeding bus_stops …")
    for stop in BUS_STOPS:
        doc_data = {k: v for k, v in stop.items() if k != "id"}
        db.collection("bus_stops").document(stop["id"]).set(doc_data)
        print(f"  ✓ {stop['name']}")

    print("\nSeeding bus_routes …")
    for route in BUS_ROUTES:
        doc_data = {k: v for k, v in route.items() if k != "id"}
        db.collection("bus_routes").document(route["id"]).set(doc_data)
        print(f"  ✓ {route['name']}")

    print("\nSeeding live_buses …")
    for bus in LIVE_BUSES:
        doc_data = {k: v for k, v in bus.items() if k != "id"}
        db.collection("live_buses").document(bus["id"]).set(doc_data)
        print(f"  ✓ {bus['id']}")

    print("\n🎉 Firestore seeded successfully!")


if __name__ == "__main__":
    seed()
