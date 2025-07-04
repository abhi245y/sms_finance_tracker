from tests.sample_data.sms_samples import SBI_CREDIT_CARD_DEBIT, INVALID_SMS
from tests.sample_data.praser_result_model import ResultModel

import datetime


class TestSBIParser:
    
    def test_parser_upi_transaction(self, sbi_parser):
        result = ResultModel(sbi_parser.parse(SBI_CREDIT_CARD_DEBIT))
        
        assert result is not None
        assert result.account_num  == "0400"
        assert result.amount == 315
        assert result.merchant == "Kerala State Road Tran" 
        assert result.timestamp == datetime.datetime(2025, 6, 5, 0, 0)
        assert result.merchant in result.description 
        
    
    def test_paraser_invlaid_transaction(self, sbi_parser):
        result = sbi_parser.parse(INVALID_SMS)
        assert result is None