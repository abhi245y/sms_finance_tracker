from typing  import Dict

class ResultModel:
        
    def __init__(self, parased_data: Dict ):
        self._bank_name = parased_data["bank_name"]
        self._account_last4 = parased_data["account_last4"]
        self._amount = parased_data["amount"]
        self._merchant_vpa = parased_data["merchant_vpa"]
        self._transaction_datetime_from_sms = parased_data["transaction_datetime_from_sms"]
        self._description = parased_data["description"]
        
    @property
    def bank_name(self):
        return self._bank_name
        
    @property
    def account_num(self):
        return self._account_last4
        
    @property
    def amount(self):
        return self._amount
        
    @property
    def merchant(self):
        return self._merchant_vpa
        
    @property
    def timestamp(self):
        return self._transaction_datetime_from_sms
        
    @property
    def description(self):
        return self._description