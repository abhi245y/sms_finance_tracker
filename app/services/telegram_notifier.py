import httpx
from typing import Optional
from sqlalchemy.orm import Session
import enum

from app.core.config import settings
from app.core.security import create_mini_app_access_token 
from app.schemas.transaction import TransactionInDB
from app.models.transaction import TransactionStatus
from app.crud import crud_account

from app.services.budget_service import get_remaining_spend_power


API_BASE_URL = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}"

class TransactionType(str, enum.Enum):
    NEW = "New Transaction Captured"
    UPDATED = "Transaction UPDATED"

async def send_message(text: str, reply_markup: Optional[dict] = None) -> Optional[int]:
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
            response_data = response.json()
            if response_data.get("ok"):
                return response_data["result"]["message_id"]
            
        except httpx.HTTPStatusError as e:
            print(f"ERROR sending Telegram message: {e.response.text}")
        except Exception as e:
            print(f"ERROR during Telegram notification: {e}")
            
        return None

def _format_transaction_message(transaction: TransactionInDB, type_str: TransactionType, db: Session) -> str:
    """Formats a transaction object into a nice string for Telegram."""
    def escape_md(text: str) -> str:
        escape_chars = r'_*[]()~`>#+-=|{}.!'
        return "".join(f"\\{char}" if char in escape_chars else char for char in str(text))

    amount_str = escape_md(f"{transaction.amount:.2f} {transaction.currency}")
    merchant = escape_md(transaction.merchant_vpa or "Unknown Merchant")
    
    budget_line = ""
    summary = get_remaining_spend_power(db) 
    if summary:
        remaining_str = escape_md(f"₹{summary['remaining']:,.0f}")
        budget_str = escape_md(f"₹{summary['budget']:,.0f}")
        
        percentage = 0
        if summary['budget'] > 0:
            percentage = (summary['spent'] / summary['budget']) * 100
        
        progress_blocks = int(percentage / 10)
        progress_bar = ("█" * progress_blocks) + ("░" * (10 - progress_blocks))

        budget_line = (
            f"\n\n*💰 Spend Power*:\n"
            f"`{remaining_str} / {budget_str} Left`\n"
            f"`[{progress_bar}] {percentage:.0f}% Used`"
        )
    
    account_name = "⚠️ *Not Set*"
    if transaction.account:
        account_name = escape_md(transaction.account.name)

    subcategory_display_name  = "⚠️ *Not Set*"
    if transaction.subcategory:
        parent_name = transaction.subcategory.parent_category.name if transaction.subcategory.parent_category else ""
        subcategory_display_name = escape_md(
            f"{transaction.subcategory.name} ({parent_name})" if parent_name else transaction.subcategory.name
        )

    status_emoji_map = { 
        TransactionStatus.PROCESSED: "✅",
        TransactionStatus.PENDING_CATEGORIZATION: "🏷️",
        TransactionStatus.PENDING_ACCOUNT_SELECTION: "🏦",
        TransactionStatus.PENDING_PROCESSING:"🚧",
        TransactionStatus.ERROR: "❌",
        TransactionStatus.FAILED: "💀",
        TransactionStatus.CANCELLED: "🚫"
    }
    status_emoji = status_emoji_map.get(transaction.status, "⚙️") 
    status_text = escape_md(transaction.status.value.replace('_', ' ').title()) 
    
    description_text = escape_md(transaction.description or "_No description_")
    
    message = (
            f"*{status_emoji} {escape_md(type_str.value)}*\n\n" 
            f"*Amount*: `{amount_str}`\n"
            f"*Merchant*: {merchant}\n"
            f"*Account*: {account_name}\n"
            f"*Category*: {subcategory_display_name}\n" 
            f"*Description*: {description_text}\n"
            f"*Status*: {status_text}"
            f"{budget_line}" 
        )
    return message

def _build_inline_keyboard(transaction: TransactionInDB, db: Session) -> Optional[dict]:
    """Builds an interactive keyboard based on the transaction's status."""
    buttons = []
    mini_app_access_token = create_mini_app_access_token(transaction_hash=transaction.unique_hash)
    mini_app_url = f"{settings.MINI_APP_BASE_URL}/edit-transaction?token={mini_app_access_token}"
    
    if transaction.status == TransactionStatus.PROCESSED:
        buttons.append([{"text": "✏️ Edit Details (App)", "web_app": {"url": mini_app_url}}])
    
    elif transaction.status == TransactionStatus.PENDING_PROCESSING:
        buttons.append([{"text": "🏦 Select Account", "callback_data": f"sel_mod:{transaction.unique_hash}:{TransactionStatus.PENDING_ACCOUNT_SELECTION.value}"}])
        buttons.append([{"text": "🏷️ Select Category (App)", "web_app": {"url": mini_app_url}}])

    elif transaction.status == TransactionStatus.PENDING_ACCOUNT_SELECTION:
        accounts = crud_account.get_accounts(db, limit=5)
        for acc in accounts:
            buttons.append([{"text": f"{acc.name}", "callback_data": f"set_acc:{transaction.unique_hash}:{acc.id}"}])
        if len(accounts) >= 5: 
             buttons.append([{"text": "🏦 More Accounts (App)", "web_app": {"url": mini_app_url}}])

    elif transaction.status == TransactionStatus.PENDING_CATEGORIZATION:
        buttons.append([{"text": "🏷️ Select Category (App)", "web_app": {"url": mini_app_url}}])
        
    if transaction.status != TransactionStatus.PROCESSED:
        found_edit_button = any("Edit Details (App)" in row[0]["text"] for row in buttons if row)
        if not found_edit_button:
             buttons.append([{"text": "📲 Open in App", "web_app": {"url": mini_app_url}}])


    return {"inline_keyboard": buttons} if buttons else None 

async def send_new_transaction_notification(transaction: TransactionInDB, db: Session):
    """The main function to call from an endpoint."""
    message_text = _format_transaction_message(transaction, TransactionType.NEW, db)
    keyboard = _build_inline_keyboard(transaction, db)
    return await send_message(text=message_text, reply_markup=keyboard)

async def send_update_notification(transaction: TransactionInDB, db: Session):
    """Sends a simpler notification when a transaction is updated."""
    message_text = _format_transaction_message(transaction, TransactionType.UPDATED)
    keyboard = _build_inline_keyboard(transaction, db)
    await send_message(text=message_text, reply_markup=keyboard)
    
async def edit_message_after_update(transaction: TransactionInDB, chat_id: int, message_id: int, db: Session):
    """Edits an existing Telegram message to reflect the updated transaction state."""
    new_text = _format_transaction_message(transaction, TransactionType.UPDATED, db)
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