from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Any, Optional, List

from app.crud import crud_category
from app.schemas import category as category_schema
from app.api import deps

router = APIRouter()

@router.get(
    "/all_details",
    response_model=List[category_schema.CategoryInDB],
    summary="Get all categories with their subcategories",
    description="Returns a list of all categories, each containing its subcategories, ordered by display_order."
)
def read_all_categories_with_details(
    db: Session = Depends(deps.get_db),
    skip: int = 0, 
    limit: int = 100 
) -> Any:
    """
    Retrieve all categories, with their subcategories populated and ordered.
    """
   
    categories = crud_category.get_categories(db=db, skip=skip, limit=limit)
    if not categories:
        return []
    return categories



@router.post(
    "/",
    response_model=category_schema.CategoryCreate, 
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
    response_model=List[category_schema.CategoryInDB],
    status_code=status.HTTP_201_CREATED,
    summary="Create multiple categories in bulk",
    description="Accepts a list of category names to create. Skips duplicates if they already exist."
)
def create_new_categories_bulk(
    *,
    db: Session = Depends(deps.get_db),
    categories_in: List[category_schema.CategoryInDB],
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
    response_model=category_schema.CategoryBase,
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
        
        
@router.get(
    "/{category_id_or_name}", 
    response_model=category_schema.CategoryInDB, 
    summary="Get a specific category by ID or Name with its subcategories"
)
def get_single_category_details(
    category_id_or_name: str,
    db: Session = Depends(deps.get_db),
) -> Any:
    category = None
    try:
        category_id = int(category_id_or_name)
        category = crud_category.get_category(db=db, category_id=category_id)
    except ValueError:
        category = crud_category.get_category_by_name(db=db, name=category_id_or_name) 
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category '{category_id_or_name}' not found.",
        )
    # If get_category doesn't automatically load subcategories due to how it's called,
    # you might need to adjust it or explicitly load them here.
    # However, the updated crud_category.get_categories with selectinload should handle it for lists.
    # For single item, ensure the relationship is loaded.
    # A quick way for a single item if not loaded:
    # if category and not category.subcategories: # Or check if it's an uninitialized loader
    #     category.subcategories = crud_subcategory.get_subcategories_for_parent(db, parent_category_id=category.id)
    return category

