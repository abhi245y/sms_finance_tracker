from pydantic import BaseModel, Field, ConfigDict

class BudgetBase(BaseModel):
    year: int = Field(..., ge=2020, json_schema_extra={"example": 2024})
    month: int = Field(..., ge=1, le=12, json_schema_extra={"example": 6})
    budget_amount: float = Field(..., gt=0, json_schema_extra={"example": 15000.0})

class BudgetCreate(BudgetBase):
    pass

class BudgetUpdate(BaseModel):
    budget_amount: float = Field(..., gt=0, json_schema_extra={"example": 16000.0})

class BudgetInDB(BudgetBase):
    id: int
      
    model_config = ConfigDict(from_attributes=True)
    