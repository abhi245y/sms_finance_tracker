from typing import Dict, Optional, Any, List
from datetime import datetime
from abc import ABC, abstractmethod

class BaseParser(ABC):
    """
    Abstract Base Class for all bank/service parsers.
    Each subclass is responsible for parsing SMS messages from a specific source.
    """
    @abstractmethod
    def parse(self, sms_text: str) -> Optional[Dict[str, Any]]:
        """
        If the parser can handle the SMS, it returns a dict of parsed data.
        The dictionary must include 'bank_name' and 'account_last4'.
        Otherwise, it returns None.
        """
        raise NotImplementedError

    def _parse_date(self, date_str: str, formats: List[str]) -> Optional[datetime]:
        """
        A reusable helper method to parse date strings.
        It's placed in the BaseParser so all subclasses can use it.
        """
        for fmt in formats:
            try:
                dt_obj = datetime.strptime(date_str, fmt)
                if '%y' in fmt and dt_obj.year < 2000:
                    dt_obj = dt_obj.replace(year=dt_obj.year + 2000)
                if any(f in fmt for f in ["%d-%m", "%d/%m"]) and dt_obj.year == 1900:
                    dt_obj = dt_obj.replace(year=datetime.now().year)
                return dt_obj
            except ValueError as e:
                print(e)
                continue
            
        return None
