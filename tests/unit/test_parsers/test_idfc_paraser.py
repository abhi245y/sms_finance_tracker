from tests.sample_data.sms_samples import IDFC_CREDIT_CARD_DEBIT, INVALID_SMS
from tests.sample_data.praser_result_model import ResultModel

import datetime


class TestIDFCFirstBankParser:
    
    def test_parser_upi_transaction(self, idfc_parser):
        result = ResultModel(idfc_parser.parse(IDFC_CREDIT_CARD_DEBIT))
        
        assert result is not None
        assert result.account_num  == "4609"
        assert result.amount == 1110.00
        assert result.merchant == "dummyBrand" 
        assert result.timestamp == datetime.datetime(2025, 5, 31, 17, 17)
        assert result.merchant in result.description 
        
    
    def test_paraser_invlaid_transaction(self, idfc_parser):
        result = idfc_parser.parse(INVALID_SMS)
        assert result is None