import httpx
from typing import Optional
from sqlalchemy.orm import Session
import enum

from app.core.config import settings
from app.schemas.transaction import TransactionInDB
from app.models.transaction import TransactionStatus
from app.crud import crud_category, crud_account


API_BASE_URL = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}"

class TransactionType(str, enum.Enum):
    NEW = "New Transaction Captured"
    UPDATED = "Transaction UPDATED"

async def send_message(text: str, reply_markup: Optional[dict] = None):
    """A simple async function to send a message using httpx."""
    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHAT_ID:
        print("WARN: Telegram credentials not set. Skipping notification.")
        return

    async with httpx.AsyncClient() as client:
        payload = {
            "chat_id": settings.TELEGRAM_CHAT_ID,
            "text": text,
            "parse_mode": "MarkdownV2",
        }
        if reply_markup:
            payload["reply_markup"] = reply_markup

        try:
            response = await client.post(f"{API_BASE_URL}/sendMessage", json=payload)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            print(f"ERROR sending Telegram message: {e.response.text}")
        except Exception as e:
            print(f"ERROR during Telegram notification: {e}")

def _format_transaction_message(transaction: TransactionInDB, type: TransactionType) -> str:
    """Formats a transaction object into a nice string for Telegram."""
    # Helper to escape MarkdownV2 characters
    def escape_md(text: str) -> str:
        escape_chars = r'_*[]()~`>#+-=|{}.!'
        return "".join(f"\\{char}" if char in escape_chars else char for char in str(text))

    amount_str = escape_md(f"{transaction.amount:.2f} {transaction.currency}")
    merchant = escape_md(transaction.merchant_vpa or "Unknown Merchant")
    
    account_name = "⚠️ *Not Set*"
    if transaction.account:
        account_name = escape_md(transaction.account.name)

    category_name = "⚠️ *Not Set*"
    if transaction.category_obj:
        category_name = escape_md(transaction.category_obj.name)

    status_emoji = {
        TransactionStatus.PROCESSED: "✅",
        TransactionStatus.PENDING_CATEGORIZATION: "🏷️",
        TransactionStatus.PENDING_ACCOUNT_SELECTION: "🏦",
        TransactionStatus.ERROR: "❌"
    }.get(transaction.status, "⚙️")
    status_text = escape_md(transaction.status.replace('_', ' ').title())

    # Construct the message using MarkdownV2
    message = (
        f"*{status_emoji} {type}*\n\n"
        f"*Amount*: `{amount_str}`\n"
        f"*Merchant*: {merchant}\n"
        f"*Account*: {account_name}\n"
        f"*Category*: {category_name}\n"
        f"*Status*: {status_text}"
    )
    return message

def _build_inline_keyboard(transaction: TransactionInDB, db: Session) -> Optional[dict]:
    """Builds an interactive keyboard based on the transaction's status."""
    buttons = []
    if transaction.status == TransactionStatus.PENDING_ACCOUNT_SELECTION:
        accounts = crud_account.get_accounts(db, limit=20)
        for acc in accounts:
            callback_data = f"set_acc:{transaction.unique_hash}:{acc.id}"
            buttons.append([{"text": f"Set Account: {acc.name}", "callback_data": callback_data}])
    
    if transaction.status == TransactionStatus.PENDING_CATEGORIZATION:
        categories = crud_category.get_categories(db, limit=20)
        for cat in categories:
            callback_data = f"set_cat:{transaction.unique_hash}:{cat.id}"
            buttons.append([{"text": f"Set Category: {cat.name}", "callback_data": callback_data}])

    if not buttons:
        return {"inline_keyboard": []} 
        
    return {"inline_keyboard": buttons}

async def send_new_transaction_notification(transaction: TransactionInDB, db: Session):
    """The main function to call from an endpoint."""
    message_text = _format_transaction_message(transaction, TransactionType.NEW)
    keyboard = _build_inline_keyboard(transaction, db)
    await send_message(text=message_text, reply_markup=keyboard)

async def send_update_notification(transaction: TransactionInDB, db: Session):
    """Sends a simpler notification when a transaction is updated."""
    message_text = _format_transaction_message(transaction, TransactionType.UPDATED)
    keyboard = _build_inline_keyboard(transaction, db)
    await send_message(text=message_text, reply_markup=keyboard)
    
async def edit_message_after_update(transaction: TransactionInDB, chat_id: int, message_id: int, db: Session):
    """Edits an existing Telegram message to reflect the updated transaction state."""
    new_text = _format_transaction_message(transaction, TransactionType.UPDATED)
    keyboard = _build_inline_keyboard(transaction, db)
    async with httpx.AsyncClient() as client:
        payload = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": new_text,
            "parse_mode": "MarkdownV2",
            "reply_markup": keyboard
        }
        try:
            await client.post(f"{API_BASE_URL}/editMessageText", json=payload)
        except httpx.HTTPStatusError as e:
            print(f"INFO: Could not edit Telegram message (this is often okay): {e.response.text}")