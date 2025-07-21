from  app.models import (
    Account, AccountType,AccountPurpose,
    Category, SubCategory, Transaction, TransactionStatus)

from datetime import datetime

from sqlalchemy.orm import Session

from tests.sample_data.sms_samples import SBI_CREDIT_CARD_DEBIT
import uuid
import random

class TestDataFactory:
    
    @staticmethod
    def create_test_account(db_session: Session, **kwargs):
        """
        Creates a test Account with sensible defaults.
        """
        
        defaults = {
            "name": "Test HDFC Card",
            "account_type": AccountType.CREDIT_CARD,
            "bank_name": "HDFC Bank", 
            "account_last4": random.randint(1000, 9999),
            "purpose": AccountPurpose.PERSONAL
        }
        
        defaults.update(kwargs)
        
        account = Account(**defaults)
        
        db_session.add(account)
        db_session.commit()
        db_session.refresh(account) 
        
        return account
    
    @staticmethod
    def create_test_category(db_session: Session, **kwargs):
        """
        Creates a test Category with defaults
        """
        defaults = {
            "name": "Test Food & Drinks",
            "description": "Test category for food expenses",
            "display_order": 1
        }
        
        defaults.update(kwargs)
        
        category = Category(**defaults)
        db_session.add(category)
        db_session.commit()
        db_session.refresh(category)
        
        return category
    
    @staticmethod
    def create_test_sub_category(db_session: Session, parent_category , **kwargs):
        """
        Creates a test Sub Category with defaults
        """
        
        defaults = {
            "name": "Test Snacks",
            "icon_name": "emoji:🍿", 
            "display_order": 1,
            "is_reimbursable": False,
            "exclude_from_budget": False,
            "parent_category_id": parent_category.id
        }
    
        
        defaults.update(kwargs)
        
        sub_category = SubCategory(**defaults)
        db_session.add(sub_category)
        db_session.commit()
        db_session.refresh(sub_category)
        
        return sub_category
    
    @staticmethod
    def create_test_transaction(db_session: Session, account , subcategory , **kwargs):
        """
        Creates a test Transaction with defaults
        """
        
        defaults = {
            "raw_sms_content": SBI_CREDIT_CARD_DEBIT,
            "amount": 500.00,
            "currency": "INR",
            "merchant_vpa": "Test Merchant",
            "description": "Test description",
        
            "unique_hash": f"test_hash_{uuid.uuid4().hex[:8]}", 
            "transaction_datetime_from_sms": datetime.now(),  
            "status": TransactionStatus.PROCESSED, 
        
            "subcategory_id": subcategory.id, 
            "account_id": account.id if account is not None else None,          
        
            "telegram_message_id": None,       
            "linked_transaction_hash": None,  
            "override_reimbursable": None,
        }
        
        defaults.update(kwargs)
        
        transaction = Transaction(**defaults)
        db_session.add(transaction)
        db_session.commit()
        db_session.refresh(transaction)
        
        return transaction
    
    @staticmethod
    def create_test_monthly_budget(db_session: Session, **kwargs):
        """
        Creates a test MonthlyBudget with defaults
        """
        from app.models.monthly_budget import MonthlyBudget
        from datetime import datetime
        
        now = datetime.now()
        defaults = {
            "year": now.year,
            "month": now.month,
            "budget_amount": 15000.0
        }
        
        defaults.update(kwargs)
        
        budget = MonthlyBudget(**defaults)
        db_session.add(budget)
        db_session.commit()
        db_session.refresh(budget)
        
        return budget