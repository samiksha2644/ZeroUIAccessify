from fastapi import APIRouter, HTTPException
from app.models.schemas import TripStartRequest, TripStartResponse, TripLocationRequest, TripLocationResponse, TripEndResponse
from app.firebase import get_firestore, get_realtime_db
from app.services.fare import calculate_fare, deduct_fare
from app.services.detection import check_wrong_bus, check_arrival
from google.cloud.firestore import firestore
import uuid

router = APIRouter()

@router.post("/start", response_model=TripStartResponse)
async def start_trip(payload: TripStartRequest):
    """
    Check wallet balance, create TRIPS doc, write to Realtime DB.
    """
    db = get_firestore()
    rdb = get_realtime_db()
    
    user_doc = db.collection("USERS").document(payload.user_id).get()
    if not user_doc.exists:
        raise HTTPException(status_code=404, detail="User not found")
        
    balance = user_doc.to_dict().get("wallet_balance", 0.0)
    est_fare = await calculate_fare(payload.origin_stop_id, payload.dest_stop_id, payload.route_id)
    
    if balance < est_fare:
        raise HTTPException(status_code=402, detail=f"Insufficient funds. Balance: {balance}, Est Fare: {est_fare}")
        
    trip_id = str(uuid.uuid4())
    
    # Write TRIPS doc
    db.collection("TRIPS").document(trip_id).set({
        "user_id": payload.user_id,
        "origin_stop_id": payload.origin_stop_id,
        "dest_stop_id": payload.dest_stop_id,
        "route_id": payload.route_id,
        "bus_id": payload.bus_id,
        "status": "active",
        "created_at": firestore.SERVER_TIMESTAMP,
        "estimated_fare": est_fare
    })
    
    # Write to Realtime DB
    rdb.child("active_trips").child(trip_id).set({
        "user_id": payload.user_id,
        "bus_id": payload.bus_id,
        "status": "active"
    })
    
    return {"trip_id": trip_id}

@router.put("/{trip_id}/location", response_model=TripLocationResponse)
async def update_location(trip_id: str, payload: TripLocationRequest):
    """
    Update logic check for wrong bus and arrival, and respond with alert.
    """
    is_wrong = await check_wrong_bus(trip_id, payload.lat, payload.lng)
    if is_wrong:
        return {"status": "wrong_direction", "alert_type": "warning", "message": "You might be on the wrong bus!"}
        
    is_arrived = await check_arrival(trip_id, payload.lat, payload.lng)
    if is_arrived:
        return {"status": "arrived", "alert_type": "success", "message": "You have arrived at your destination stop."}
        
    return {"status": "on_track", "message": "You are on track."}

@router.post("/{trip_id}/end", response_model=TripEndResponse)
async def end_trip(trip_id: str):
    """
    Calculate final fare, deduct using atomic transaction, map 'completed', remove from RTDB.
    """
    db = get_firestore()
    rdb = get_realtime_db()
    
    trip_doc = db.collection("TRIPS").document(trip_id).get()
    if not trip_doc.exists:
        raise HTTPException(status_code=404, detail="Trip not found")
        
    trip_data = trip_doc.to_dict()
    if trip_data.get("status") == "completed":
        raise HTTPException(status_code=400, detail="Trip already completed")
        
    user_id = trip_data.get("user_id")
    final_fare = trip_data.get("estimated_fare", 15.0)  # simplistic fallback
    
    try:
        new_balance = deduct_fare(user_id, trip_id, final_fare)
        # Remove from RTDB
        rdb.child("active_trips").child(trip_id).delete()
        
        return {
            "fare_paid": final_fare,
            "new_balance": new_balance
        }
    except Exception as e:
        raise HTTPException(status_code=402, detail=str(e))
