"""
PMPML Saarthi — FastAPI Backend

Endpoints:
  POST /parse-destination   → extract destination from raw voice text
  POST /find-route          → plan a trip (nearest stop → destination stop → route)
  POST /check-proximity     → check if user is near a target stop (for alighting alert)
"""

from datetime import datetime, timezone
import random
from typing import List, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from nlp_utils import extract_destination, detect_command
from geo_utils import haversine, find_nearest_stop, find_stop_by_name, bearing, stops_between
from firebase_client import get_all_stops, get_all_routes, get_route_by_id, get_live_buses, get_stop_by_id

# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(
    title="PMPML Saarthi API",
    version="0.1.0",
    description="Voice-first backend for navigating Pune's PMPML bus network.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------
class ParseRequest(BaseModel):
    text: str


class ParseResponse(BaseModel):
    destination: Optional[str] = None
    command: Optional[str] = None


class RouteRequest(BaseModel):
    user_lat: float
    user_lng: float
    destination_name: str


class StopInfo(BaseModel):
    id: str
    name: str
    lat: float
    lng: float
    distance_meters: Optional[float] = None


class RouteResponse(BaseModel):
    nearest_stop: StopInfo
    destination_stop: StopInfo
    route_name: str
    route_id: str
    next_bus_eta_minutes: int
    stops_on_journey: List[str]
    total_stops: int
    walk_direction: str
    walk_distance_meters: float
    speech: str


class ProximityRequest(BaseModel):
    user_lat: float
    user_lng: float
    target_stop_lat: float
    target_stop_lng: float


class ProximityResponse(BaseModel):
    distance_meters: float
    alert: bool
    message: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/")
def health():
    return {"status": "ok", "service": "PMPML Saarthi API"}


@app.post("/parse-destination", response_model=ParseResponse)
def parse_destination(req: ParseRequest):
    """
    Takes raw transcribed voice text and returns:
      - destination (extracted place name), OR
      - command ('repeat', 'cancel', 'where_am_i')
    """
    command = detect_command(req.text)
    if command:
        return ParseResponse(command=command)

    destination = extract_destination(req.text)
    return ParseResponse(destination=destination)


@app.post("/find-route", response_model=RouteResponse)
def find_route(req: RouteRequest):
    """
    Given the user's GPS position and spoken destination name, returns the
    best bus route connecting the nearest stop to the destination stop.
    """
    all_stops = get_all_stops()
    all_routes = get_all_routes()

    # 1. Find nearest stop to the user (within 5 km for demo friendliness)
    nearest = find_nearest_stop(req.user_lat, req.user_lng, all_stops, max_radius_m=5000)
    if not nearest:
        nearest = min(all_stops, key=lambda s: haversine(req.user_lat, req.user_lng, s["lat"], s["lng"]))
        nearest["distance_meters"] = round(haversine(req.user_lat, req.user_lng, nearest["lat"], nearest["lng"]), 1)

    # 2. Find the destination stop by name
    dest_stop = find_stop_by_name(req.destination_name, all_stops)
    if not dest_stop:
        # fallback: pick a stop that partially matches
        dest_name_lower = req.destination_name.lower()
        for s in all_stops:
            if dest_name_lower[:4] in s["name"].lower():
                dest_stop = s
                break
    if not dest_stop:
        # absolute fallback for demo
        dest_stop = all_stops[1]

    # 3. Find a route that contains BOTH stops
    chosen_route = None
    for route in all_routes:
        if nearest["id"] in route["stops"] and dest_stop["id"] in route["stops"]:
            chosen_route = route
            break

    # If no direct route, pick whatever route serves the nearest stop
    if not chosen_route:
        for route in all_routes:
            if nearest["id"] in route["stops"]:
                chosen_route = route
                # If dest_stop isn't on this route, pick the last stop as destination
                if dest_stop["id"] not in route["stops"]:
                    last_stop_id = route["stops"][-1]
                    dest_stop = get_stop_by_id(last_stop_id) or dest_stop
                break

    if not chosen_route:
        chosen_route = all_routes[0]

    # 4. Compute journey segment
    journey_stops, num_stops = stops_between(
        chosen_route["stops"], nearest["id"], dest_stop["id"]
    )
    journey_stop_names = []
    for sid in journey_stops:
        s = get_stop_by_id(sid)
        journey_stop_names.append(s["name"] if s else sid)

    # 5. Simulate next bus ETA
    freq = chosen_route.get("frequency_minutes", 15)
    eta = random.randint(2, freq)

    # 6. Walking direction and distance
    walk_dir = bearing(req.user_lat, req.user_lng, nearest["lat"], nearest["lng"])
    walk_dist = nearest.get("distance_meters", 0)

    # 7. Build spoken response
    speech = (
        f"Walk {int(walk_dist)} meters {walk_dir} to {nearest['name']} Bus Stop. "
        f"Board Bus {chosen_route['name'].replace('Route ', '')} arriving in {eta} minutes. "
        f"Your journey has {num_stops} stops. "
        f"I will alert you before your stop."
    )

    return RouteResponse(
        nearest_stop=StopInfo(
            id=nearest["id"],
            name=nearest["name"],
            lat=nearest["lat"],
            lng=nearest["lng"],
            distance_meters=walk_dist,
        ),
        destination_stop=StopInfo(
            id=dest_stop["id"],
            name=dest_stop["name"],
            lat=dest_stop["lat"],
            lng=dest_stop["lng"],
        ),
        route_name=chosen_route["name"],
        route_id=chosen_route["id"],
        next_bus_eta_minutes=eta,
        stops_on_journey=journey_stop_names,
        total_stops=num_stops,
        walk_direction=walk_dir,
        walk_distance_meters=walk_dist,
        speech=speech,
    )


@app.post("/check-proximity", response_model=ProximityResponse)
def check_proximity(req: ProximityRequest):
    """
    Returns how far the user is from a target stop and whether to trigger
    an alighting alert (≤ 200 m).
    """
    dist = haversine(req.user_lat, req.user_lng, req.target_stop_lat, req.target_stop_lng)
    dist_rounded = round(dist, 1)
    should_alert = dist_rounded <= 200

    if should_alert:
        message = "You are approaching your destination stop. Prepare to get off."
    else:
        message = f"You are {int(dist_rounded)} meters from your stop."

    return ProximityResponse(
        distance_meters=dist_rounded,
        alert=should_alert,
        message=message,
    )
