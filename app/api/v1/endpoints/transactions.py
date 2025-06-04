from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from typing import Any, List

from app import crud
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

    transaction_in = TransactionCreate(
        raw_sms_content=sms_in.sms_content,
        amount=parsed_data.get("amount"),
        currency=parsed_data.get("currency"),
        description=parsed_data.get("description")
        # other fields can be None initially
    )
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
