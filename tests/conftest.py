
import pytest
from app.services.parsers.hdfc_parser import HDFCParser
from app.services.parsers.amex_parser import AmexParser
from app.services.parsers.federal_parser import FederalBankParser
from app.services.parsers.icici_parser import ICICIBankParser
from app.services.parsers.idfc_parser import IDFCFirstBankParser
from app.services.parsers.sbi_parser import SBIParser

@pytest.fixture
def hdfc_parser():
    return HDFCParser()

@pytest.fixture
def amex_parser():
    return AmexParser()

@pytest.fixture
def federal_parser():
    return FederalBankParser()

@pytest.fixture
def icici_parser():
    return ICICIBankParser()

@pytest.fixture
def idfc_parser():
    return IDFCFirstBankParser()

@pytest.fixture
def sbi_parser():
    return SBIParser()