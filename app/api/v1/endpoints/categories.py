from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Any, Optional

from app.crud import crud_category
from app.schemas import category as category_schema
from app.api import deps

router = APIRouter()

@router.get(
    "/list",
    response_model=category_schema.CategoryNamesList,
    summary="Get a list of all category names",
    description="Returns a JSON object containing a list of all category names, intended for populating selection menus."
)
def get_category_list(
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Retrieve all category names.
    """
    category_names = crud_category.get_all_category_names(db=db)
    if not category_names:
        # It's okay to return an empty list if no categories exist yet.
        # The client (Shortcut) should handle an empty list gracefully.
        pass
    return {"category_names": category_names}

@router.post(
    "/",
    response_model=category_schema.Category, 
    status_code=status.HTTP_201_CREATED,
    summary="Create a new category",
)
def create_new_category(
    *,
    db: Session = Depends(deps.get_db),
    category_in: category_schema.CategoryCreate,
) -> Any:
    """
    Create a new category.
    """
    existing_category = crud_category.get_category_by_name(db, name=category_in.name)
    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Category with name '{category_in.name}' already exists.",
        )
    category = crud_category.create_category(db=db, obj_in=category_in)
    return category


@router.post(
    "/bulk/",
    response_model=category_schema.CategoryBulkCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create multiple categories in bulk",
    description="Accepts a list of category names to create. Skips duplicates if they already exist."
)
def create_new_categories_bulk(
    *,
    db: Session = Depends(deps.get_db),
    categories_in: category_schema.CategoryCreateBulk,
) -> Any:
    """
    Create multiple new categories in a single request.
    """
    if not categories_in.categories:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The list of categories cannot be empty.",
        )
    created_db_categories, errors = crud_category.create_multiple_categories(db=db, categories_in=categories_in.categories)
    
    return {"created_categories": created_db_categories, "errors": errors}


@router.get(
    "/",
    response_model=category_schema.Category,
    summary="Get a specific category by ID or Name"
)
def get_category(
    category_name: Optional[str] = None, 
    category_id: Optional[int] = None,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get a specific category by its ID or Name.
    """
    category = None
    if category_name:
        category = crud_category.get_category_by_name(db=db, name=category_name)
    elif category_id:
         category = crud_category.get_category(db=db, category_id=category_id)
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Please specify either Category ID or Name",
        )
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID: {category_id} or Name: {category_name} not found.",
        )
    return category
        
        


