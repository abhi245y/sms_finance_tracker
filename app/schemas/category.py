from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional

# --- SubCategory Schemas ---
class SubCategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    icon_name: Optional[str] = Field(None, max_length=100, json_schema_extra={"example": "fthr:coffee"})
    display_order: int = Field(0, json_schema_extra={"example": 0})
    is_reimbursable: bool = Field(default=False)
    exclude_from_budget: bool = Field(default=False)
    parent_category_id: int 
    
class SubCategoryCreate(SubCategoryBase):
    pass

class SubCategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    icon_name: Optional[str] = Field(None, max_length=100)
    display_order: Optional[int] = None
    parent_category_id: Optional[int] = None
    is_reimbursable: Optional[bool] = None 
    exclude_from_budget: Optional[bool] = None
    
class SubCategoryInDB(SubCategoryBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

# --- Category Schemas ---
class CategoryBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, json_schema_extra={"example": "Food & Drinks"})
    description: Optional[str] = Field(None, max_length=255, json_schema_extra={"example": "Eating out, Swiggy, Zomato etc."})
    display_order: int = Field(0, json_schema_extra={"example": 0})

class CategoryCreate(CategoryBase):
    pass 

class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    display_order: Optional[int] = None

class CategoryInDB(CategoryBase):
    id: int
    subcategories: List[SubCategoryInDB] = []

    model_config = ConfigDict(from_attributes=True)

class CategoryListWithSubcategories(BaseModel):
    categories: List[CategoryInDB]