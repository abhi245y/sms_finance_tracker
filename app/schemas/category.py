from pydantic import BaseModel, Field, validator
from typing import List, Optional
from enum import Enum

# --- SubCategory Schemas ---
class SubCategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    icon_name: Optional[str] = Field(None, max_length=100, example="fthr:coffee")
    display_order: int = Field(0, example=0)
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

    class Config:
        from_attributes  = True

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
        from_attributes  = True

class CategoryListWithSubcategories(BaseModel):
    categories: List[CategoryInDB]
    

class IconType(str, Enum):
    FEATHER = "feather"
    EMOJI = "emoji"
    UPLOAD = "upload"

class UnifiedCategorySubcategoryCreate(BaseModel):
    category_name: str = Field(..., min_length=2, max_length=100, example="Food & Drinks")
    category_description: Optional[str] = Field(None, max_length=255, example="Eating out, delivery, etc.")
    
    subcategory_name: str = Field(..., min_length=1, max_length=100, example="Pizza")
    subcategory_icon_type: IconType = Field(..., example="feather")
    subcategory_icon_value: str = Field(..., max_length=300000, example="pizza") 
    
    is_reimbursable: bool = Field(default=False)
    exclude_from_budget: bool = Field(default=False)
    
    @validator('subcategory_icon_value')
    def validate_icon_value(cls, v, values):
        icon_type = values.get('subcategory_icon_type')
        if icon_type == IconType.FEATHER:
            if not v.replace('-', '').replace('_', '').isalnum():
                raise ValueError('Feather icon names should only contain letters, numbers, hyphens, and underscores')
        elif icon_type == IconType.EMOJI:
            if len(v) > 10:
                raise ValueError('Emoji value too long')
        elif icon_type == IconType.UPLOAD:
            if not v.startswith('data:image/svg+xml;base64,') and not v.startswith('<svg'):
                raise ValueError('Upload must be a valid SVG (base64 or raw SVG)')
        return v

class UnifiedCategorySubcategoryResponse(BaseModel):
    """Response after creating category and subcategory"""
    category: CategoryInDB
    subcategory: SubCategoryInDB
    created_new_category: bool = Field(..., description="Whether a new category was created")
    
    class Config:
        from_attributes  = True