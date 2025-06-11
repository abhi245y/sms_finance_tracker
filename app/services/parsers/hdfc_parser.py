from typing import Dict, Optional, Any
import re
from .base_parser import BaseParser

class HDFCParser(BaseParser):
    """Parses SMS from HDFC Bank (for Cards and UPI)."""
    bank_name = "HDFC Bank"

    def parse(self, sms_text: str) -> Optional[Dict[str, Any]]:
        parsers = [self._parse_card, self._parse_upi]
        for parser_func in parsers:
            if (result := parser_func(sms_text)):
                return result
        return None

    def _parse_card(self, sms_text: str) -> Optional[Dict[str, Any]]:
        pattern = re.compile(r"Spent Rs\.(?P<amount>[\d,]+\.?\d*)\s*On HDFC Bank Card (?P<card_last4>\d{4})\s*At\s*(?P<merchant>.+?)\s*On\s*(?P<date>\d{4}-\d{2}-\d{2}):(?P<time>\d{2}:\d{2}:\d{2})")
        if (match := pattern.search(sms_text)):
            data = match.groupdict()
            parsed_datetime = self._parse_date(f"{data['date']} {data['time']}", ["%Y-%m-%d %H:%M:%S"])
            return {
                "bank_name": self.bank_name,
                "account_last4": data['card_last4'],
                "amount": float(data["amount"].replace(",", "")),
                "merchant_vpa": data["merchant"].strip(),
                "transaction_datetime_from_sms": parsed_datetime,
                "description": f"Spent at {data['merchant'].strip()}",
            }
        return None

    def _parse_upi(self, sms_text: str) -> Optional[Dict[str, Any]]:
        pattern = re.compile(r"Amt Sent Rs\.(?P<amount>[\d,]+\.?\d*)\s*\nFrom HDFC Bank A/C \*(?P<account_last4>\d{4})\s*\nTo (?P<recipient>.+?)\s*\nOn (?P<date>\d{2}-\d{2})")
        if (match := pattern.search(sms_text)):
            data = match.groupdict()
            parsed_datetime = self._parse_date(data["date"], ["%d-%m"])
            return {
                "bank_name": self.bank_name,
                "account_last4": data['account_last4'],
                "amount": float(data["amount"].replace(",", "")),
                "merchant_vpa": data["recipient"].strip(),
                "transaction_datetime_from_sms": parsed_datetime,
                "description": f"UPI to {data['recipient'].strip()}",
            }
        return None
