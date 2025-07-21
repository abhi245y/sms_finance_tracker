from tests.fixtures.test_data_factory import TestDataFactory
from app.services.budget_service import (
    get_current_budget_period, 
    get_current_month_spending, 
    get_remaining_spend_power
)
from app.models.account import AccountType, AccountPurpose

from datetime import datetime
from freezegun import freeze_time


class TestBudgetService:
    """Test suite for BudgetService calculations"""
    
    @freeze_time("2025-06-15")
    def test_get_current_budget_period_june_2025(self):
        """Test budget period calculation for mid-June"""
        
        start_date, end_date = get_current_budget_period()
        
        
        assert start_date == datetime(2025, 6, 1, 0, 0, 0, 0)
        assert end_date.year == 2025
        assert end_date.month == 6
        assert end_date.day == 30  
        assert end_date.hour == 23
        assert end_date.minute == 59
    
    @freeze_time("2025-02-15")
    def test_get_current_budget_period_february_2025(self):
        """Test budget period calculation for February (non-leap year)"""
        
        start_date, end_date = get_current_budget_period()
        
        
        assert start_date == datetime(2025, 2, 1, 0, 0, 0, 0)
        assert end_date.day == 28
    
    @freeze_time("2025-06-15")
    def test_get_current_month_spending_no_transactions(self, db_session):
        """Test spending calculation with no transactions"""
        
        result = get_current_month_spending(db_session)
        
        
        assert result == 0.0
    
    @freeze_time("2025-06-15")
    def test_get_current_month_spending_with_valid_transactions(self, db_session):
        """Test spending calculation with valid personal account transactions"""

        personal_account = TestDataFactory.create_test_account(
            db_session, 
            account_type=AccountType.CREDIT_CARD,
            purpose=AccountPurpose.PERSONAL
        )
        
        category = TestDataFactory.create_test_category(db_session)
        subcategory = TestDataFactory.create_test_sub_category(
            db_session, 
            category,
            name="Coffee",
            is_reimbursable=False,
            exclude_from_budget=False
        )
        
        TestDataFactory.create_test_transaction(
            db_session,
            account=personal_account,
            subcategory=subcategory,
            amount=100.0,
            transaction_datetime_from_sms=datetime(2025, 6, 10),
            override_reimbursable=None  
        )
        
        TestDataFactory.create_test_transaction(
            db_session,
            account=personal_account,
            subcategory=subcategory,
            amount=250.0,
            transaction_datetime_from_sms=datetime(2025, 6, 12)
        )
        
        
        result = get_current_month_spending(db_session)
        
        
        assert result == 350.0
    
    @freeze_time("2025-06-15")
    def test_get_current_month_spending_excludes_business_accounts(self, db_session):
        """Test that business account transactions are excluded"""
        business_account = TestDataFactory.create_test_account(
            db_session,
            purpose=AccountPurpose.BUSINESS
        )
        
        category = TestDataFactory.create_test_category(db_session)
        subcategory = TestDataFactory.create_test_sub_category(
            db_session, category, is_reimbursable=False, exclude_from_budget=False
        )
        
        TestDataFactory.create_test_transaction(
            db_session,
            account=business_account,
            subcategory=subcategory,
            amount=500.0,
            transaction_datetime_from_sms=datetime(2025, 6, 10)
        )
        
        
        result = get_current_month_spending(db_session)
        
        assert result == 0.0
        
    @freeze_time("2025-06-15")
    def test_get_current_month_spending_excludes_reimbursable_subcategory(self, db_session):
        category = TestDataFactory.create_test_category(db_session)
        subcategory = TestDataFactory.create_test_sub_category(
            db_session, category, is_reimbursable=True, exclude_from_budget=True
        )
        
        TestDataFactory.create_test_transaction(
            db_session,
            subcategory=subcategory,
            override_reimbursable=None,
            transaction_datetime_from_sms=datetime(2025, 6, 10)
        )
        
        result = get_current_month_spending(db_session)
        
        assert result == 0.0
        
    @freeze_time("2025-06-15")
    def  test_get_current_month_spending_includes_non_reimbursable_subcategory(self, db_session):
        pass
        

    # TODO: Add more get_current_month_spending tests for:
    # - Reimbursable transactions (should be excluded)
    # - Transactions with exclude_from_budget=True
    # - Linked transactions (should be excluded)
    # - Transactions outside current month (should be excluded)
    # - Override reimbursable scenarios
    
    @freeze_time("2025-06-15")
    def test_get_remaining_spend_power_with_budget_and_spending(self, db_session):
        """Test complete spend power calculation"""
        TestDataFactory.create_test_monthly_budget(
            db_session,
            year=2025,
            month=6,
            budget_amount=10000.0
        )
        
        personal_account = TestDataFactory.create_test_account(
            db_session, purpose=AccountPurpose.PERSONAL
        )
        category = TestDataFactory.create_test_category(db_session)
        subcategory = TestDataFactory.create_test_sub_category(
            db_session, category, is_reimbursable=False, exclude_from_budget=False
        )
        
        TestDataFactory.create_test_transaction(
            db_session,
            account=personal_account,
            subcategory=subcategory,
            amount=2500.0,
            transaction_datetime_from_sms=datetime(2025, 6, 10)
        )
        
        
        result = get_remaining_spend_power(db_session)
        
        
        assert result is not None
        assert result["budget"] == 10000.0
        assert result["spent"] == 2500.0
        assert result["remaining"] == 7500.0 
    
    @freeze_time("2025-06-15")
    def test_get_remaining_spend_power_no_budget_set(self, db_session):
        """Test when no budget is set for current month"""
        
        result = get_remaining_spend_power(db_session)
        
        
        assert result is None

    # TODO: Add test for get_remaining_spend_power with no spending