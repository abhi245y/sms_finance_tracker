from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.account import Account as AccountModel, AccountType
from app.schemas.account import AccountCreate, AccountUpdate

# --- READ Operations ---

def get_account(db: Session, account_id: int) -> Optional[AccountModel]:
    """Get a single account by its ID."""
    return db.query(AccountModel).filter(AccountModel.id == account_id).first()

def get_account_by_identifier(db: Session, *, bank_name: str, account_last4: str) -> Optional[AccountModel]:
    """Get a single account by its unique composite key (bank_name + last4)."""
    return db.query(AccountModel).filter(
        AccountModel.bank_name == bank_name,
        AccountModel.account_last4 == account_last4
    ).first()

def get_account_by_type(db: Session, account_type: AccountType, skip: int = 0, limit: int = 100) -> Optional[AccountModel]:
    """Get a list of all accounts  of given type."""
    return db.query(AccountModel).filter(
        AccountModel.account_type == account_type
    ).offset(skip).limit(limit).all()

def get_accounts(db: Session, skip: int = 0, limit: int = 100) -> List[AccountModel]:
    """Get a list of all accounts."""
    return db.query(AccountModel).order_by(AccountModel.name).offset(skip).limit(limit).all()

# --- CREATE Operation ---

def create_account(db: Session, *, obj_in: AccountCreate) -> AccountModel:
    """Create a new account."""
    db_obj = AccountModel(
        name=obj_in.name,
        account_type=obj_in.account_type,
        bank_name=obj_in.bank_name,
        account_last4=obj_in.account_last4
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

# --- UPDATE Operation ---

def update_account(
    db: Session,
    *,
    db_obj: AccountModel,
    obj_in: AccountUpdate
) -> AccountModel:
    """Update an existing account."""
    update_data = obj_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

# --- DELETE Operation ---
# Note: Need a strategy for what happens to transactions linked to a deleted account.
# For now, we'll just provide the function.
def delete_account(db: Session, *, account_id: int) -> Optional[AccountModel]:
    """Delete an account by ID."""
    db_obj = db.query(AccountModel).filter(AccountModel.id == account_id).first()
    if db_obj:
        db.delete(db_obj)
        db.commit()
    return db_obj