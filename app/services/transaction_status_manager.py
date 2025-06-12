from typing import Dict, Any, Optional

from app.models.account import AccountType
from app.crud import crud_category, crud_account
from app.models.transaction import TransactionStatus 


class TransactionStatusManager:
    """Manages transaction status transitions based on account and category validation"""
    
    @staticmethod
    def is_account_valid( db, account_id: Optional[int]) -> bool:
        """Check if provided account_id is valid"""
        if account_id is None:
            return False
        
        try:
            account = crud_account.get_account(db=db, account_id=account_id)
            return account is not None and account.account_type != AccountType.UNKNOWN
        except Exception:
            return False
    
    @staticmethod
    def is_category_valid(db, category_id: Optional[int], category_name: Optional[str]=None) -> bool:
        """Check if provided category_id or category_name is valid"""
        if category_id is None and category_name is None:
            return False
        
        try:
            if category_id:
                category = crud_category.get_category(db=db, category_id=category_id)
                return category is not None and category.name.lower() != "uncategorized"
            elif category_name:
                return category_name.lower() != "uncategorized"
            return False
        except Exception:
            return False
        
    @staticmethod
    def determine_initial_status(db, creation_data: Dict[str, Any]) -> TransactionStatus:
        """
        Determine the initial status for a new transaction
        
        Args:
            creation_data: Data provided for transaction creation
            db: Database session
            
        Returns:
            TransactionStatus: The appropriate initial status
        """
        account_id = creation_data.get("account_id")
        category_id = creation_data.get("category_id")
        
        has_valid_account = TransactionStatusManager.is_account_valid(account_id=account_id, db=db)
        has_valid_category = TransactionStatusManager.is_category_valid(category_id=category_id, db=db)
        
        if has_valid_account and has_valid_category:
            return TransactionStatus.PROCESSED
        elif has_valid_account and not has_valid_category:
            return TransactionStatus.PENDING_CATEGORIZATION
        elif not has_valid_account and has_valid_category:
            return TransactionStatus.PENDING_ACCOUNT_SELECTION
        else:
            return TransactionStatus.PENDING_PROCESSING
    
    @staticmethod
    def determine_status_for_update(transaction, db, update_data: Dict[str, Any]) -> TransactionStatus:
        """
        Determine status for transaction updates (existing method)
        """
        is_providing_account = "account_id" in update_data
        is_providing_category = "category_id" in update_data or "category_name" in update_data
        
        if is_providing_account:
            has_valid_account = TransactionStatusManager.is_account_valid(
                account_id=update_data.get("account_id"), db=db
            )
        else:
            has_valid_account = TransactionStatusManager.is_account_valid(
                account_id=transaction.account_id, db=db
            )
        
        if is_providing_category:
            has_valid_category = TransactionStatusManager.is_category_valid(
                category_id=update_data.get("category_id"), 
                category_name=update_data.get("category_name"), 
                db=db
            )
        else:
            has_valid_category = TransactionStatusManager.is_category_valid(
                category_id=transaction.category_id, db=db
            )
        
        if has_valid_account and has_valid_category:
            return TransactionStatus.PROCESSED
        elif has_valid_account and not has_valid_category:
            return TransactionStatus.PENDING_CATEGORIZATION
        elif not has_valid_account and has_valid_category:
            return TransactionStatus.PENDING_ACCOUNT_SELECTION
        else:
            return TransactionStatus.PENDING_PROCESSING