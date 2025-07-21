from tests.fixtures.test_data_factory import TestDataFactory
from app.services.transaction_status_manager import TransactionStatusManager
from app.models.transaction import TransactionStatus
from app.models.account import AccountType


class TestTransactionStatusManager:
    """Test suite for TransactionStatusManager business logic"""
    
    def test_is_account_valid_with_valid_account(self, db_session):
        """Test that a properly configured account is considered valid"""
        account = TestDataFactory.create_test_account(
            db_session, 
            account_type=AccountType.CREDIT_CARD 
        )
        
        result = TransactionStatusManager.is_account_valid(db_session, account.id)
        
        assert result is True
    
    def test_is_account_valid_with_unknown_account_type(self, db_session):
        """Test that UNKNOWN account type is considered invalid"""
        
        account = TestDataFactory.create_test_account(
            db_session, 
            account_type=AccountType.UNKNOWN
        )
        
          
        result = TransactionStatusManager.is_account_valid(db_session, account.id)
        
        
        assert result is False
    
    def test_is_account_valid_with_none_account_id(self, db_session):
        """Test that None account_id returns False"""
        
        result = TransactionStatusManager.is_account_valid(db_session, None)
        
        assert result is False
    
    def test_is_account_valid_with_nonexistent_account_id(self, db_session):
        """Test that non-existent account ID returns False"""
        
        result = TransactionStatusManager.is_account_valid(db_session, 99999)
        
        assert result is False
        
    def test_is_subcategory_valid(self, db_session):
        
        category = TestDataFactory.create_test_category(db_session)
        sub_category = TestDataFactory.create_test_sub_category(db_session, parent_category=category)
        
        result = TransactionStatusManager.is_subcategory_valid(db=db_session, subcategory_id=sub_category.id)
        
        assert result is not None
        assert result is True
    
    def test_determine_initial_status_all_valid(self, db_session):
        """Test status when both account and subcategory are valid"""
        
        account = TestDataFactory.create_test_account(
            db_session, account_type=AccountType.SAVINGS_ACCOUNT
        )
        category = TestDataFactory.create_test_category(db_session)
        subcategory = TestDataFactory.create_test_sub_category(
            db_session, category, name="Pizza" 
        )
        
        creation_data = {
            "account_id": account.id,
            "subcategory_id": subcategory.id
        }
        
        
        result = TransactionStatusManager.determine_initial_status(db_session, creation_data)
        
        
        assert result == TransactionStatus.PROCESSED
    
    def test_determine_initial_status_needs_account_selection(self, db_session):
        """Test status when account is invalid but category is valid"""
        
        category = TestDataFactory.create_test_category(db_session)
        subcategory = TestDataFactory.create_test_sub_category(
            db_session, category, name="Coffee"
        )
        
        creation_data = {
            "account_id": None, 
            "subcategory_id": subcategory.id
        }
        
        
        result = TransactionStatusManager.determine_initial_status(db_session, creation_data)
        
        
        assert result == TransactionStatus.PENDING_ACCOUNT_SELECTION
    
    def test_determine_status_for_update_upgrades_from_unknown_account(self, db_session):
        """Test upgrading from UNKNOWN account to valid account"""
        
        unknown_account = TestDataFactory.create_test_account(
            db_session, account_type=AccountType.UNKNOWN
        )
        category = TestDataFactory.create_test_category(db_session)
        valid_subcategory = TestDataFactory.create_test_sub_category(db_session, category)
        transaction = TestDataFactory.create_test_transaction(
            db_session, account=unknown_account, subcategory=valid_subcategory
        )
    
        valid_account = TestDataFactory.create_test_account(db_session)
    
        update_data = {"account_id": valid_account.id}
    
        result = TransactionStatusManager.determine_status_for_update(
            transaction, db_session, update_data
        )
    
        assert result == TransactionStatus.PROCESSED
        
        
    def test_determine_status_for_update_downgrades_to_unknown_account(self, db_session):
        """Test downgrading from valid account to UNKNOWN account"""
        
        valid_account = TestDataFactory.create_test_account(db_session)
        category = TestDataFactory.create_test_category(db_session)
        valid_subcategory = TestDataFactory.create_test_sub_category(
            db_session, category, name="Coffee"
        )
        transaction = TestDataFactory.create_test_transaction(
            db_session, account=valid_account, subcategory=valid_subcategory)
    
        unknown_account = TestDataFactory.create_test_account(
            db_session, account_type=AccountType.UNKNOWN, account_last4="0000"
        )
    
        update_data = {"account_id": unknown_account.id}
    
        result = TransactionStatusManager.determine_status_for_update(transaction, db_session, update_data)
    
        assert result == TransactionStatus.PENDING_ACCOUNT_SELECTION
        
    def test_determine_status_for_update_category_to_uncategorized(self, db_session):
        """Test changing from valid category to Uncategorized"""

        valid_account = TestDataFactory.create_test_account(db_session)
        category = TestDataFactory.create_test_category(db_session)
        valid_subcategory = TestDataFactory.create_test_sub_category(
            db_session, category, name="Coffee")
        
        transaction = TestDataFactory.create_test_transaction(
            db_session, account=valid_account, subcategory=valid_subcategory)
        
        general_category = TestDataFactory.create_test_category(db_session, name="General")
        uncategoriesd_subcategory = TestDataFactory.create_test_sub_category(
            db_session, general_category, name="Uncategorized"
        )
        
        update_data = {"subcategory_id": uncategoriesd_subcategory.id}
        
        result = TransactionStatusManager.determine_status_for_update(transaction, db_session, update_data)
    
        assert result == TransactionStatus.PENDING_CATEGORIZATION