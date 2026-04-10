from fastapi import APIRouter
from firebase_admin import firestore

router = APIRouter()

@router.get("/wallet/balance")
async def get_balance(user_id: str):
    db = firestore.client()
    wallet = db.collection("wallets")\
               .where("user_id", "==", user_id)\
               .get()
    if wallet:
        balance = wallet[0].to_dict()["balance"]
        return {"balance": balance, "message": f"Your balance is ₹{balance}"}
    return {"error": "Wallet not found"}

@router.post("/wallet/topup")
async def topup_wallet(user_id: str, amount: float):
    db = firestore.client()
    wallet_ref = db.collection("wallets")\
                   .where("user_id", "==", user_id)\
                   .get()
    if wallet_ref:
        doc = wallet_ref[0]
        new_balance = doc.to_dict()["balance"] + amount
        doc.reference.update({"balance": new_balance})
        db.collection("wallet_transactions").add({
            "user_id": user_id,
            "amount": amount,
            "type": "credit",
            "description": "Wallet top up",
            "timestamp": firestore.SERVER_TIMESTAMP
        })
        return {"message": f"₹{amount} added. New balance ₹{new_balance}"}
    return {"error": "Wallet not found"}

@router.post("/wallet/pay")
async def pay_from_wallet(user_id: str, fare: float, destination: str):
    db = firestore.client()
    wallet_ref = db.collection("wallets")\
                   .where("user_id", "==", user_id)\
                   .get()
    if wallet_ref:
        doc = wallet_ref[0]
        balance = doc.to_dict()["balance"]
        if balance < fare:
            return {"error": "Insufficient balance"}
        new_balance = balance - fare
        doc.reference.update({"balance": new_balance})
        db.collection("wallet_transactions").add({
            "user_id": user_id,
            "amount": fare,
            "type": "debit",
            "description": f"Ticket to {destination}",
            "timestamp": firestore.SERVER_TIMESTAMP
        })
        return {
            "message": f"₹{fare} paid. Ticket to {destination} confirmed.",
            "remaining_balance": new_balance
        }
    return {"error": "Wallet not found"}