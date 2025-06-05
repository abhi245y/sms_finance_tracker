from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.transaction import TransactionStatus

class SMSRecieved(BaseModel):
    sms_content: str
    category_name: Optional[str] = None

class TransactionBase(BaseModel):
    raw_sms_content: str
    amount: Optional[float] = None
    currency: Optional[str] = "INR"
    transaction_type: Optional[str] = None
    account_identifier: Optional[str] = None
    description: Optional[str] = None
    status: TransactionStatus = TransactionStatus.PENDING_CATEGORIZATION
    merchant_vpa: Optional[str] = None
    transaction_datetime_from_sms: Optional[datetime] = None
    bank_name: Optional[str] = None

class TransactionCreate(TransactionBase):
    category_id: Optional[int] = None
    status: Optional[str] = "pending_categorization"

class TransactionUpdate(BaseModel): # For later when user updates
    amount: Optional[float] = None
    category_id: Optional[int] = None
    transaction_type: Optional[str] = None
    account_identifier: Optional[str] = None
    category: Optional[str] = None
    status: Optional[TransactionStatus] = None
    description: Optional[str] = None


class CategoryForTransaction(BaseModel):
    id: int
    name: str
    class Config:
        orm_mode = True

class TransactionInDB(TransactionBase):
    id: int
    received_at: datetime
    status: str
    category_id: Optional[int] = None 
    category_obj: Optional[CategoryForTransaction] = None

    class Config:
        orm_mode = True