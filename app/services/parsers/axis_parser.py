from typing import Dict, Optional, Any
import re
from .base_parser import BaseParser

class AXISParser(BaseParser):
    """Parses SMS from AXIS."""
    bank_name = "AXIS"

    def parse(self, sms_text: str) -> Optional[Dict[str, Any]]:
        pattern = re.compile(
            r"Spent\s+Card\s+no\.\s+XX(?P<card_last4>\d{4})\s+INR\s+(?P<amount>[\d,]+(?:\.\d+)?)\s+(?P<date>\d{2}-\d{2}-\d{2})\s+(?P<time>\d{2}:\d{2}:\d{2})\s+(?P<merchant>[A-Z0-9\s&\.\-]+)",
            re.IGNORECASE
        )

        if (match := pattern.search(sms_text)):
            data = match.groupdict()
            parsed_datetime = self._parse_date(
                f"{data['date']} {data['time']}",
                ["%d-%m-%y %H:%M:%S"]
            )
            return {
                "bank_name": self.bank_name,
                "account_last4": data["card_last4"],
                "amount": float(data["amount"].replace(",", "")),
                "currency": "INR",
                "merchant_vpa": data["merchant"].strip(),
                "transaction_datetime_from_sms": parsed_datetime,
                "description": f"Spent at {data['merchant'].strip()}",
            }
        return None

