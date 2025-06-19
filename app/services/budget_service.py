from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_
from datetime import datetime
from app.models import Transaction, SubCategory, Account
from app.crud import crud_budget

def get_current_budget_period() -> tuple[datetime, datetime]:
    """
    Determines the start and end dates for the current budget period.
    TODO: For now, this is fixed to the calendar month. Make this configurable later.
    """
    today = datetime.now()
    start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    next_month = (today.replace(day=28) + datetime.timedelta(days=4)).replace(day=1)
    end_of_month = next_month - datetime.timedelta(microseconds=1)
    
    return start_of_month, end_of_month

def get_current_month_spending(db: Session) -> float:
    """
    Calculates total spending for the current budget period, respecting all the new rules.
    """
    start_date, end_date = get_current_budget_period()

    total_spent = db.query(func.sum(Transaction.amount)).join(
        Transaction.subcategory
    ).join(
        Transaction.account
    ).filter(
        Transaction.transaction_datetime_from_sms.between(start_date, end_date),
        Account.purpose == 'PERSONAL',
        SubCategory.exclude_from_budget.is_(False),
        SubCategory.is_reimbursable.is_(False),
        Transaction.linked_transaction_hash.is_(None),
        or_(Transaction.override_reimbursable.is_(False), 
        and_(
            Transaction.override_reimbursable.is_(None), 
            SubCategory.is_reimbursable.is_(False)
        )
    )
        # TODO Add the override logic here later
    ).scalar()

    return total_spent or 0.0

def get_remaining_spend_power(db: Session) -> dict | None:
    """
    The main service function to get the full budget picture for the current period.
    """
    today = datetime.now()
    budget_obj = crud_budget.get_budget(db, year=today.year, month=today.month)
    
    if not budget_obj:
        return None 

    total_spent = get_current_month_spending(db)
    
    remaining = budget_obj.budget_amount - total_spent
    
    return {
        "budget": budget_obj.budget_amount,
        "spent": total_spent,
        "remaining": remaining,
    }