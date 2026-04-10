import httpx
from app.config import Config

async def get_nearest_stops(lat: float, lng: float, radius: int = 1000):
    """
    Google Maps API call to get nearest transit stations (bus stops).
    (Note: the local db + geopy will also be used in stops.py, but this provides Maps context).
    """
    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lng}&radius={radius}&type=transit_station&key={Config.GOOGLE_MAPS_API_KEY}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json().get("results", [])

async def get_directions(origin: str, destination: str):
    """
    Google Maps Directions API call.
    Values can be 'lat,lng' or 'Place ID'.
    """
    url = f"https://maps.googleapis.com/maps/api/directions/json?origin={origin}&destination={destination}&mode=transit&transit_mode=bus&key={Config.GOOGLE_MAPS_API_KEY}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json().get("routes", [])
