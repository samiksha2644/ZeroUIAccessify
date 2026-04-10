from app.firebase import get_firestore
from google.cloud.firestore import Transaction
import logging

logger = logging.getLogger(__name__)

async def calculate_fare(origin_stop_id: str, dest_stop_id: str, route_id: str) -> float:
    """
    Calculates fare between two stops on a route.
    Uses ROUTE_STOPS distance_from_start_m diff and FARE_ZONES base_fare + per_km_rate.
    For demonstration, we implement a mocked fallback if DB is missing data.
    """
    db = get_firestore()
    try:
        # Get start stop distance
        start_query = db.collection("ROUTE_STOPS")\
            .where("route_id", "==", route_id)\
            .where("stop_id", "==", origin_stop_id)\
            .limit(1).get()
        
        # Get end stop distance
        end_query = db.collection("ROUTE_STOPS")\
            .where("route_id", "==", route_id)\
            .where("stop_id", "==", dest_stop_id)\
            .limit(1).get()
        
        if not start_query or not end_query:
            return 15.0 # Fallback static fare

        start_dist = start_query[0].to_dict().get("distance_from_start_m", 0)
        end_dist = end_query[0].to_dict().get("distance_from_start_m", 1000)
        
        distance_km = abs(end_dist - start_dist) / 1000.0

        # Basic fare logic: Base fare + (distance * per_km_rate)
        # Mocking the FARE_ZONES read to avoid complexity in hackathon
        base_fare = 10.0
        per_km_rate = 2.0
        
        fare = base_fare + (distance_km * per_km_rate)
        return round(fare, 2)
    except Exception as e:
        logger.error(f"Error calculating fare: {e}")
        return 15.0 # fallback

def deduct_fare(user_id: str, trip_id: str, fare: float) -> float:
    """
    Deducts fare using a Firestore atomic transaction.
    """
    db = get_firestore()
    transaction = db.transaction()
    user_ref = db.collection("USERS").document(user_id)
    trip_ref = db.collection("TRIPS").document(trip_id)
    
    @firestore.transactional
    def update_in_transaction(transaction: Transaction, user_ref, trip_ref):
        user_snapshot = user_ref.get(transaction=transaction)
        if not user_snapshot.exists:
            raise Exception("User not found")
        
        current_balance = user_snapshot.to_dict().get("wallet_balance", 0.0)
        if current_balance < fare:
            raise Exception("Insufficient funds")
        
        new_balance = current_balance - fare
        
        # Update user balance
        transaction.update(user_ref, {"wallet_balance": new_balance})
        # Update trip status
        transaction.update(trip_ref, {
            "status": "completed",
            "fare_paid": fare
        })
        
        return new_balance

    return update_in_transaction(transaction, user_ref, trip_ref)
