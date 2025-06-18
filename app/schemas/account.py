from pydantic import BaseModel, Field, constr
from typing import List, Optional

from app.models import AccountType, AccountPurpose

# --- Base Schema ---
# Contains fields common to creating and reading an account.
class AccountBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, example="HDFC Salary Account")
    account_type: AccountType = Field(..., example=AccountType.SAVINGS_ACCOUNT)
    bank_name: str = Field(..., max_length=100, example="HDFC Bank")
    account_last4: constr(pattern=r'^\d{4}$') = Field(..., example="1234")
    purpose: AccountPurpose = Field(default=AccountPurpose.PERSONAL, example=AccountPurpose.PERSONAL)

# --- Schema for Creating an Account ---
# This is what the API will expect in the POST request body.
class AccountCreate(AccountBase):
    pass # No new fields for creation, it's the same as the base

# --- Schema for Updating an Account ---
# All fields are optional for partial updates (PATCH).
class AccountUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    account_type: Optional[AccountType] = None
    purpose: Optional[AccountPurpose] = None

# --- Schema for Reading/Returning an Account from DB ---
# This represents an account as it is stored in the database, including its ID.
class AccountInDBBase(AccountBase):
    id: int

    class Config:
        orm_mode = True

class Account(AccountInDBBase):
    pass # For now, same as AccountInDBBase

# --- Schema for a list of accounts ---
class AccountList(BaseModel):
    accounts: List[Account]