from pydantic import BaseModel,Field
from datetime import datetime
from typing import Optional
from app.models.transaction import TransactionStatus
from app.schemas.category import SubCategoryInDB

class SMSRecieved(BaseModel):
    sms_content: str

class TransactionBase(BaseModel):
    amount: Optional[float] = None
    currency: Optional[str] = Field("INR", example="INR")
    merchant_vpa: Optional[str] = None
    transaction_datetime_from_sms: Optional[datetime] = None
    description: Optional[str] = None
    raw_sms_content: str

    unique_hash: str
    linked_transaction_hash: Optional[str] = None
    subcategory_id: Optional[int] = None 
    
    account_id: Optional[int] = None
    
    status: TransactionStatus = TransactionStatus.PENDING_PROCESSING
    
    # exclude_from_cashflow: bool = Field(False, example=False)
    
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
    subcategory_id: Optional[int] = None    
    description: Optional[str] = None
    status: Optional[str] = None
    linked_transaction_hash: Optional[str] = None


class CategoryForTransaction(BaseModel):
    """A minimal Category schema for embedding in a Transaction response."""
    id: int
    name: str
    class Config:
        orm_mode = True
        
class SubCategoryForTransaction(BaseModel):
    id: int
    name: str
    icon_name: Optional[str] = None
    parent_category_id: int
    parent_category_name: str 

    class Config:
        orm_mode = True
        
class AccountForTransaction(BaseModel):
    """A minimal Account schema for embedding in a Transaction response."""
    id: int
    name: str
    account_type: str
    account_last4: str
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
    subcategory: Optional[SubCategoryInDB] = None

    class Config:
        orm_mode = True