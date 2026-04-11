"""
Geospatial utilities — haversine distance and nearest-stop finder.
All distances are in meters.
"""

import math
from typing import List, Dict, Optional, Tuple


def haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Return distance in meters between two (lat, lng) points."""
    R = 6_371_000  # Earth radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lng2 - lng1)

    a = (
        math.sin(d_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    )
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def find_nearest_stop(
    lat: float, lng: float, stops: List[Dict], max_radius_m: float = 500.0
) -> Optional[Dict]:
    """
    Given a user's position and a list of stop dicts (each having 'lat' and
    'lng' keys), return the closest stop within *max_radius_m*, or None.
    """
    best: Optional[Dict] = None
    best_dist = float("inf")

    for stop in stops:
        d = haversine(lat, lng, stop["lat"], stop["lng"])
        if d < best_dist and d <= max_radius_m:
            best_dist = d
            best = {**stop, "distance_meters": round(d, 1)}

    return best


def find_stop_by_name(
    name: str, stops: List[Dict]
) -> Optional[Dict]:
    """Case-insensitive partial match on stop name."""
    name_lower = name.lower().strip()
    for stop in stops:
        if name_lower in stop["name"].lower():
            return stop
    return None


def bearing(lat1: float, lng1: float, lat2: float, lng2: float) -> str:
    """Return a human-readable compass direction from point 1 to point 2."""
    d_lng = math.radians(lng2 - lng1)
    phi1, phi2 = math.radians(lat1), math.radians(lat2)

    x = math.sin(d_lng) * math.cos(phi2)
    y = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(d_lng)
    angle = (math.degrees(math.atan2(x, y)) + 360) % 360

    directions = ["north", "northeast", "east", "southeast",
                   "south", "southwest", "west", "northwest"]
    idx = int((angle + 22.5) // 45) % 8
    return directions[idx]


def stops_between(
    route_stops: List[str], from_stop_id: str, to_stop_id: str
) -> Tuple[List[str], int]:
    """
    Return the ordered sub-list of stop IDs the rider passes through
    (inclusive) and how many stops remain after boarding.
    Works for both forward and reverse travel on a route.
    """
    if from_stop_id not in route_stops or to_stop_id not in route_stops:
        return [], 0

    from_idx = route_stops.index(from_stop_id)
    to_idx = route_stops.index(to_stop_id)

    if from_idx <= to_idx:
        segment = route_stops[from_idx : to_idx + 1]
    else:
        segment = route_stops[to_idx : from_idx + 1][::-1]

    return segment, len(segment) - 1
