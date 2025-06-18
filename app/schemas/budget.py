from pydantic import BaseModel, Field
from typing import Optional

class BudgetBase(BaseModel):
    year: int = Field(..., ge=2020, example=2024)
    month: int = Field(..., ge=1, le=12, example=6)
    budget_amount: float = Field(..., gt=0, example=15000.0)

class BudgetCreate(BudgetBase):
    pass

class BudgetUpdate(BaseModel):
    budget_amount: float = Field(..., gt=0, example=16000.0)

class BudgetInDB(BudgetBase):
    id: int
      
    class Config:
        orm_mode = True

    