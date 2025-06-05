from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Any

from app.crud import crud_category
from app.schemas import category as category_schema # Import category schemas (e.g., CategoryNamesList, Category, CategoryCreate)
from app.api import deps

router = APIRouter()

@router.get(
    "/",
    response_model=category_schema.CategoryNamesList,
    summary="Get a list of all category names",
    description="Returns a JSON object containing a list of all category names, intended for populating selection menus."
)
def read_category_names(
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

# Optional: Add more endpoints for full category management if needed later.
# For example, to create a new category (you'd need to secure this endpoint):
@router.post(
    "/",
    response_model=category_schema.Category, # Returns the created category object
    status_code=status.HTTP_201_CREATED,
    summary="Create a new category",
    # dependencies=[Depends(deps.get_current_active_superuser)] # TODO Secure this
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
    # dependencies=[Depends(deps.get_current_active_superuser)] # Example: Secure this
)
def create_new_categories_bulk(
    *,
    db: Session = Depends(deps.get_db),
    categories_in: category_schema.CategoryCreateBulk, # Expects {"categories": [{"name": "Cat1"}, {"name": "Cat2"}]}
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
    "/{category_id}",
    response_model=category_schema.Category,
    summary="Get a specific category by ID"
)
def read_category_by_id(
    category_id: int,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get a specific category by its ID.
    """
    category = crud_category.get_category(db=db, category_id=category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {category_id} not found.",
        )
    return category
