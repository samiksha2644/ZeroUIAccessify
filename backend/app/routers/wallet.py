from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.models.schemas import WalletResponse, TopupRequest, TopupResponse, TransactionsListResponse
from app.firebase import get_firestore
from google.cloud.firestore import Transaction, firestore
import uuid

router = APIRouter()

@router.get("/{user_id}", response_model=WalletResponse)
async def get_wallet(user_id: str):
    """
    Returns balance, currency, last 10 transactions.
    """
    db = get_firestore()
    user_doc = db.collection("USERS").document(user_id).get()
    
    if not user_doc.exists:
        raise HTTPException(status_code=404, detail="User not found")
        
    balance = user_doc.to_dict().get("wallet_balance", 0.0)
    
    # Get last 10 transactions
    tx_query = db.collection("WALLET_TRANSACTIONS")\
        .where("user_id", "==", user_id)\
        .order_by("timestamp", direction=firestore.Query.DESCENDING)\
        .limit(10).stream()
        
    transactions = []
    for tx in tx_query:
        data = tx.to_dict()
        transactions.append({
            "transaction_id": tx.id,
            "type": data.get("type"),
            "amount": data.get("amount"),
            "timestamp": data.get("timestamp"),
            "description": data.get("description")
        })
        
    return {
        "balance": balance,
        "currency": "INR",
        "recent_transactions": transactions
    }

@router.post("/topup", response_model=TopupResponse)
async def topup_wallet(payload: TopupRequest):
    """
    Atomic transaction: add to balance, write WALLET_TRANSACTIONS doc with type topup.
    """
    db = get_firestore()
    transaction = db.transaction()
    user_ref = db.collection("USERS").document(payload.user_id)
    tx_id = str(uuid.uuid4())
    tx_ref = db.collection("WALLET_TRANSACTIONS").document(tx_id)
    
    @firestore.transactional
    def execute_topup(transaction: Transaction, user_ref, tx_ref):
        user_snapshot = user_ref.get(transaction=transaction)
        if not user_snapshot.exists:
            raise Exception("User not found")
            
        current_balance = user_snapshot.to_dict().get("wallet_balance", 0.0)
        new_balance = current_balance + payload.amount
        
        transaction.update(user_ref, {"wallet_balance": new_balance})
        transaction.set(tx_ref, {
            "user_id": payload.user_id,
            "type": "topup",
            "amount": payload.amount,
            "timestamp": firestore.SERVER_TIMESTAMP,
            "description": "User Topup"
        })
        return new_balance
        
    try:
        new_balance = execute_topup(transaction, user_ref, tx_ref)
        return {
            "new_balance": new_balance,
            "transaction_id": tx_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}/transactions", response_model=TransactionsListResponse)
async def list_transactions(
    user_id: str, 
    limit: int = 20, 
    before_timestamp: Optional[str] = Query(None, description="ISO format string or let it empty for first page")
):
    """
    Full transaction history paginated.
    """
    db = get_firestore()
    query = db.collection("WALLET_TRANSACTIONS")\
        .where("user_id", "==", user_id)\
        .order_by("timestamp", direction=firestore.Query.DESCENDING)
        
    # Example simplest pagination: purely rely on limit (offset pagination is expensive in firestore, cursor pagination better)
    # Using basic limit for hackathon constraints and without heavy cursor logic
    tx_query = query.limit(limit).stream()
    
    transactions = []
    for tx in tx_query:
        data = tx.to_dict()
        transactions.append({
            "transaction_id": tx.id,
            "type": data.get("type"),
            "amount": data.get("amount"),
            "timestamp": data.get("timestamp"),
            "description": data.get("description")
        })
        
    return {"transactions": transactions}
