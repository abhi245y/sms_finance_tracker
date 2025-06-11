import hashlib
from typing import Dict, Any, Optional
from datetime import datetime

def generate_transaction_hash(parsed_data: Dict[str, Any]) -> Optional[str]:
    """
    Generates a unique, recreatable SHA256 hash for a transaction.
    
    The hash is based on the most stable components of a transaction:
    - Transaction Datetime (normalized to ISO 8601 format)
    - Amount (formatted to 2 decimal places)
    - Account ID
    - Merchant/VPA (normalized to lowercase)
    """
    try:
        tx_datetime: Optional[datetime] = parsed_data.get("transaction_datetime_from_sms")
        amount: Optional[float] = parsed_data.get("amount")
        account_id: Optional[int] = parsed_data.get("account_id")
        merchant: Optional[str] = parsed_data.get("merchant_vpa")

        if not tx_datetime or amount is None:
            return None
        
        datetime_str = tx_datetime.strftime('%Y-%m-%dT%H:%M:%S')

        amount_str = f"{amount:.2f}"

        merchant_str = str(merchant).lower().strip() if merchant else "none"

        # Use account_id if available, otherwise fall back to bank_name for ambiguous transactions
        # This requires the ParserEngine to pass bank_name through.
        identifier_str = str(account_id) if account_id is not None else str(parsed_data.get("bank_name", "unknown_bank")).lower()

        stable_string = f"{datetime_str}|{amount_str}|{identifier_str}|{merchant_str}"
        
        print(f"DEBUG: Generating hash from stable string: \"{stable_string}\"")

        hasher = hashlib.sha256()
        hasher.update(stable_string.encode('utf-8'))
        return hasher.hexdigest()

    except Exception as e:
        print(f"ERROR: Could not generate transaction hash. Error: {e}")
        return None