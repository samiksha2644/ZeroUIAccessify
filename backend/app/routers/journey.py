from fastapi import APIRouter, HTTPException
from app.models.schemas import JourneyPlanRequest, JourneyPlanResponse
from app.firebase import get_firestore

router = APIRouter()

@router.post("/plan", response_model=JourneyPlanResponse)
async def plan_journey(payload: JourneyPlanRequest):
    """
    Query ROUTE_STOPS to find all routes containing both stops. 
    Rank by minimum stop sequence difference (assuming sequential stops).
    Returns route_id, route_name, departure_stop, arrival_stop, est_duration, est_fare.
    """
    db = get_firestore()
    
    # 1. Get routes that have origin
    origin_query = db.collection("ROUTE_STOPS")\
        .where("stop_id", "==", payload.origin_stop_id).stream()
    
    origin_routes = {doc.to_dict()["route_id"]: doc.to_dict() for doc in origin_query}
    
    # 2. Get routes that have destination
    dest_query = db.collection("ROUTE_STOPS")\
        .where("stop_id", "==", payload.dest_stop_id).stream()
        
    dest_routes = {doc.to_dict()["route_id"]: doc.to_dict() for doc in dest_query}
    
    # 3. Find common routes
    common_route_ids = set(origin_routes.keys()).intersection(set(dest_routes.keys()))
    
    if not common_route_ids:
        raise HTTPException(status_code=404, detail="No direct routes found between these stops.")
    
    best_route_id = None
    min_diff = float('inf')
    
    for rid in common_route_ids:
        seq_origin = origin_routes[rid].get("stop_sequence", 0)
        seq_dest = dest_routes[rid].get("stop_sequence", 0)
        
        diff = seq_dest - seq_origin
        if diff > 0 and diff < min_diff:
            min_diff = diff
            best_route_id = rid
            
    if not best_route_id:
        raise HTTPException(status_code=404, detail="No valid forward route found.")
        
    try:
        route_doc = db.collection("ROUTES").document(best_route_id).get()
        route_name = route_doc.to_dict().get("route_name", best_route_id) if route_doc.exists else best_route_id
    except:
        route_name = best_route_id

    # Mock estimations
    est_duration_mins = min_diff * 3  # roughly 3 mins per stop
    est_fare = 15.0  # Would use fare.py calculate_fare in reality
    
    return {
        "route_id": best_route_id,
        "route_name": route_name,
        "departure_stop": payload.origin_stop_id,
        "arrival_stop": payload.dest_stop_id,
        "estimated_duration_mins": est_duration_mins,
        "estimated_fare": est_fare
    }
