
import pytest
from app.services.parsers.hdfc_parser import HDFCParser
from app.services.parsers.amex_parser import AmexParser
from app.services.parsers.federal_parser import FederalBankParser
from app.services.parsers.icici_parser import ICICIBankParser
from app.services.parsers.idfc_parser import IDFCFirstBankParser
from app.services.parsers.sbi_parser import SBIParser

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base_class import Base

@pytest.fixture(scope='function')
def test_engine():
    """Creates an in-memory SQLite database for testing"""
    engine = create_engine(
        "sqlite:///:memory:", 
        connect_args={"check_same_thread":False},
        echo=False
    )
    
    return engine

@pytest.fixture(scope='function')
def test_tables(test_engine):
    """Creates all database tables once per test session"""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)
    
@pytest.fixture
def db_session(test_tables, test_engine):
    """
    Provides a clean database session for each test.
    Changes are rolled back after each test.
    """
    
    TestSession = sessionmaker(bind=test_engine)
    session = TestSession()
    
    try:
        yield session
    finally:
        session.rollback()
        session.close()
        

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