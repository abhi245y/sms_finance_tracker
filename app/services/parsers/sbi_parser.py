from typing import Dict, Optional, Any
import re
from .base_parser import BaseParser

class SBIParser(BaseParser):
    """Parses SMS from SBI."""
    bank_name = "SBI"

    def parse(self, sms_text: str) -> Optional[Dict[str, Any]]:
        # This one parser can handle both card and potentially other SBI messages if patterns are added.
        return self._parse_credit_card(sms_text)

    def _parse_credit_card(self, sms_text: str) -> Optional[Dict[str, Any]]:
        pattern = re.compile(r"Rs\.(?P<amount>[\d,]+\.?\d*)\s*spent on your SBI Credit Card ending (?P<card_last4>\d{4})\s*at\s*(?P<merchant>.+?)\s*on\s*(?P<date>\d{2}/\d{2}/\d{2})")
        if (match := pattern.search(sms_text)):
            data = match.groupdict()
            parsed_datetime = self._parse_date(data["date"], ["%d/%m/%y"])
            return {
                "bank_name": self.bank_name,
                "account_last4": data['card_last4'],
                "amount": float(data["amount"].replace(",", "")),
                "merchant_vpa": data["merchant"].strip(),
                "transaction_datetime_from_sms": parsed_datetime,
                "description": f"Spent at {data['merchant'].strip()}",
            }
        return None
