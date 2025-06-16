from pydantic import BaseModel, Field
from typing import List, Optional

# --- SubCategory Schemas ---
class SubCategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    icon_name: Optional[str] = Field(None, max_length=100, example="fthr:coffee")
    display_order: int = Field(0, example=0)
    parent_category_id: int 
    
class SubCategoryCreate(SubCategoryBase):
    pass

class SubCategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    icon_name: Optional[str] = Field(None, max_length=100)
    display_order: Optional[int] = None
    parent_category_id: Optional[int] = None 
    
class SubCategoryInDB(SubCategoryBase):
    id: int

    class Config:
        orm_mode = True

# --- Category Schemas ---
class CategoryBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, example="Food & Drinks")
    description: Optional[str] = Field(None, max_length=255, example="Eating out, Swiggy, Zomato etc.")
    display_order: int = Field(0, example=0)

class CategoryCreate(CategoryBase):
    pass 

class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    display_order: Optional[int] = None

class CategoryInDB(CategoryBase):
    id: int
    subcategories: List[SubCategoryInDB] = []

    class Config:
        orm_mode = True

class CategoryListWithSubcategories(BaseModel):
    categories: List[CategoryInDB]