from typing import Dict, Optional, Any
import re
from .base_parser import BaseParser

class AmexParser(BaseParser):
    """Parses SMS from AMEX."""
    bank_name = "AMEX"

    def parse(self, sms_text: str) -> Optional[Dict[str, Any]]:
        pattern = re.compile(r"Alert:\s*You've spent (?P<currency_symbol>\$|INR)\s*(?P<amount>[\d,]+\.?\d*)\s*on your AMEX card\s+\*\*\s*(?P<card_last4>\d{4,5})\s*at\s*(?P<merchant>.+?)\s*on\s*(?P<date>\d{1,2}\s+\w+\s+\d{4})\s*at\s*(?P<time>\d{2}:\d{2}\s+(?:AM|PM))")
        
        if (match := pattern.search(sms_text)):
            data = match.groupdict()
            parsed_datetime = self._parse_date(f"{data['date']} {data['time']}", ["%d %B %Y %I:%M %p"])
            return {
                "bank_name": self.bank_name,
                "account_last4": data['card_last4'][-4:], 
                "amount": float(data["amount"].replace(",", "")),
                "currency": "USD" if data["currency_symbol"] == "$" else "INR",
                "merchant_vpa": data["merchant"].strip(),
                "transaction_datetime_from_sms": parsed_datetime,
                "description": f"Spent at {data['merchant'].strip()}",
            }
        return None
