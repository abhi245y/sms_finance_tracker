from tests.sample_data.praser_result_model import ResultModel
from tests.sample_data.sms_samples import HDFC_CREDIT_CARD_SMS_DEBIT, HDFC_NETBANKING_DEBIT, INVALID_SMS


import datetime
class TestHDFCParser:
        
    def test_parse_valid_credit_transaction(self, hdfc_parser):
        result = ResultModel(hdfc_parser.parse(HDFC_CREDIT_CARD_SMS_DEBIT))
            
        assert result is not None
        assert result.account_num  == "2568"
        assert result.amount == 2475.94
        assert result.merchant == "PARAGON" 
        assert result.timestamp == datetime.datetime(2025, 6, 7, 19, 56, 35)
        assert result.merchant in result.description 
            
    def test_parse_valid_netbanking_transaction(self, hdfc_parser):
        result = ResultModel(hdfc_parser.parse(HDFC_NETBANKING_DEBIT))
            
        assert result is not None
        assert result.account_num  == "1675"
        assert result.amount == 1193.00
        assert result.merchant == "Thalappakatti Pattom Kerala TV01"
        assert result.timestamp == datetime.datetime(2025, 6, 1, 0, 0)
        assert result.merchant in result.description
        
    def test_parse_invalid_sms(self, hdfc_parser):
        result = hdfc_parser.parse(INVALID_SMS)
        assert result is None