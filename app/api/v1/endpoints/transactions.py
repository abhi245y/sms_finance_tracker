from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from typing import Any, List


from app.api import deps
from app.core.config import settings
from app.services.sms_parser import parse_sms_content

from app.schemas.transaction import TransactionInDB, SMSRecieved, TransactionCreate
from app.crud import crud_transaction

router = APIRouter()

async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != settings.IPHONE_SHORTCUT_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )

@router.post("/", response_model=TransactionInDB, dependencies=[Depends(verify_api_key)])
def receive_sms(
    *,
    db: Session = Depends(deps.get_db),
    sms_in: SMSRecieved,
) -> Any:
    """
    Receive SMS content from iPhone Shortcut.
    """
    parsed_data = parse_sms_content(sms_in.sms_content)
    
    if not parsed_data:

        """
        
        If parser returns None (e.g., it's a credit transaction or unparseable as spend),
        you might choose to not create a transaction record, or create one with a specific status.
        For now, let's assume we only want to store spend transactions that were parsed.
        You could also log sms_in.sms_content here for manual review of unparsed messages.
        
        """
        print(f"SMS not processed as spend or unparseable: {sms_in.sms_content[:100]}")

        return {"message": "SMS not processed as a spend transaction or was unparseable."}


    transaction_in_data = {
        "raw_sms_content": sms_in.sms_content,
        "amount": parsed_data.get("amount"),
        "currency": parsed_data.get("currency", "INR"),
        "description": parsed_data.get("description"),
        "transaction_type": parsed_data.get("transaction_type"),
        "account_identifier": parsed_data.get("account_identifier"),
        "bank_name":  parsed_data.get("bank_name"),
        "merchant_vpa": parsed_data.get("merchant_vpa"),
        "transaction_datetime_from_sms": parsed_data.get("transaction_datetime_from_sms")
    }
    
    print(f"Transation Data: {transaction_in_data}")
    
    # Filter out None values before passing to Pydantic model to allow optional fields
    transaction_in_data_cleaned = {k: v for k, v in transaction_in_data.items() if v is not None}
    
    transaction_in = TransactionCreate(**transaction_in_data_cleaned)
    transaction = crud_transaction.create_transaction(db=db, obj_in=transaction_in)
    return transaction

@router.get("/", response_model=List[TransactionInDB])
def read_transactions(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve transactions.
    """
    transactions = crud_transaction.get_transactions(db, skip=skip, limit=limit)
    return transactions
