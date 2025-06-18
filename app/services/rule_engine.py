from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
# from app.crud import crud_subcategory

# Define rules as a list of functions. This is easily extendable.
# Each rule function takes the parsed data and returns a subcategory_id if it matches, else None.

def rule_self_transfer(parsed_data: Dict[str, Any], db: Session) -> Optional[int]:
    # This is a placeholder. A real implementation would check against a list of the user's own VPAs/accounts.
    # For now, replying on the user to categorize this manually.
    return None

def rule_cred_cc_payment(parsed_data: Dict[str, Any], db: Session) -> Optional[int]:
    merchant = parsed_data.get("merchant_vpa", "").lower()
    if "cred.cc.payment" in merchant:
        # Find the subcategory for "Credit Card Payment"
        # This requires a way to reliably get a specific subcategory. Let's assume we have a helper for that.
        # subcat = crud_subcategory.get_subcategory_by_name_and_parent(db, name="Credit card", parent_name="Credit Bill")
        # if subcat: return subcat.id
        # For now, let's assume we know its ID from the seed data.
        return 1036
    return None

RULES = [
    rule_cred_cc_payment,
    rule_self_transfer,
]

class RuleEngine:
    def __init__(self, db_session: Session):
        self.db = db_session

    def run(self, parsed_data: Dict[str, Any]) -> Optional[int]:
        """
        Runs all rules against the parsed transaction data.
        Returns the ID of the first matching subcategory.
        """
        for rule_func in RULES:
            subcategory_id = rule_func(parsed_data, self.db)
            if subcategory_id:
                print(f"DEBUG: Rule '{rule_func.__name__}' matched. Setting subcategory to {subcategory_id}.")
                return subcategory_id
        return None