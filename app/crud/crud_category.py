from sqlalchemy.orm import Session, selectinload
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from typing import List, Optional, Dict, Any, Tuple


from app.models.category import Category as CategoryModel
from app.models.subcategory import SubCategory as SubCategoryModel 
from app.schemas.category import CategoryCreate, CategoryUpdate 

from app.services.icon_handler import IconHandler
from app.schemas.category import UnifiedCategorySubcategoryCreate, SubCategoryCreate
from app.crud.crud_subcategory import create_subcategory

# --- READ Operations ---

def get_category(db: Session, category_id: int) -> Optional[CategoryModel]:
    return db.query(CategoryModel).filter(CategoryModel.id == category_id).first()

def get_category_by_name(db: Session, name: str) -> Optional[CategoryModel]:
    return db.query(CategoryModel).filter(CategoryModel.name == name).first()

def get_categories(db: Session, skip: int = 0, limit: int = 100) -> List[CategoryModel]:
    """
    Get a list of all categories, with pagination, and eagerly load their subcategories.
    Subcategories are ordered by their display_order.
    Categories are ordered by their display_order.
    """
    return db.query(CategoryModel)\
        .options(selectinload(CategoryModel.subcategories))\
        .order_by(CategoryModel.display_order, CategoryModel.name)\
        .offset(skip)\
        .limit(limit)\
        .all()

def get_all_category_names(db: Session) -> List[str]:
    results = db.query(CategoryModel.name).order_by(CategoryModel.name).all()
    return [result[0] for result in results]

# --- SubCategory CRUD (Minimal as discussed, primarily for get_subcategory for now) ---

def get_subcategory(db: Session, subcategory_id: int) -> Optional[SubCategoryModel]:
    """Get a single subcategory by its ID, optionally loading its parent."""
    return db.query(SubCategoryModel)\
        .options(selectinload(SubCategoryModel.parent_category))\
        .filter(SubCategoryModel.id == subcategory_id)\
        .first()
        
# --- CREATE Operation ---

def create_category(db: Session, *, obj_in: CategoryCreate) -> CategoryModel:
    """
    Create a new category.
    'obj_in' is a Pydantic schema (CategoryCreate).
    """
    db_obj = CategoryModel(name=obj_in.name)
    # If your CategoryCreate schema had more fields, you'd map them here:
    # db_obj = CategoryModel(**obj_in.dict()) # If CategoryModel fields match CategoryCreate fields
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def create_multiple_categories(db: Session, *, categories_in: List[CategoryCreate]) -> Tuple[List[CategoryModel], List[Dict[str, Any]]]:
    """
    Create multiple new categories.
    Skips categories that already exist by name.
    Returns a tuple: (list_of_successfully_created_categories, list_of_errors)
    """
    created_categories_db: List[CategoryModel] = []
    errors: List[Dict[str, Any]] = []

    for cat_in in categories_in:
        existing_category = get_category_by_name(db, name=cat_in.name)
        if existing_category:
            errors.append({"name": cat_in.name, "detail": "Category with this name already exists."})
            continue

        try:
            created_db_obj = CategoryModel(name=cat_in.name)
            db.add(created_db_obj)
            db.flush()
            db.refresh(created_db_obj)
            created_categories_db.append(created_db_obj)

        except IntegrityError as e:
            db.rollback()
            errors.append({"name": cat_in.name, "detail": f"Database integrity error: {e.orig}"})
        except Exception as e:
            db.rollback()
            errors.append({"name": cat_in.name, "detail": f"An unexpected error occurred: {str(e)}"})
    
    db.commit()
    for cat in created_categories_db:
        db.refresh(cat)

    return created_categories_db, errors

def create_category_with_subcategory(
    db: Session, 
    *, 
    obj_in: UnifiedCategorySubcategoryCreate
) -> Tuple[CategoryModel, SubCategoryModel, bool]:
    """
    Create or find category and create subcategory under it.
    
    Args:
        db: Database session
        obj_in: Unified creation schema
        
    Returns:
        Tuple of (category_model, subcategory_model, created_new_category)
    """
    icon_handler = IconHandler()
    created_new_category = False
    
    existing_category = get_category_by_name(db, name=obj_in.category_name)
    
    if existing_category:
        category = existing_category
    else:
        category_create_data = CategoryCreate(
            name=obj_in.category_name,
            description=obj_in.category_description or f"Custom category: {obj_in.category_name}",
            display_order=999  
        )
        category = create_category(db=db, obj_in=category_create_data)
        created_new_category = True
    
    try:
        processed_icon_name = icon_handler.process_icon(
            icon_type=obj_in.subcategory_icon_type.value,
            icon_value=obj_in.subcategory_icon_value
        )
    except ValueError as e:
        raise ValueError(f"Icon processing failed: {str(e)}")
    
    max_display_order = db.query(func.max(SubCategoryModel.display_order))\
        .filter(SubCategoryModel.parent_category_id == category.id)\
        .scalar() or 0
        
    subcategory_create_data = SubCategoryCreate(
        name=obj_in.subcategory_name,
        icon_name=processed_icon_name,
        display_order=max_display_order + 1,
        is_reimbursable=obj_in.is_reimbursable,
        exclude_from_budget=obj_in.exclude_from_budget,
        parent_category_id=category.id
    )
    
    subcategory = create_subcategory(db=db, obj_in=subcategory_create_data)
    
    return category, subcategory, created_new_category

# --- UPDATE Operation ---

def update_category(
    db: Session,
    *,
    db_obj: CategoryModel, 
    obj_in: CategoryUpdate 
) -> CategoryModel:
    """
    Update an existing category.
    'db_obj' is the SQLAlchemy model instance.
    'obj_in' is a Pydantic schema (CategoryUpdate) or a dict.
    """
    update_data = obj_in.dict(exclude_unset=True) 
    
    for field, value in update_data.items():
        setattr(db_obj, field, value)
        
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

# --- DELETE Operation ---

def delete_category(db: Session, *, category_id: int) -> Optional[CategoryModel]:
    """
    Delete a category by ID.
    Returns the deleted category object or None if not found.
    """
    db_obj = db.query(CategoryModel).filter(CategoryModel.id == category_id).first()
    if db_obj:
        db.delete(db_obj)
        db.commit()
    return db_obj
