from .sample_data.sms_smaples import AMEX_DEBIT, INVALID_SMS
from .sample_data.praser_result_model import ResultModel

import datetime


class TestAmexParaser:
    
    def test_parser_card_transaction(self, amex_parser):
        result = ResultModel(amex_parser.parse(AMEX_DEBIT))
        
        assert result is not None
        assert result.account_num  == "1004"
        assert result.amount == 2067.98
        assert result.merchant == "LULU HYPERMA" 
        assert result.timestamp == datetime.datetime(2025, 6, 5, 20, 36)
        assert result.merchant in result.description 
    
    def test_paraser_invlaid_transaction(self, amex_parser):
        result = ResultModel(amex_parser.parse(INVALID_SMS))
        
        assert result is None