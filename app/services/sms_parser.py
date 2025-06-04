import re
from typing import Dict, Optional, Any

def parse_sms_content(sms_content: str) -> Dict[str, Any]:
    """
    Very basic initial SMS parser.
    This needs to be significantly improved with more specific regex for bank SMS formats.
    """
    parsed_data = {"raw_sms": sms_content}

    # Attempt to find amount (very naive)
    # Look for "Rs." or "INR" followed by a number
    # Example: "Rs.1,234.56", "INR 500", "Rs 23.00"
    amount_match = re.search(r"(?:Rs\.?|INR)\s*([\d,]+\.?\d*)", sms_content, re.IGNORECASE)
    if amount_match:
        try:
            amount_str = amount_match.group(1).replace(",", "")
            parsed_data["amount"] = float(amount_str)
            parsed_data["currency"] = "INR" # Assume INR if keyword found
        except ValueError:
            pass 

    # Attempt to find a simple description (e.g., "spent at MERCHANT_NAME")
    # This is highly dependent on SMS format
    spent_at_match = re.search(r"(?:spent at|debited for purchase at)\s+([\w\s.-]+?)(?:\son\s|$|\.)", sms_content, re.IGNORECASE)
    if spent_at_match:
        parsed_data["description"] = f"Spent at {spent_at_match.group(1).strip()}"
    else:
        # Fallback or more generic description
        first_sentence = sms_content.split('.')[0]
        parsed_data["description"] = first_sentence[:100] # Truncate if too long

    # Add more parsing logic here for card numbers, account numbers, UPI IDs, etc.
    # E.g., look for "A/c XXXXX1234", "Card XX1234"

    return parsed_data
