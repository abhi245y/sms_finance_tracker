from .sample_data.sms_smaples import SBI_CREDIT_CARD_DEBIT, INVALID_SMS
from .sample_data.praser_result_model import ResultModel

import datetime


class TestclassSBIParser:
    
    def test_parser_upi_transaction(self, sbi_parser):
        result = ResultModel(sbi_parser.parse(SBI_CREDIT_CARD_DEBIT))
        
        assert result is not None
        assert result.account_num  == "4609"
        assert result.amount == 315
        assert result.merchant == "dummyBrand" 
        assert result.timestamp == datetime.datetime(2025, 5, 31, 17, 17)
        assert result.merchant in result.description 
        
    
    def test_paraser_invlaid_transaction(self, sbi_parser):
        result = ResultModel(sbi_parser.parse(INVALID_SMS))
        
        assert result is None