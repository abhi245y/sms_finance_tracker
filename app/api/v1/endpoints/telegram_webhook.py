from fastapi import APIRouter, Depends, Request, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session
from typing import Any

from app.api import deps
from app.core.config import settings
from app.schemas.telegram import TelegramUpdate
from app.schemas.transaction import TransactionUpdate
from app.crud import crud_transaction
from app.services import telegram_notifier

router = APIRouter()

@router.post("/webhook")
async def telegram_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    This endpoint is set as the webhook for the Telegram bot.
    It receives all updates from Telegram, but we only care about callback_queries.
    """
    data = await request.json()
    update = TelegramUpdate.parse_obj(data)

    if not update.callback_query or not update.callback_query.data:
        # This update is not a button press we care about, ignore it.
        return {"ok": True}

    if update.callback_query.message.chat.id != int(settings.TELEGRAM_CHAT_ID):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized chat")

    callback_data = update.callback_query.data
    # callback_data is formatted as "action:hash:value"
    # e.g., "set_cat:some_hash_string:5"
    try:
        action, unique_hash, value = callback_data.split(":")
        value_id = int(value)
    except (ValueError, IndexError):
        print(f"ERROR: Could not parse callback_data: {callback_data}")
        return {"ok": False, "error": "Invalid callback_data format"}

    # Fetch the transaction using the hash from the callback data
    db_transaction = crud_transaction.get_transaction_by_hash(db, hash_str=unique_hash)
    if not db_transaction:
        return {"ok": True}
        
    update_data = {}
    if action == "set_acc":
        update_data["account_id"] = value_id
    elif action == "set_cat":
        update_data["category_id"] = value_id
    else:
        return {"ok": False, "error": "Unknown action"}
        
    # Use the same logic as the PATCH endpoint to update the transaction
    from app.models.transaction import TransactionStatus
    
    has_account = db_transaction.account_id is not None or "account_id" in update_data
    has_category = db_transaction.category_id is not None or "category_id" in update_data
    
    if not has_account:
        current_status = TransactionStatus.PENDING_ACCOUNT_SELECTION
    elif not has_category:
        current_status = TransactionStatus.PENDING_CATEGORIZATION
    else:
        current_status = TransactionStatus.PROCESSED
    
    update_data["status"] = current_status.value
    
    update_schema = TransactionUpdate(**update_data)
    updated_transaction = crud_transaction.update_transaction(
        db=db, db_obj=db_transaction, obj_in=update_schema
    )

    background_tasks.add_task(
        telegram_notifier.edit_message_after_update,
        transaction=updated_transaction,
        chat_id=update.callback_query.message.chat.id,
        message_id=update.callback_query.message.message_id,
        db=db
    )
    
    return {"ok": True}