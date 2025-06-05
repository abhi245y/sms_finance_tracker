from pydantic import BaseModel, Field
from typing import List, Optional

# --- Base Schema ---
class CategoryBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, example="Groceries")

    # Optional: Add description or other fields if needed in the future
    # description: Optional[str] = Field(None, max_length=255, example="Monthly grocery shopping")

# --- Schema for Creating a Category ---
# Used when receiving data to create a new category.
class CategoryCreate(CategoryBase):
    pass # For now, same as CategoryBase

# --- Schema for Creating Multiple Categories ---
class CategoryCreateBulk(BaseModel):
    categories: List[CategoryCreate] = Field(..., min_items=1)

# --- Schema for Updating a Category ---
# Not strictly needed for the current plan, but good to define for completeness.
class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    # description: Optional[str] = Field(None, max_length=255)

# --- Schema for Reading a Category (from DB) ---
# This represents a category as it is stored in the database, including its ID.
class CategoryInDBBase(CategoryBase):
    id: int

    class Config:
        orm_mode = True

class Category(CategoryInDBBase):
    pass # For now, same as CategoryInDBBase

# --- Schema for the API response to the iPhone Shortcut ---
# The Shortcut just needs a list of category names (strings).
class CategoryNamesList(BaseModel):
    category_names: List[str] = Field(..., example=["Food & Dining", "Groceries", "Transport"])
    
# --- Schema for the Response of Bulk Category Creation ---
# This can be a simple list of the created categories or a more detailed report
class CategoryBulkCreateResponse(BaseModel):
    created_categories: List[Category] # Using the 'Category' schema which includes ID
    errors: List[dict] # List of errors, e.g., {"name": "Duplicate Name", "error": "Already exists"}
