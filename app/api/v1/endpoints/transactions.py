from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from typing import Any, List 

from app.api import deps
from app.core.config import settings
from app.services.parser_engine import ParserEngine 

from app.schemas.transaction import TransactionInDB, SMSRecieved, TransactionCreate, TransactionUpdate
from app.models.transaction import TransactionStatus 
from app.models.account import AccountType
from app.crud import crud_transaction, crud_category, crud_account

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
    engine = ParserEngine(db_session=db)
    final_parsed_data = engine.run(sms_text=sms_in.sms_content)
    
    if not final_parsed_data:
        raise HTTPException(status_code=422, detail={"status":"SMS is a credit transaction, has an unparseable format, or a stable hash could not be generated."})
    
    existing_transaction = crud_transaction.get_transaction_by_hash(db, hash_str=final_parsed_data["unique_hash"])
    if existing_transaction:
        print(f"DEBUG: Duplicate transaction detected with hash {final_parsed_data['unique_hash']}. Returning existing transaction ID {existing_transaction.id}.")
        return existing_transaction
    
    account_id = final_parsed_data.get("account_id")
    account_type = crud_account.get_account(db=db, account_id=account_id).account_type
    
    if account_id and account_type != AccountType.UNKNOWN:
        current_status = TransactionStatus.PENDING_CATEGORIZATION
    else:
        current_status = TransactionStatus.PENDING_ACCOUNT_SELECTION

    final_parsed_data["status"] = current_status.value
    final_parsed_data["raw_sms_content"] = sms_in.sms_content
    
    transaction_to_create = TransactionCreate(**final_parsed_data)
    
    # TODO Implement Plan C: unique hash and duplicate check here)
    
    print(f"Transation Data: {transaction_to_create}")
  
    try:
        transaction = crud_transaction.create_transaction(db=db, obj_in=transaction_to_create)
    except Exception as e:
        print(f"Error creating Pydantic TransactionCreate model: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid transaction data: {e}")

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
    
@router.patch(
    "/{transaction_hash}",
    response_model=TransactionInDB,
    summary="Update a Transaction (Enrichment)",
    dependencies=[Depends(verify_api_key)]
)
def update_transaction_details(
    *,
    db: Session = Depends(deps.get_db),
    transaction_hash: str,
    transaction_in: TransactionUpdate,
) -> Any:
    """
    Update a transaction with enrichment data like an account or category.
    This is the primary endpoint for the interactive part of the Shortcut
    or a future UI to update transactions that are pending input.
    """

    print("Parameters and values:", locals())
    
    db_transaction = crud_transaction.get_transaction_by_hash(db=db, hash_str=transaction_hash)
    if not db_transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"status": f"Transaction with ID {transaction_hash} not found."},
        )


    if not transaction_in.dict(exclude_unset=True):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"status":"Request body is empty. Please provide fields to update."}
        )

    update_data = transaction_in.dict(exclude_unset=True)
    
    if "category_name" in update_data:
        update_data['category_id'] = crud_category.get_category_by_name(db, name=update_data["category_name"]).id
        category = crud_category.get_category(db=db, category_id=update_data['category_id'])
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with Name {update_data['category_name']} not found.",
            )

    if "account_id" in update_data:
        account = crud_account.get_account(db=db, account_id=update_data["account_id"])
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"status":f"Account with ID {update_data['account_id']} not found."},
            )
            
    
    if "category_id" in update_data:
        category = crud_category.get_category(db=db, category_id=update_data["category_id"])
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with ID {update_data['category_id']} not found.",
            )
            
    current_status = db_transaction.status

    if status != TransactionStatus.PROCESSED:
        has_account = db_transaction.account_id is not None or "account_id" in update_data
        has_category = db_transaction.category_id is not None or "category_id" in update_data or "category_name" in update_data

        if not has_account:
            current_status = TransactionStatus.PENDING_ACCOUNT_SELECTION
        elif not has_category:
            current_status = TransactionStatus.PENDING_CATEGORIZATION
        else:
            current_status = TransactionStatus.PROCESSED
    
    update_data["status"] = current_status.value
        
    update_schema = TransactionUpdate(**update_data)

    updated_transaction = crud_transaction.update_transaction(
        db=db,
        db_obj=db_transaction,
        obj_in=update_schema
    )
    
    print(updated_transaction)

    return updated_transaction