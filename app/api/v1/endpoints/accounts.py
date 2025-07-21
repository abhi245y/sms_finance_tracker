from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import List, Any

from app.crud import crud_account
from app.core.config import settings
from app.schemas import account as account_schema
from app.api import deps

router = APIRouter()

async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != settings.IPHONE_SHORTCUT_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )

@router.post(
    "/",
    response_model=account_schema.Account,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new account",
    dependencies=[Depends(verify_api_key)]
)
def create_new_account(
    *,
    db: Session = Depends(deps.get_db),
    account_in: account_schema.AccountCreate,
) -> Any:
    """
    Create a new account (e.g., a credit card, savings account).
    This is used to manually register your payment methods with the system.
    """

    existing_account = crud_account.get_account_by_identifier(
        db,
        bank_name=account_in.bank_name,
        account_last4=account_in.account_last4
    )
    if existing_account:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"An account with bank '{account_in.bank_name}' and last 4 digits '{account_in.account_last4}' already exists.",
        )
    
    account = crud_account.create_account(db=db, obj_in=account_in)
    return account

@router.get(
    "/",
    response_model=List[account_schema.Account],
    summary="Get a list of all registered accounts",
    dependencies=[Depends(verify_api_key)]
)
def read_all_accounts(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve all registered accounts.
    """
    accounts = crud_account.get_accounts(db, skip=skip, limit=limit)
    return accounts

@router.get(
    "/for-mini-app",
    response_model=List[account_schema.Account],
    summary="Get a list of all registered accounts (For Mini App)",
    # dependencies=[Depends(deps.get_transaction_hash_from_token)]
)
def read_all_accounts_mini_app(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve all registered accounts.
    """
    accounts = crud_account.get_accounts(db, skip=skip, limit=limit)
    return accounts


@router.get(
    "/{account_id}",
    response_model=account_schema.Account,
    summary="Get a specific account by its ID",
    dependencies=[Depends(verify_api_key)]
)
def read_account_by_id(
    account_id: int,    
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get a specific account by its ID.
    """
    account = crud_account.get_account(db=db, account_id=account_id)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account with ID {account_id} not found.",
        )
    return account

@router.patch(
    "/{account_id}",
    response_model=account_schema.Account,
    summary="Update an account",
    dependencies=[Depends(verify_api_key)]
)
def update_existing_account(
    *,
    db: Session = Depends(deps.get_db),
    account_id: int,
    account_in: account_schema.AccountUpdate,
) -> Any:
    """
    Update an account's details, such as its user-friendly name or type.
    """
    db_account = crud_account.get_account(db=db, account_id=account_id)
    if not db_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account with ID {account_id} not found.",
        )
    
    update_data = account_in.model_dump(exclude_unset=True)
    if "bank_name" in update_data or "account_last4" in update_data:
        # This is a design choice. Forcing users to delete and recreate an account if the
        # core identifiers are wrong can be safer than allowing direct updates.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Updating 'bank_name' or 'account_last4' is not permitted. Please create a new account."},
        )

    updated_account = crud_account.update_account(db=db, db_obj=db_account, obj_in=account_in)
    return updated_account
