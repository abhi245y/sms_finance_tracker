from tests.sample_data.sms_samples import ICICI_CRDIT_CARD_DEBIT, INVALID_SMS
from tests.sample_data.praser_result_model import ResultModel

import datetime


class TestFederalBankParser:
    
    def test_parser_upi_transaction(self, icici_parser):
        result = ResultModel(icici_parser.parse(ICICI_CRDIT_CARD_DEBIT))
        
        assert result is not None
        assert result.account_num  == "7007"
        assert result.amount == 862.00
        assert result.merchant == "IND*Amazon" 
        assert result.timestamp == datetime.datetime(2025, 5, 30, 0, 0)
        assert result.merchant in result.description 
        
    
    def test_paraser_invlaid_transaction(self, icici_parser):
        result = icici_parser.parse(INVALID_SMS)
        assert result is None