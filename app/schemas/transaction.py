from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.transaction import TransactionStatus

class SMSRecieved(BaseModel):
    sms_content: str

class TransactionBase(BaseModel):
    # Core data fields parsed from SMS
    amount: Optional[float] = None
    currency: Optional[str] = "INR"
    merchant_vpa: Optional[str] = None
    transaction_datetime_from_sms: Optional[datetime] = None
    description: Optional[str] = None
    raw_sms_content: str

    unique_hash: str
    account_id: Optional[int] = None
    category_id: Optional[int] = 11
    
    status: TransactionStatus = TransactionStatus.PENDING_PROCESSING
    
    class Config:
        orm_mode = True

class TransactionCreate(TransactionBase):
    pass

class TransactionUpdate(BaseModel):
    """
    Schema for updating an existing transaction. All fields are optional.
    This will be used in the PATCH request body.
    """
    account_id: Optional[int] = None
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class CategoryForTransaction(BaseModel):
    """A minimal Category schema for embedding in a Transaction response."""
    id: int
    name: str
    class Config:
        orm_mode = True
        
class AccountForTransaction(BaseModel):
    """A minimal Account schema for embedding in a Transaction response."""
    id: int
    name: str
    account_type: str
    class Config:
        orm_mode = True

class TransactionInDB(TransactionBase):
    """
    The comprehensive schema for representing a transaction when returned from the API.
    Includes database-generated fields and nested objects for related models.
    """
    id: int
    unique_hash: str
    received_at: datetime
    status: str
    account: Optional[AccountForTransaction] = None
    category_obj: Optional[CategoryForTransaction] = None

    class Config:
        orm_mode = True