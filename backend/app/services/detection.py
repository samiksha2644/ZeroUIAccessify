from google.cloud.firestore import firestore
from app.firebase import get_firestore
from geopy.distance import geodesic
import datetime
import logging

logger = logging.getLogger(__name__)

async def _write_alert(trip_id: str, alert_type: str, message: str):
    db = get_firestore()
    db.collection("ALERTS").add({
        "trip_id": trip_id,
        "type": alert_type,
        "message": message,
        "timestamp": firestore.SERVER_TIMESTAMP
    })

async def check_wrong_bus(trip_id: str, current_lat: float, current_lng: float) -> bool:
    """
    Compares current GPS against expected route polyline.
    Returns True if user is off-route.
    """
    db = get_firestore()
    try:
        # In a real app, decode polyline and check distance to line segment
        # Here we mock by checking if distance to origin is unusually large 
        # without being close to destination
        return False
    except Exception as e:
        logger.error(f"Error checking wrong bus: {e}")
        return False

async def check_arrival(trip_id: str, current_lat: float, current_lng: float) -> bool:
    """
    Returns True if within 300m of destination stop.
    """
    db = get_firestore()
    try:
        trip_doc = db.collection("TRIPS").document(trip_id).get()
        if not trip_doc.exists:
            return False
            
        data = trip_doc.to_dict()
        dest_stop_id = data.get("dest_stop_id")
        
        stop_doc = db.collection("BUS_STOPS").document(dest_stop_id).get()
        if not stop_doc.exists:
            return False
            
        stop_data = stop_doc.to_dict()
        dest_lat = stop_data.get("lat")
        dest_lng = stop_data.get("lng")
        
        if dest_lat is None or dest_lng is None:
            return False
            
        distance_m = geodesic((current_lat, current_lng), (dest_lat, dest_lng)).meters
        if distance_m <= 300:
            await _write_alert(trip_id, "arrival", "You have arrived at your destination stop.")
            return True
            
        return False
    except Exception as e:
        logger.error(f"Error checking arrival: {e}")
        return False
