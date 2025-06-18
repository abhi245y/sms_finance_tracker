from fastapi import APIRouter, Depends, Request, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session
from typing import Any

from app.api import deps
from app.core.config import settings
from app.schemas.telegram import TelegramUpdate
from app.schemas.transaction import TransactionUpdate, TransactionStatus
from app.crud import crud_transaction 
from app.services import telegram_notifier
from app.services.transaction_status_manager import TransactionStatusManager

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
        action, unique_hash, value_str = callback_data.split(":")
    except (ValueError, IndexError):
        print(f"ERROR: Could not parse callback_data: {callback_data}")
        return {"ok": False, "error": "Invalid callback_data format"}

    db_transaction = crud_transaction.get_transaction_by_hash(db, hash_str=unique_hash, include_relations=False)
    if not db_transaction or not db_transaction.telegram_message_id:
        return {"ok": True}
    
    
    update_data = {}
    if action == "set_acc":
        update_data["account_id"] = int(value_str)
        current_status = TransactionStatusManager.determine_status_for_update(
            transaction=db_transaction, db=db, update_data=update_data
        )
        update_data["status"] = current_status.value
    elif action == "set_subcat": 
        update_data["subcategory_id"] = int(value_str)
        current_status = TransactionStatusManager.determine_status_for_update(
            transaction=db_transaction, db=db, update_data=update_data
        )
        update_data["status"] = current_status.value
    elif action == "sel_mod":
        try:
            new_status_enum = TransactionStatus[value_str.upper()]
            update_data["status"] = new_status_enum
        except KeyError:
            print(f"ERROR: Invalid status value for sel_mod: {value_str}")
            return {"ok": False, "error": "Invalid status value"}
    else:
        return {"ok": False, "error": "Unknown action"}
    
    update_schema = TransactionUpdate(**update_data)
    
    updated_transaction_orm = crud_transaction.update_transaction(
        db=db, db_obj=db_transaction, obj_in=update_schema
    ) # This will have relations loaded

    background_tasks.add_task(
        telegram_notifier.edit_message_after_update,
        transaction=updated_transaction_orm, # Pass the ORM object with relations
        chat_id=update.callback_query.message.chat.id,
        message_id=update.callback_query.message.message_id,
        db=db
    )
    
    return {"ok": True}