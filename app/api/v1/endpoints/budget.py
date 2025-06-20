from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Any 
from datetime import datetime

from app.api import deps
from app.schemas import budget as budget_schema
from app.crud import crud_budget 
from app.services.budget_service import get_remaining_spend_power

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
    If a budget for that period already exists, its amount will be updated.
    Otherwise, a new budget entry will be created.
    """
    budget = crud_budget.create_or_update_budget(db, budget_in=budget_in)
    return budget

@router.get(
    "/{year}/{month}",
    response_model=budget_schema.BudgetInDB,
    summary="Get Budget for a Specific Month",
    dependencies=[Depends(deps.get_api_key)]
)
def get_specific_monthly_budget(
    year: int,
    month: int,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Retrieves the budget record for the specified year and month.
    """
    if not (2020 <= year <= datetime.now().year + 5):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid year provided.")
    if not (1 <= month <= 12):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid month provided.")
        
    budget = crud_budget.get_budget(db, year=year, month=month)
    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No budget found for {month:02d}/{year}."
        )
    return budget

@router.get(
    "/summary", 
    response_model=dict,
    summary="Get Current Budget Summary",
    dependencies=[Depends(deps.get_api_key)]
)
def get_budget_summary(db: Session = Depends(deps.get_db)) -> Any:
    """
    Returns the current month's budget, amount spent, and remaining spend power.
    """
    summary = get_remaining_spend_power(db)
    if summary is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No budget has been set for the current month, or spend power could not be calculated."
        )
    return summary