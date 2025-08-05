from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Any, Optional, List

from app.crud import crud_category, crud_subcategory 
from app.schemas.category import (
    CategoryBase,
    CategoryInDB,
    SubCategoryInDB,
    CategoryCreate,
    SubCategoryUpdate,
    UnifiedCategorySubcategoryCreate, 
    UnifiedCategorySubcategoryResponse
)
from app.models.subcategory import SubCategory as SubCategoryModel

from app.api import deps

router = APIRouter()

@router.get(
    "/all_details",
    response_model=List[CategoryInDB],
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
    "/create-with-subcategory",
    response_model=UnifiedCategorySubcategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create category (if needed) and subcategory in one step",
    description="Creates a new subcategory under the specified category. If the category doesn't exist, it will be created first.",
    dependencies=[Depends(deps.get_api_key)]
)
def create_category_and_subcategory(
    *,
    db: Session = Depends(deps.get_db),
    category_data: UnifiedCategorySubcategoryCreate,
) -> Any:
    """
    Create or find a category and create a subcategory under it.
    
    This endpoint handles both scenarios:
    1. Category exists → Just create the subcategory
    2. Category doesn't exist → Create category first, then subcategory
    
    Icon handling:
    - feather: Use feather icon name (e.g., "coffee" becomes "fthr:coffee")
    - emoji: Use emoji character (e.g., "🍕" becomes "emoji:🍕") 
    - upload: Base64 encoded SVG or raw SVG content (becomes "img:custom/filename.svg")
    """
    try:
        existing_category = crud_category.get_category_by_name(db, name=category_data.category_name)
        if existing_category:
            existing_subcat = db.query(SubCategoryModel).filter(
                SubCategoryModel.name == category_data.subcategory_name,
                SubCategoryModel.parent_category_id == existing_category.id
            ).first()
            
            if existing_subcat:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Subcategory '{category_data.subcategory_name}' already exists under category '{category_data.category_name}'"
                )
        
        category, subcategory, created_new_category = crud_category.create_category_with_subcategory(
            db=db, obj_in=category_data
        )
        
        db.refresh(category)
        db.refresh(subcategory)
        
        category_response = CategoryInDB.model_validate(category)
        subcategory_response = SubCategoryInDB.model_validate(subcategory)
        
        return UnifiedCategorySubcategoryResponse(
            category=category_response,
            subcategory=subcategory_response,
            created_new_category=created_new_category
        )
        
    except ValueError as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )


@router.post(
    "/",
    response_model=CategoryCreate, 
    status_code=status.HTTP_201_CREATED,
    summary="Create a new category",
)
def create_new_category(
    *,
    db: Session = Depends(deps.get_db),
    category_in: CategoryCreate,
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
    response_model=List[CategoryInDB],
    status_code=status.HTTP_201_CREATED,
    summary="Create multiple categories in bulk",
    description="Accepts a list of category names to create. Skips duplicates if they already exist."
)
def create_new_categories_bulk(
    *,
    db: Session = Depends(deps.get_db),
    categories_in: List[CategoryInDB],
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
    response_model=CategoryBase,
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
    response_model=CategoryInDB, 
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
    return category



@router.get(
    "/subcategories/{subcategory_id}",
    response_model=SubCategoryInDB,
    summary="Get a single subcategory by ID"
)
def get_subcategory_by_id(
    subcategory_id: int,
    db: Session = Depends(deps.get_db),
    # Add security if needed, e.g., dependencies=[Depends(deps.get_api_key)]
) -> Any:
    """Retrieve details for a specific subcategory."""
    subcategory = crud_subcategory.get_subcategory(db=db, subcategory_id=subcategory_id)
    if not subcategory:
        raise HTTPException(status_code=404, detail="Subcategory not found")
    return subcategory

@router.patch(
    "/subcategories/{subcategory_id}",
    response_model=SubCategoryInDB,
    summary="Update a subcategory",
)
def update_single_subcategory(
    subcategory_id: int,
    *,
    db: Session = Depends(deps.get_db),
    subcategory_in: SubCategoryUpdate,
    dependencies=[Depends(deps.get_api_key)]
) -> Any:
    """Update a subcategory's flags (e.g., is_reimbursable)."""
    db_subcategory = crud_subcategory.get_subcategory(db=db, subcategory_id=subcategory_id)
    if not db_subcategory:
        raise HTTPException(status_code=404, detail="Subcategory not found")
    
    updated_subcategory = crud_subcategory.update_subcategory(
        db=db, db_obj=db_subcategory, obj_in=subcategory_in
    )
    return updated_subcategory