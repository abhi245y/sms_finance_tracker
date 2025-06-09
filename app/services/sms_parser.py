import re
from datetime import datetime
from typing import Dict, Optional, Any, List, Callable

# --- Helper function to parse dates ---
def _parse_date(date_str: str, formats: List[str]) -> Optional[datetime]:
    """
    Tries to parse a date string using a list of possible formats.
    Handles %y (e.g., 25 -> 2025) and %d-%m (assumes current year).
    """
    for fmt in formats:
        try:
            dt_obj = datetime.strptime(date_str, fmt)
            
            # Handle 2-digit year (e.g., '25' becomes 2025)
            if '%y' in fmt and dt_obj.year < 2000: # strptime might parse '25' as 1925
                dt_obj = dt_obj.replace(year=dt_obj.year + 2000)
            
            # Handle formats like "dd-mm" assuming current year if strptime defaults to 1900
            if any(no_year_fmt in fmt for no_year_fmt in ["%d-%m", "%d/%m", "%m-%d", "%m/%d"]) \
               and dt_obj.year == 1900:
                dt_obj = dt_obj.replace(year=datetime.now().year)
                
            formatted_str = dt_obj.strftime("%Y-%m-%d %H:%M:%S")
            return datetime.strptime(formatted_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue
    return None

# --- Define parser functions for each bank/type ---

def _parse_federal_bank_upi(sms: str) -> Optional[Dict[str, Any]]:
    pattern = re.compile(
        r"Rs\s*(?P<amount>[\d,]+\.?\d*)\s*debited via UPI on\s*(?P<date>\d{2}-\d{2}-\d{4})\s*(?P<time>\d{2}:\d{2}:\d{2})\s*to VPA\s*(?P<vpa>[^.]+?)\.Ref No"
    )
    match = pattern.search(sms)
    if match:
        data = match.groupdict()
        datetime_str = f"{data['date']} {data['time']}"
        parsed_datetime = _parse_date(datetime_str, ["%d-%m-%Y %H:%M:%S"])
        return {
            "bank_name": "Federal Bank",
            "transaction_type": "UPI",
            "amount": float(data["amount"].replace(",", "")),
            "currency": "INR",
            "merchant_vpa": data["vpa"],
            "account_identifier": "Federal Bank UPI", # Actual account not in SMS, generic
            "transaction_datetime_from_sms": parsed_datetime if parsed_datetime else None,
            "description": f"UPI to {data['vpa']}",
        }
    return None

def _parse_pluxee_card(sms: str) -> Optional[Dict[str, Any]]:
    pattern = re.compile(
        r"Rs\.\s*(?P<amount>[\d,]+\.?\d*)\s*spent from Pluxee\s*(?:Meal\s*)?Card wallet, card no\.(?:xx|\*\*)?(?P<card_last4>\d{4})\s*on\s*(?P<date>\d{1,2}-\d{2}-\d{4})\s*(?P<time>\d{2}:\d{2}:\d{2})\s*at\s*(?P<merchant>[^.]+?)\s*\."
    )
    match = pattern.search(sms)
    if match:
        data = match.groupdict()
        datetime_str = f"{data['date']} {data['time']}"
        parsed_datetime = _parse_date(datetime_str, ["%d-%m-%Y %H:%M:%S", "%m-%d-%Y %H:%M:%S"]) 
        merchant = data["merchant"].strip()
        return {
            "bank_name": "Pluxee",
            "transaction_type": "Wallet",
            "amount": float(data["amount"].replace(",", "")),
            "currency": "INR",
            "merchant_vpa": merchant,
            "account_identifier": f"Pluxee Card xx{data['card_last4']}",
            "transaction_datetime_from_sms": parsed_datetime if parsed_datetime else None,
            "description": f"Spent at {merchant}",
        }
    return None

def _parse_idfc_first_bank_cc(sms: str) -> Optional[Dict[str, Any]]:
    pattern = re.compile(
        r"INR\s*(?P<amount>[\d,]+\.?\d*)\s*spent on your IDFC FIRST Bank Credit Card ending (?:XX|\*\*)(?P<card_last4>\d{4})\s*at\s*(?P<merchant>.+?)\s*on\s*(?P<date>\d{2}\s+\w{3}\s+\d{4})\s*at\s*(?P<time>\d{2}:\d{2}\s+(?:AM|PM))"
    )
    match = pattern.search(sms)
    if match:
        data = match.groupdict()
        datetime_str = f"{data['date']} {data['time']}"
        parsed_datetime = _parse_date(datetime_str, ["%d %b %Y %I:%M %p"])
        merchant = data["merchant"].strip()
        return {
            "bank_name": "IDFC FIRST Bank",
            "transaction_type": "Credit Card",
            "amount": float(data["amount"].replace(",", "")),
            "currency": "INR",
            "merchant_vpa": merchant,
            "account_identifier": f"IDFC CC XX{data['card_last4']}",
            "transaction_datetime_from_sms": parsed_datetime if parsed_datetime else None,
            "description": f"Spent at {merchant}",
        }
    return None

def _parse_hdfc_bank_upi(sms: str) -> Optional[Dict[str, Any]]:
    # Handles multi-line SMS. Using explicit \n for clarity.
    pattern = re.compile(
        r"Amt Sent Rs\.(?P<amount>[\d,]+\.?\d*)\s*\nFrom HDFC Bank A/C \*(?P<account_last4>\d{4})\s*\nTo (?P<recipient>.+?)\s*\nOn (?P<date>\d{2}-\d{2})"
    )
    match = pattern.search(sms)
    if match:
        data = match.groupdict()
        parsed_date = _parse_date(data["date"], ["%d-%m"]) # Assumes current year
        recipient = data["recipient"].strip()
        return {
            "bank_name": "HDFC Bank",
            "transaction_type": "UPI",
            "amount": float(data["amount"].replace(",", "")),
            "currency": "INR",
            "merchant_vpa": recipient,
            "account_identifier": f"HDFC A/C *{data['account_last4']}",
            "transaction_datetime_from_sms": parsed_date.strftime("%Y-%m-%d") if parsed_date else None, # Time not available
            "description": f"UPI to {recipient}",
        }
    return None

def _parse_icici_bank_card(sms: str) -> Optional[Dict[str, Any]]:
    pattern = re.compile(
        r"(?P<currency_symbol>INR|Rs)\s*(?P<amount>[\d,]+\.?\d*)\s*spent (?:on|using) ICICI Bank Card (?:XX|\*\*)(?P<card_last4>\d{4})\s*on\s*(?P<date>\d{1,2}-\w{3}-\d{2})\s*(?:on|at)\s*(?P<merchant>[^.]+?)\."
    )
    match = pattern.search(sms)
    if match:
        data = match.groupdict()
        parsed_date = _parse_date(data["date"], ["%d-%b-%y", "%d-%B-%y"]) # e.g., 30-May-25
        merchant = data["merchant"].strip()
        
        # Clean up common merchant prefixes/suffixes
        if merchant.startswith("IND*") and merchant.endswith(" -"):
            merchant = merchant[len("IND*"):-len(" -")].strip()
        elif merchant.startswith("IND*"):
            merchant = merchant[len("IND*"):].strip()

        return {
            "bank_name": "ICICI Bank",
            "transaction_type": "Credit Card", # Could be Debit or Credit
            "amount": float(data["amount"].replace(",", "")),
            "currency": "INR", # Based on INR or Rs
            "merchant_vpa": merchant,
            "account_identifier": f"ICICI Card XX{data['card_last4']}",
            "transaction_datetime_from_sms": parsed_date.strftime("%Y-%m-%d") if parsed_date else None, # Time not available
            "description": f"Spent at {merchant}",
        }
    return None

def _parse_federal_bank_netbanking(sms: str) -> Optional[Dict[str, Any]]:
    pattern = re.compile(
        r"Rs\.(?P<amount>[\d,]+\.?\d*)\s*debited from your A/c (?:XX|\*\*)(?P<account_last4>\d{4})\s*on\s*(?P<date>\d{2}\w{3}\d{4})\s*(?P<time>\d{2}:\d{2}:\d{2})"
    )
    match = pattern.search(sms)
    if match:
        data = match.groupdict()
        datetime_str = f"{data['date']} {data['time']}"
        parsed_datetime = _parse_date(datetime_str, ["%d%b%Y %H:%M:%S"]) # e.g., 08JUN2025
        return {
            "bank_name": "Federal Bank",
            "transaction_type": "Net Banking",
            "amount": float(data["amount"].replace(",", "")),
            "currency": "INR",
            "merchant_vpa": "FEDNET Transaction", # Merchant isn't specified, so use a generic name
            "account_identifier": f"Federal Bank A/c XX{data['account_last4']}",
            "transaction_datetime_from_sms": parsed_datetime,
            "description": "FEDNET Net Banking Debit",
        }
    return None

def _parse_hdfc_bank_card(sms: str) -> Optional[Dict[str, Any]]:
    pattern = re.compile(
        r"Spent Rs\.(?P<amount>[\d,]+\.?\d*)\s*On HDFC Bank Card (?P<card_last4>\d{4})\s*At\s*(?P<merchant>.+?)\s*On\s*(?P<date>\d{4}-\d{2}-\d{2}):(?P<time>\d{2}:\d{2}:\d{2})"
    )
    match = pattern.search(sms)
    if match:
        data = match.groupdict()
        datetime_str = f"{data['date']} {data['time']}"
        parsed_datetime = _parse_date(datetime_str, ["%Y-%m-%d %H:%M:%S"])
        merchant = data["merchant"].strip()
        return {
            "bank_name": "HDFC Bank",
            "transaction_type": "Credit Card",
            "amount": float(data["amount"].replace(",", "")),
            "currency": "INR",
            "merchant_vpa": merchant,
            "account_identifier": f"HDFC Bank Card {data['card_last4']}",
            "transaction_datetime_from_sms": parsed_datetime,
            "description": f"Spent at {merchant}",
        }
    return None

def _parse_amex_card(sms: str) -> Optional[Dict[str, Any]]:
    pattern = re.compile(
        r"spent (?P<currency_symbol>INR|\$)\s*(?P<amount>[\d,]+\.?\d*)\s*on your AMEX card \*\*\s*(?P<card_last4>\d{4})\s*at\s*(?P<merchant>.+?)\s*on\s*(?P<date>\d{1,2}\s+\w+\s+\d{4})\s*at\s*(?P<time>\d{2}:\d{2}\s+(?:AM|PM))"
    )
    match = pattern.search(sms)
    if match:
        data = match.groupdict()
        datetime_str = f"{data['date']} {data['time']}"
        parsed_datetime = _parse_date(datetime_str, ["%d %B %Y %I:%M %p"])
        merchant = data["merchant"].strip()
        currency = "USD" if data["currency_symbol"] == "$" else "INR"
        return {
            "bank_name": "AMEX",
            "transaction_type": "Credit Card",
            "amount": float(data["amount"].replace(",", "")),
            "currency": currency,
            "merchant_vpa": merchant,
            "account_identifier": f"AMEX Card ** {data['card_last4']}",
            "transaction_datetime_from_sms": parsed_datetime,
            "description": f"Spent at {merchant}",
        }
    return None

def _parse_sbi_credit_card(sms: str) -> Optional[Dict[str, Any]]:
    pattern = re.compile(
        r"Rs\.(?P<amount>[\d,]+\.?\d*)\s*spent on your SBI Credit Card ending (?P<card_last4>\d{4})\s*at\s*(?P<merchant>.+?)\s*on\s*(?P<date>\d{2}/\d{2}/\d{2})"
    )
    match = pattern.search(sms)
    if match:
        data = match.groupdict()
        parsed_datetime = _parse_date(data["date"], ["%d/%m/%y"])
        merchant = data["merchant"].strip()
        return {
            "bank_name": "SBI",
            "transaction_type": "Credit Card",
            "amount": float(data["amount"].replace(",", "")),
            "currency": "INR",
            "merchant_vpa": merchant,
            "account_identifier": f"SBI Credit Card {data['card_last4']}",
            "transaction_datetime_from_sms": parsed_datetime, # No time info available
            "description": f"Spent at {merchant}",
        }
    return None

# --- Main parser function ---
_SPENDING_PARSERS: List[Callable[[str], Optional[Dict[str, Any]]]] = [
    _parse_idfc_first_bank_cc,
    _parse_icici_bank_card,
    _parse_hdfc_bank_upi,
    _parse_federal_bank_upi,
    _parse_pluxee_card,
    _parse_federal_bank_netbanking,
    _parse_hdfc_bank_card,
    _parse_amex_card,
    _parse_sbi_credit_card,
]

_CREDIT_KEYWORDS = [ "credited to your A/c", "credited to Acct", "received", "deposited" ]

def parse_sms_content(sms_content: str) -> Optional[Dict[str, Any]]:
    """
    Parses SMS content to extract transaction details.
    Prioritizes spending transactions and tries to identify details from known bank formats.
    Returns a dictionary with parsed data or None if it's a credit or unparseable.
    """
    # 1. Filter out credit/income transactions
    for keyword in _CREDIT_KEYWORDS:
        if keyword.lower() in sms_content.lower():
            # print(f"DEBUG: Ignoring credit transaction: {sms_content[:70]}...")
            return None 

    # 2. Try specific bank/type parsers for spending
    for parser_func in _SPENDING_PARSERS:
        parsed_data = parser_func(sms_content)
        if parsed_data:
            # Add raw SMS and ensure essential fields have defaults if not set by parser
            parsed_data["raw_sms"] = sms_content
            parsed_data.setdefault("currency", "INR") # Should be set by parsers, but as a fallback
            parsed_data.setdefault("bank_name", "Unknown")
            parsed_data.setdefault("transaction_type", "Unknown")
            parsed_data.setdefault("account_identifier", "Unknown")
            parsed_data.setdefault("merchant_vpa", "Unknown")
            parsed_data.setdefault("transaction_datetime_from_sms", "Unknown")
            print(f"DEBUG: Parsed by {parser_func.__name__}")
            return parsed_data

    # 3. Optional: Fallback to a very generic parser if no specific one matched
    # For now, we'll skip a noisy generic fallback. If an SMS is a spend but not parsed,
    # it's better to explicitly add a parser for it.
    
    print(f"DEBUG: Could not parse as spend: {sms_content[:70]}...")
    return None