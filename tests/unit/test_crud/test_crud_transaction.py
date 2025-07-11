from tests.fixtures.test_data_factory import TestDataFactory
from tests.sample_data.sms_samples import SBI_CREDIT_CARD_DEBIT
from app.crud import crud_transaction
from app.schemas.transaction import TransactionCreate, TransactionUpdate

import uuid

class TestTransactionCRUD:
        
    def test_create_transaction(sefl, db_session):
        
        account = TestDataFactory.create_test_account(db_session=db_session)
        category = TestDataFactory.create_test_category(db_session=db_session)
        sub_category = TestDataFactory.create_test_sub_category(db_session=db_session, parent_category=category)
        
        transaction_data = TransactionCreate(
            unique_hash= f"test_hash_{uuid.uuid4().hex[:8]}", 
            raw_sms_content= SBI_CREDIT_CARD_DEBIT,
            amount = 100.00,
            currency="INR",
            subcategory_id=sub_category.id,
            account_id=account.id
        )
        
        result = crud_transaction.create_transaction(db=db_session, obj_in=transaction_data)
        
        assert result.id is not None
        assert result.amount == 100
        assert result.account_id == account.id
        assert result.subcategory_id == sub_category.id
        
    def test_get_transaction_by_hash(self, db_session):
        
        account = TestDataFactory.create_test_account(db_session=db_session)
        category = TestDataFactory.create_test_category(db_session=db_session, name="Test Vehicle")
        sub_category = TestDataFactory.create_test_sub_category(db_session=db_session, parent_category=category)
        
        transaction = TestDataFactory.create_test_transaction(
            db_session=db_session, account=account, subcategory=sub_category, unique_hash=f"test_hash_{uuid.uuid4().hex[:8]}"
        )
        
        result = crud_transaction.get_transaction_by_hash(
            db=db_session, hash_str=transaction.unique_hash, include_relations=False
        )
        
        assert result is not None
        assert result.unique_hash == transaction.unique_hash
        assert result.id == transaction.id
        
    def test_get_transaction_by_hash_not_found(self, db_session):
        
        result = crud_transaction.get_transaction_by_hash(
            db=db_session, hash_str=f"test_hash_{uuid.uuid4().hex[:8]}", include_relations=False
        )
        
        assert result is None
    
    def test_update_transaction(self, db_session):
        
        account = TestDataFactory.create_test_account(db_session=db_session)
        category = TestDataFactory.create_test_category(db_session=db_session, name="Test Investment")
        sub_category = TestDataFactory.create_test_sub_category(db_session=db_session, parent_category=category)
        
        transaction = TestDataFactory.create_test_transaction(
            db_session=db_session, account=account, subcategory=sub_category, description="Original description"
        )
        
        update_data = TransactionUpdate(description="Updated description")
        
        update_transaction = crud_transaction.update_transaction(db=db_session, db_obj=transaction, obj_in=update_data)
        
        assert update_transaction.description == "Updated description"
        assert update_transaction.id == transaction.id