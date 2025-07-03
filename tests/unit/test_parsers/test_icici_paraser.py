from .sample_data.sms_smaples import ICICI_CRDIT_CARD_DEBIT, INVALID_SMS
from .sample_data.praser_result_model import ResultModel

import datetime


class TestFederalBankParser:
    
    def test_parser_upi_transaction(self, icici_parser):
        result = ResultModel(icici_parser.parse(ICICI_CRDIT_CARD_DEBIT))
        
        assert result is not None
        assert result.account_num  == "7007"
        assert result.amount == 862.00
        assert result.merchant == "IND*Amazon.in" 
        assert result.timestamp == datetime.datetime(2025, 6, 4, 12, 17, 5)
        assert result.merchant in result.description 
        
    
    def test_paraser_invlaid_transaction(self, icici_parser):
        result = ResultModel(icici_parser.parse(INVALID_SMS))
        
        assert result is None