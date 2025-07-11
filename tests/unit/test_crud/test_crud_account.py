from tests.fixtures.test_data_factory import TestDataFactory
from app.crud import crud_account
from app.schemas.account import AccountCreate, AccountUpdate
from app.models.account import AccountType, AccountPurpose

class TestAccountCRUD:
    
    def test_create_account_success(self, db_session):
        account_data = AccountCreate(
            name="Test ICICI Card",
            account_type=AccountType.CREDIT_CARD,
            bank_name="ICICI Bank",
            account_last4="5678",
            purpose=AccountPurpose.PERSONAL
        )
        
        result = crud_account.create_account(db_session, obj_in=account_data)
        
        assert result.id is not None
        assert result.name == "Test ICICI Card"
        assert result.account_last4 == "5678"
        assert result.account_type == AccountType.CREDIT_CARD
    
    def test_get_account_by_identifier_exists(self, db_session):
        account = TestDataFactory.create_test_account(
            db_session, 
            bank_name="SBI", 
            account_last4="9999"
        )
        
        result = crud_account.get_account_by_identifier(
            db_session, bank_name="SBI", account_last4="9999"
        )
        
        assert result is not None
        assert result.id == account.id
        assert result.bank_name == "SBI"
        assert result.account_last4 == "9999"
    
    def test_get_account_by_identifier_not_found(self, db_session):
        
        result = crud_account.get_account_by_identifier(
            db_session, bank_name="NonExistent", account_last4="0000"
        )
        
        assert result is None
    
    def test_get_accounts_with_pagination(self, db_session):
        TestDataFactory.create_test_account(db_session, name="Account 1")
        TestDataFactory.create_test_account(db_session, name="Account 2", account_last4="1111")
        TestDataFactory.create_test_account(db_session, name="Account 3", account_last4="2222")
        
        result = crud_account.get_accounts(db_session, skip=0, limit=2)
        
        assert len(result) == 2
        assert all(account.id is not None for account in result)
    
    def test_update_account_success(self, db_session):
        account = TestDataFactory.create_test_account(
            db_session, name="Old Name", purpose=AccountPurpose.PERSONAL
        )
        
        update_data = AccountUpdate(name="New Name", purpose=AccountPurpose.BUSINESS)
        updated_account = crud_account.update_account(
            db_session, db_obj=account, obj_in=update_data
        )
        
        assert updated_account.name == "New Name"
        assert updated_account.purpose == AccountPurpose.BUSINESS
        assert updated_account.id == account.id 