from typing import Dict, Optional, Any
import re
from .base_parser import BaseParser

class IDFCFirstBankParser(BaseParser):
    bank_name = "IDFC FIRST Bank"
    def parse(self, sms_text: str) -> Optional[Dict[str, Any]]:

        parsers = [self._parse_card]
        for parser_func in parsers:
            if (result := parser_func(sms_text)):
                return result
        return None

    def _parse_card(self, sms_text: str) -> Optional[Dict[str, Any]]:
        pattern = re.compile(r"INR\s*(?P<amount>[\d,]+\.?\d*)\s*spent on your IDFC FIRST Bank Credit Card ending (?:XX|\*\*)(?P<card_last4>\d{4})\s*at\s*(?P<merchant>.+?)\s*on\s*(?P<date>\d{2}\s+\w{3}\s+\d{4})\s*at\s*(?P<time>\d{2}:\d{2}\s+(?:AM|PM))")
        if (match := pattern.search(sms_text)):
            data = match.groupdict()
            parsed_datetime = self._parse_date(f"{data['date']} {data['time']}", ["%d %b %Y %I:%M %p"])
            return {
                "bank_name": self.bank_name,
                "account_last4": data['card_last4'],
                "amount": float(data["amount"].replace(",", "")),
                "merchant_vpa": data["merchant"].strip(),
                "transaction_datetime_from_sms": parsed_datetime,
                "description": f"Spent at {data['merchant'].strip()}",
            }
        return None 