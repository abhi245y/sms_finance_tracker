from typing import Dict, Optional, Any
import re
from .base_parser import BaseParser

class ICICIBankParser(BaseParser):
    bank_name = "ICICI Bank"
    def parse(self, sms_text: str) -> Optional[Dict[str, Any]]:

        parsers = [self._parse_card]
        for parser_func in parsers:
            if (result := parser_func(sms_text)):
                return result
        return None

    def _parse_card(self, sms_text: str) -> Optional[Dict[str, Any]]:
        pattern = re.compile(
        r"(?P<currency_symbol>INR|Rs)\s*(?P<amount>[\d,]+\.?\d*)\s*spent (?:on|using) ICICI Bank Card (?:XX|\*\*)(?P<card_last4>\d{4})\s*on\s*(?P<date>\d{1,2}-\w{3}-\d{2})\s*(?:on|at)\s*(?P<merchant>[^.]+?)\."
    )
        if (match := pattern.search(sms_text)):
            data = match.groupdict()
            parsed_datetime = self._parse_date(f"{data['date']}", ["%d-%b-%y", "%d-%B-%y"])
            return {
                "bank_name": self.bank_name,
                "account_last4": data['card_last4'],
                "amount": float(data["amount"].replace(",", "")),
                "merchant_vpa": data["merchant"].strip(),
                "transaction_datetime_from_sms": parsed_datetime,
                "description": f"Spent at {data['merchant'].strip()}",
            }
        return None 