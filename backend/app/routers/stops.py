from fastapi import APIRouter, Query, HTTPException
from typing import List
from app.models.schemas import StopResponse
from app.firebase import get_firestore
from geopy.distance import geodesic

router = APIRouter()

@router.get("/nearest", response_model=List[StopResponse])
async def get_nearest_stops(
    lat: float = Query(..., description="Latitude"),
    lng: float = Query(..., description="Longitude"),
    limit: int = Query(3, description="Number of results to return")
):
    """
    Query BUS_STOPS collection, calculate distance using geopy,
    return nearest N stops sorted by distance in metres.
    Note: A full DB scan is used here for simplicity in hackathon.
    In prod, use spatial indexing (like GeoHashes or Redis Geo).
    """
    db = get_firestore()
    stops_ref = db.collection("BUS_STOPS")
    
    try:
        # Full scan! Use with caution if > 10,000 stops
        stops = stops_ref.stream()
        results = []
        
        for stop in stops:
            data = stop.to_dict()
            s_lat = data.get("lat")
            s_lng = data.get("lng")
            
            if s_lat and s_lng:
                dist = geodesic((lat, lng), (s_lat, s_lng)).meters
                results.append({
                    "stop_id": stop.id,
                    "stop_name": data.get("name", "Unknown Stop"),
                    "lat": s_lat,
                    "lng": s_lng,
                    "distance_m": round(dist, 2)
                })
        
        # Sort and limit
        results.sort(key=lambda x: x["distance_m"])
        return results[:limit]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
