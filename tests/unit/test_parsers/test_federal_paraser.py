from tests.sample_data.sms_samples import FEDERAL_UPI_DEBIT, FEDERAL_NETBANKING_DEBIT, INVALID_SMS
from tests.sample_data.praser_result_model import ResultModel

import datetime


class TestFederalBankParser:
    
    def test_parser_upi_transaction(self, federal_parser):
        result = ResultModel(federal_parser.parse(FEDERAL_UPI_DEBIT))
        
        assert result is not None
        assert result.account_num  == "0000"
        assert result.amount == 1.0
        assert result.merchant == "hashik2233-1@okhdfcbank" 
        assert result.timestamp == datetime.datetime(2025, 6, 4, 12, 17, 5)
        assert result.merchant in result.description 
        
    def test_parser_netbanking_transaction(self, federal_parser):
        result = ResultModel(federal_parser.parse(FEDERAL_NETBANKING_DEBIT))
        
        assert result is not None
        assert result.account_num  == "0214"
        assert result.amount == 2194.00
        assert result.merchant == "FEDNET Transaction" 
        assert result.timestamp == datetime.datetime(2025, 6, 8, 20, 34, 51)
    
    def test_paraser_invlaid_transaction(self, federal_parser):
        result = federal_parser.parse(INVALID_SMS)
        assert result is None