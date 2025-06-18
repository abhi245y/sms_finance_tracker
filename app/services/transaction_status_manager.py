from typing import Dict, Any, Optional

from app.models.account import AccountType
from app.crud import crud_account 
from app.models.transaction import TransactionStatus, Transaction 
from app.models.subcategory import SubCategory 


class TransactionStatusManager:
    """Manages transaction status transitions based on account and subcategory validation"""
    
    @staticmethod
    def is_account_valid(db, account_id: Optional[int]) -> bool:
        if account_id is None:
            return False
        try:
            account = crud_account.get_account(db=db, account_id=account_id)
            return account is not None and account.account_type != AccountType.UNKNOWN
        except Exception:
            return False
    
    @staticmethod
    def is_subcategory_valid(db, subcategory_id: Optional[int]) -> bool:
        """Check if provided subcategory_id is valid and not 'Uncategorized'."""
        if subcategory_id is None:
            return False
        
        try:
            subcategory = db.query(SubCategory).filter(SubCategory.id == subcategory_id).first()
            
            if subcategory and subcategory.name.lower() != "uncategorized":
                 return True
            return False
        except Exception:
            return False
        
    @staticmethod
    def determine_initial_status(db, creation_data: Dict[str, Any]) -> TransactionStatus:
        account_id = creation_data.get("account_id")
        has_valid_account = TransactionStatusManager.is_account_valid(account_id=account_id, db=db)
        

        subcategory_id_from_creation = creation_data.get("subcategory_id")
        has_meaningful_category = TransactionStatusManager.is_subcategory_valid(
            subcategory_id=subcategory_id_from_creation, db=db
        )

        if has_valid_account and has_meaningful_category:
            return TransactionStatus.PROCESSED
        elif has_valid_account and not has_meaningful_category: 
            return TransactionStatus.PENDING_CATEGORIZATION
        elif not has_valid_account and has_meaningful_category:
            return TransactionStatus.PENDING_ACCOUNT_SELECTION
        else:
            return TransactionStatus.PENDING_PROCESSING 
    
    @staticmethod
    def determine_status_for_update(transaction: Transaction, db, update_data: Dict[str, Any]) -> TransactionStatus:
        current_account_id = transaction.account_id
        current_subcategory_id = transaction.subcategory_id

        if "account_id" in update_data:
            current_account_id = update_data["account_id"]
        
        if "subcategory_id" in update_data:
            current_subcategory_id = update_data["subcategory_id"]
            
        has_valid_account = TransactionStatusManager.is_account_valid(account_id=current_account_id, db=db)
        has_meaningful_category = TransactionStatusManager.is_subcategory_valid(subcategory_id=current_subcategory_id, db=db)
        
        if has_valid_account and has_meaningful_category:
            return TransactionStatus.PROCESSED
        elif has_valid_account and not has_meaningful_category:
            return TransactionStatus.PENDING_CATEGORIZATION
        elif not has_valid_account and has_meaningful_category:
            return TransactionStatus.PENDING_ACCOUNT_SELECTION
        else:
            return TransactionStatus.PENDING_PROCESSING 