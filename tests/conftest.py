
import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.services.parsers.hdfc_parser import HDFCParser
from app.services.parsers.amex_parser import AmexParser
from app.services.parsers.federal_parser import FederalBankParser
from app.services.parsers.icici_parser import ICICIBankParser
from app.services.parsers.idfc_parser import IDFCFirstBankParser
from app.services.parsers.sbi_parser import SBIParser

from app.models.transaction import Transaction  # noqa: F401
from app.models.category import Category  # noqa: F401
from app.models.subcategory import SubCategory # noqa: F401
from app.models.account import Account # noqa: F401
from app.models.monthly_budget import MonthlyBudget # noqa: F401


from app.db.base_class import Base

from app.main import app
from app.db.session import get_db

from tests.fixtures.test_data_factory import TestDataFactory


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
    yield test_engine
    Base.metadata.drop_all(bind=test_engine)
    
@pytest.fixture
def db_session(test_tables, test_engine):
    """
    Provides a clean database session for each test.
    Changes are rolled back after each test.
    """
    
    engine = test_tables
    TestSession = sessionmaker(bind=engine)
    session = TestSession()
    
    try:
        transaction = session.begin()
        yield session
        transaction.rollback()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

@pytest.fixture
def test_client(db_session):
    """Create FastAPI test client with test database"""
    
    def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.clear()
    
@pytest.fixture
def test_data_setup(db_session):
    """Create a full set of test data for API testing"""
    
    food_category = TestDataFactory.create_test_category(
        db_session,
        name="Food & Drinks", 
        description="Eating out, delivery, etc.",
        display_order=1
    )
    
    coffee_subcategory = TestDataFactory.create_test_sub_category(
        db_session,
        food_category,
        name="Tea & Coffee",
        icon_name="emoji:☕",
        display_order=1,
        is_reimbursable=False,
        exclude_from_budget=False
    )
    
    snacks_subcategory = TestDataFactory.create_test_sub_category(
        db_session,
        food_category, 
        name="Snacks",
        icon_name="emoji:🍿",
        display_order=2
    )
    
    transport_category = TestDataFactory.create_test_category(
        db_session,
        name="Transport",
        description="Uber, Ola, etc.",
        display_order=2
    )
    
    uber_subcategory = TestDataFactory.create_test_sub_category(
        db_session,
        transport_category,
        name="Uber",
        icon_name="img:brand/uber.svg",
        display_order=1
    )
    
    return {
        "categories": [food_category, transport_category],
        "subcategories": [coffee_subcategory, snacks_subcategory, uber_subcategory]
    }

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