from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Any

from app.api import deps
from app.schemas import budget as budget_schema
from app.crud import crud_budget

router = APIRouter()

@router.post(
    "/",
    response_model=budget_schema.BudgetInDB,
    status_code=status.HTTP_201_CREATED,
    summary="Set or Update a Monthly Budget",
    dependencies=[Depends(deps.get_api_key)]
)
def set_or_update_monthly_budget(
    *,
    db: Session = Depends(deps.get_db),
    budget_in: budget_schema.BudgetCreate,
) -> Any:
    """
    Sets the budget amount for a given year and month.
    If a budget for that period already exists, it will be updated.
    Otherwise, a new one will be created.
    """
    budget = crud_budget.create_or_update_budget(db, budget_in=budget_in)
    return budget

@router.get(
    "/summary",
    summary="Get Current Budget Summary",
    dependencies=[Depends(deps.get_api_key)]
)
def get_budget_summary(db: Session = Depends(deps.get_db)) -> Any:
    """
    Returns the current month's budget, amount spent, and remaining spend power.
    """
    from app.services.budget_service import get_remaining_spend_power

    summary = get_remaining_spend_power(db)
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No budget has been set for the current month."
        )
    return summary