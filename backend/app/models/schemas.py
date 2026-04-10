from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# --- Auth Models ---
class UserRegistration(BaseModel):
    name: str = Field(..., description="User's full name")
    phone: str = Field(..., description="User's phone number")
    language: str = Field(default="en", description="Preferred language, e.g., en, mr, hi")
    home_lat: Optional[float] = Field(None, description="Home location latitude")
    home_lng: Optional[float] = Field(None, description="Home location longitude")

class UserRegistrationResponse(BaseModel):
    user_id: str

class UserProfile(BaseModel):
    user_id: str
    name: str
    phone: str
    language: str
    wallet_balance: float
    home_lat: Optional[float]
    home_lng: Optional[float]

# --- Stops Models ---
class StopResponse(BaseModel):
    stop_id: str
    stop_name: str
    lat: float
    lng: float
    distance_m: float = Field(..., description="Distance from user in meters")

# --- Journey Models ---
class JourneyPlanRequest(BaseModel):
    origin_stop_id: str
    dest_stop_id: str
    user_id: str

class JourneyPlanResponse(BaseModel):
    route_id: str
    route_name: str
    departure_stop: str
    arrival_stop: str
    estimated_duration_mins: int
    estimated_fare: float

# --- Trip Models ---
class TripStartRequest(BaseModel):
    user_id: str
    origin_stop_id: str
    dest_stop_id: str
    route_id: str
    bus_id: str

class TripStartResponse(BaseModel):
    trip_id: str

class TripLocationRequest(BaseModel):
    lat: float
    lng: float

class TripLocationResponse(BaseModel):
    status: str = Field(..., description="e.g., 'on_track', 'arrived', 'wrong_direction'")
    alert_type: Optional[str] = None
    message: str

class TripEndResponse(BaseModel):
    fare_paid: float
    new_balance: float

# --- Wallet Models ---
class TransactionModel(BaseModel):
    transaction_id: str
    type: str # 'topup', 'fare_deduction'
    amount: float
    timestamp: datetime
    description: Optional[str] = None

class WalletResponse(BaseModel):
    balance: float
    currency: str = "INR"
    recent_transactions: List[TransactionModel]

class TopupRequest(BaseModel):
    user_id: str
    amount: float = Field(..., gt=0, description="Amount to top up")

class TopupResponse(BaseModel):
    new_balance: float
    transaction_id: str

class TransactionsListResponse(BaseModel):
    transactions: List[TransactionModel]
