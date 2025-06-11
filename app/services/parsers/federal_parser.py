from typing import Dict, Optional, Any
import re
from .base_parser import BaseParser

class FederalBankParser(BaseParser):
    """Parses SMS from Federal Bank (for UPI and Netbanking)."""
    bank_name = "Federal Bank"

    def parse(self, sms_text: str) -> Optional[Dict[str, Any]]:
        parsers = [self._parse_netbanking, self._parse_upi]
        for parser_func in parsers:
            if (result := parser_func(sms_text)):
                return result
        return None

    def _parse_upi(self, sms_text: str) -> Optional[Dict[str, Any]]:
        """Parses UPI transactions which DO NOT include the account number."""
        if self.bank_name not in sms_text:
            return None
        
        pattern = re.compile(r"Rs\s*(?P<amount>[\d,]+\.?\d*)\s*debited via UPI on\s*(?P<date>\d{2}-\d{2}-\d{4})\s*(?P<time>\d{2}:\d{2}:\d{2})\s*to VPA\s*(?P<vpa>[^.]+?)\.Ref No")

        if (match := pattern.search(sms_text)):
            data = match.groupdict()
            parsed_datetime = self._parse_date(f"{data['date']} {data['time']}", ["%d-%m-%Y %H:%M:%S"])
            return {
                "bank_name": self.bank_name,
                "account_last4": "0000", 
                "amount": float(data["amount"].replace(",", "")),
                "merchant_vpa": data["vpa"],
                "transaction_datetime_from_sms": parsed_datetime,
                "description": f"UPI to {data['vpa']}",
            }
        return None

    def _parse_netbanking(self, sms_text: str) -> Optional[Dict[str, Any]]:
        """Parses FEDNET transactions which include the account number."""
        pattern = re.compile(r"Rs\.(?P<amount>[\d,]+\.?\d*)\s*debited from your A/c XX(?P<account_last4>\d{4})\s*on\s*(?P<date>\d{2}\w{3}\d{4})\s*(?P<time>\d{2}:\d{2}:\d{2})")
        if (match := pattern.search(sms_text)):
            data = match.groupdict()
            parsed_datetime = self._parse_date(f"{data['date']} {data['time']}", ["%d%b%Y %H:%M:%S"])
            return {
                "bank_name": self.bank_name,
                "account_last4": data['account_last4'],
                "amount": float(data["amount"].replace(",", "")),
                "merchant_vpa": "FEDNET Transaction",
                "transaction_datetime_from_sms": parsed_datetime,
                "description": "FEDNET Net Banking Debit",
            }
        return None
