from fastapi import APIRouter, Depends, HTTPException, Header, status, BackgroundTasks
from app.services import telegram_notifier
from sqlalchemy.orm import Session
from typing import Any, List 

from app.api import deps
from app.core.config import settings
from app.services.parser_engine import ParserEngine
from app.services.transaction_status_manager import TransactionStatusManager

from app.schemas.transaction import (
    TransactionInDB, SMSRecieved, TransactionCreate, TransactionUpdate,
    SubCategoryForTransaction ,
    AccountForTransaction  
)
from app.crud import crud_transaction, crud_account, crud_subcategory

router = APIRouter()

async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != settings.IPHONE_SHORTCUT_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )
        
def _map_transaction_to_response_schema(transaction: Any) -> TransactionInDB:
    """Helper to map ORM object to Pydantic schema, populating SubCategoryForTransaction."""
    if not transaction:
        return None
    
    subcategory_for_response = None
    if transaction.subcategory:
        parent_name = "N/A"
        if transaction.subcategory.parent_category: 
            parent_name = transaction.subcategory.parent_category.name
        
        subcategory_for_response = SubCategoryForTransaction(
            id=transaction.subcategory.id,
            name=transaction.subcategory.name,
            icon_name=transaction.subcategory.icon_name,
            parent_category_id=transaction.subcategory.parent_category_id,
            parent_category_name=parent_name
        )

    account_for_response = None
    if transaction.account:
        account_for_response = AccountForTransaction(
            id=transaction.account.id,
            name=transaction.account.name,
            account_type=transaction.account.account_type,
            account_last4=transaction.account.account_last4
        )

    return TransactionInDB(
        id=transaction.id,
        unique_hash=transaction.unique_hash,
        telegram_message_id=transaction.telegram_message_id,
        raw_sms_content=transaction.raw_sms_content,
        received_at=transaction.received_at,
        amount=transaction.amount,
        currency=transaction.currency,
        merchant_vpa=transaction.merchant_vpa,
        transaction_datetime_from_sms=transaction.transaction_datetime_from_sms,
        description=transaction.description,
        status=transaction.status.value if transaction.status else None, 
        account_id=transaction.account_id,
        subcategory_id=transaction.subcategory_id,
        exclude_from_cashflow=getattr(transaction, 'exclude_from_cashflow', False),
        account=account_for_response,
        subcategory=subcategory_for_response
    )
    

@router.post("/", response_model=TransactionInDB, dependencies=[Depends(verify_api_key)])
async def receive_sms(
    *,
    db: Session = Depends(deps.get_db),
    sms_in: SMSRecieved,
    background_tasks: BackgroundTasks,
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
        return _map_transaction_to_response_schema(existing_transaction)
    
        
    current_status = TransactionStatusManager.determine_initial_status(
        creation_data=final_parsed_data,
        db=db
    )

    final_parsed_data["status"] = current_status.value
    final_parsed_data["raw_sms_content"] = sms_in.sms_content
    final_parsed_data.setdefault('exclude_from_cashflow', False)    
    
    transaction_to_create = TransactionCreate(**final_parsed_data)
    
    
    print(f"Transation Data: {transaction_to_create}")
  
    try:
        db_transaction = crud_transaction.create_transaction(db=db, obj_in=transaction_to_create)
    except Exception as e:
        print(f"Error creating Pydantic TransactionCreate model or DB transaction: {e}")
        print(f"Data for creation: {transaction_to_create.dict()}")
        raise HTTPException(status_code=400, detail=f"Invalid transaction data: {str(e)}")
    
    transaction_with_relations = crud_transaction.get_transaction_by_hash(db, hash_str=db_transaction.unique_hash, include_relations=True)

    message_id = await telegram_notifier.send_new_transaction_notification(
        transaction=transaction_with_relations, 
        db=db
    )
    if message_id:
        crud_transaction.update_transaction_message_id(db, transaction_obj=transaction_with_relations, message_id=message_id)

    return _map_transaction_to_response_schema(transaction_with_relations)

@router.get(
    "/get/by-token",
    response_model=TransactionInDB,
    summary="Retrieve single transaction via token.",
)
def get_transaction_by_token(
    db: Session = Depends(deps.get_db),
    transaction_hash: str = Depends(deps.get_transaction_hash_from_token),
) -> Any:
    transaction = crud_transaction.get_transaction_by_hash(db=db, hash_str=transaction_hash, include_relations=True)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return _map_transaction_to_response_schema(transaction)



@router.get("/list", response_model=List[TransactionInDB])
def read_transactions(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    transactions_orm = crud_transaction.get_transactions(db, skip=skip, limit=limit, include_relations=True)
    return [_map_transaction_to_response_schema(tx) for tx in transactions_orm]

@router.get(
    "/get/{transaction_hash}", 
    response_model=TransactionInDB,
    summary="Retrieve single transaction.",
    dependencies=[Depends(verify_api_key)]
    )
def get_transaction_by_hash_api(
    transaction_hash: str,
    db: Session = Depends(deps.get_db),
) -> Any:
    transaction = crud_transaction.get_transaction_by_hash(db=db, hash_str=transaction_hash, include_relations=True)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return _map_transaction_to_response_schema(transaction)
    
def _update_transaction_logic(
    db: Session,
    transaction_hash: str,
    transaction_in: TransactionUpdate, 
    background_tasks: BackgroundTasks
) -> Any:
    
    db_transaction = crud_transaction.get_transaction_by_hash(db=db, hash_str=transaction_hash, include_relations=False)
    if not db_transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    if not transaction_in.dict(exclude_unset=True):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Request body is empty")

    update_data = transaction_in.dict(exclude_unset=True)
    
    print(update_data)
    
    # category_name logic is removed. Update is via subcategory_id.
    # Ensure subcategory_id, if provided, is valid (optional check here, or rely on FK constraint)
    if "subcategory_id" in update_data and update_data["subcategory_id"] is not None:
        if not crud_subcategory.get_subcategory(db=db, subcategory_id=update_data["subcategory_id"]):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"SubCategory with ID {update_data['subcategory_id']} not found.")
            
    if "account_id" in update_data and update_data["account_id"] is not None:
        if not crud_account.get_account(db=db, account_id=update_data["account_id"]):
             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Account with ID {update_data['account_id']} not found.")
    

    current_status = TransactionStatusManager.determine_status_for_update(
        transaction=db_transaction, 
        db=db,
        update_data=update_data
    )
    update_data["status"] = current_status.value 
        
    update_schema = TransactionUpdate(**update_data) 

    updated_transaction_orm = crud_transaction.update_transaction(
        db=db, db_obj=db_transaction, obj_in=update_schema
    )
    
    if updated_transaction_orm.telegram_message_id:
        background_tasks.add_task(
            telegram_notifier.edit_message_after_update,
            transaction=updated_transaction_orm,
            chat_id=int(settings.TELEGRAM_CHAT_ID),
            message_id=updated_transaction_orm.telegram_message_id,
            db=db
        )

    return _map_transaction_to_response_schema(updated_transaction_orm)

@router.patch(
    "/by-token",
    response_model=TransactionInDB,
    summary="Update a Transaction (Mini App)",
)
def update_transaction_by_token(
    *,
    db: Session = Depends(deps.get_db),
    background_tasks: BackgroundTasks,
    transaction_in: TransactionUpdate,
    transaction_hash: str = Depends(deps.get_transaction_hash_from_token)
) -> Any:
    """
    Update a transaction's description or other details via a secure token.
    This endpoint is intended for use by the Telegram Mini App.
    """
    return _update_transaction_logic(
        db=db, transaction_hash=transaction_hash, transaction_in=transaction_in, background_tasks=background_tasks
    )

@router.patch("/{transaction_hash}", response_model=TransactionInDB, dependencies=[Depends(verify_api_key)])
def update_transaction_details_api(
    *,
    db: Session = Depends(deps.get_db),
    transaction_hash: str,
    transaction_in: TransactionUpdate,
    background_tasks: BackgroundTasks,
) -> Any:
    """
    Update a transaction with enrichment data like an account or category.
    This endpoint is secured with an API key, intended for use by Shortcuts or trusted clients.
    """
    return _update_transaction_logic(
        db=db, transaction_hash=transaction_hash, transaction_in=transaction_in, background_tasks=background_tasks
    )