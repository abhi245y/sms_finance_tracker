from typing import Dict, Optional, Any
import re
from .base_parser import BaseParser

class OneCardParser(BaseParser):
    """Parses SMS from OneCard."""
    bank_name = "OneCard"

    def parse(self, sms_text: str) -> Optional[Dict[str, Any]]:
        pattern = re.compile(
            r"(?:paid a bill|made a rental payment)\s+for\s+Rs\.?\s*(?P<amount>[\d,]+\.\d{2})\s+(?:on|at)\s+(?P<merchant>.+?)\s+on\s+card\s+ending\s+XX(?P<card_last4>\d{4})",
            re.IGNORECASE
        )
    
        if (match := pattern.search(sms_text)):
            data = match.groupdict()
            return {
                "bank_name": self.bank_name,
                "account_last4": data['card_last4'],
                "amount": float(data['amount'].replace(",", "")),
                "currency": "INR",
                "merchant_vpa": data['merchant'].strip(),
                "transaction_datetime_from_sms": None, 
                "description": f"Spent at {data['merchant'].strip()}",
            }
        return None

