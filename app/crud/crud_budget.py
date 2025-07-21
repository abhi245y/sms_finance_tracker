from sqlalchemy.orm import Session
from app.models.monthly_budget import MonthlyBudget
from app.schemas.budget import BudgetCreate, BudgetUpdate

def get_budget(db: Session, *, year: int, month: int) -> MonthlyBudget | None:
    """
    Retrieves the budget for a specific year and month.
    """
    return db.query(MonthlyBudget).filter(MonthlyBudget.year == year, MonthlyBudget.month == month).first()

def create_budget(db: Session, *, obj_in: BudgetCreate) -> MonthlyBudget:
    """
    Creates a new budget entry.
    """
    db_obj = MonthlyBudget(**obj_in.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update_budget(db: Session, *, db_obj: MonthlyBudget, obj_in: BudgetUpdate) -> MonthlyBudget:
    """
    Updates an existing budget's amount.
    """
    db_obj.budget_amount = obj_in.budget_amount
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def create_or_update_budget(db: Session, *, budget_in: BudgetCreate) -> MonthlyBudget:
    """
    A convenient function that checks if a budget for the given month/year exists.
    If it does, it updates it. If not, it creates a new one.
    """
    db_budget = get_budget(db, year=budget_in.year, month=budget_in.month)
    if db_budget:
        update_schema = BudgetUpdate(budget_amount=budget_in.budget_amount)
        return update_budget(db=db, db_obj=db_budget, obj_in=update_schema)
    else:
        return create_budget(db=db, obj_in=budget_in)