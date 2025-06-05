from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.transaction import TransactionStatus

class SMSRecieved(BaseModel):
    sms_content: str

class TransactionBase(BaseModel):
    raw_sms_content: str
    amount: Optional[float] = None
    currency: Optional[str] = "INR"
    transaction_type: Optional[str] = None
    account_identifier: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    status: TransactionStatus = TransactionStatus.PENDING_CATEGORIZATION
    merchant_vpa: Optional[str] = None
    transaction_datetime_from_sms: Optional[datetime] = None
    bank_name: Optional[str] = None

class TransactionCreate(TransactionBase):
    pass # For now, same as base

class TransactionUpdate(BaseModel): # For later when user updates
    amount: Optional[float] = None
    transaction_type: Optional[str] = None
    account_identifier: Optional[str] = None
    category: Optional[str] = None
    status: Optional[TransactionStatus] = None
    description: Optional[str] = None

class TransactionInDB(TransactionBase):
    id: int
    received_at: datetime

    class Config:
        orm_mode = True # For Pydantic to work with SQLAlchemy models