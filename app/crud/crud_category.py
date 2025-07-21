from sqlalchemy.orm import Session, selectinload
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.exc import IntegrityError

from app.models.category import Category as CategoryModel
from app.models.subcategory import SubCategory as SubCategoryModel 
from app.schemas.category import CategoryCreate, CategoryUpdate 

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
# You would place these in a new app/crud/crud_subcategory.py file and import from there.
# For brevity here, I'm including a minimal get_subcategory.

def get_subcategory(db: Session, subcategory_id: int) -> Optional[SubCategoryModel]:
    """Get a single subcategory by its ID, optionally loading its parent."""
    return db.query(SubCategoryModel)\
        .options(selectinload(SubCategoryModel.parent_category))\
        .filter(SubCategoryModel.id == subcategory_id)\
        .first()
# --- CREATE Operation ---
# (create_category, create_multiple_categories remain largely the same,
#  but ensure they handle new fields like description, display_order if CategoryCreate schema is updated)

def create_category(db: Session, *, obj_in: CategoryCreate) -> CategoryModel:
    """
    Create a new category.
    'obj_in' is a Pydantic schema (CategoryCreate).
    """
    db_obj = CategoryModel(**obj_in.model_dump())
    # If your CategoryCreate schema had more fields, you'd map them here:
    # db_obj = CategoryModel(**obj_in.model_dump()) # If CategoryModel fields match CategoryCreate fields
    
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

# --- UPDATE Operation ---
# Not strictly needed for the Shortcut's GET request, but good for completeness.

def update_category(
    db: Session,
    *,
    db_obj: CategoryModel, # The existing category ORM object to update
    obj_in: CategoryUpdate # Pydantic schema with fields to update
) -> CategoryModel:
    """
    Update an existing category.
    'db_obj' is the SQLAlchemy model instance.
    'obj_in' is a Pydantic schema (CategoryUpdate) or a dict.
    """
    update_data = obj_in.model_dump(exclude_unset=True) # Get only fields that were actually provided
    
    for field, value in update_data.items():
        setattr(db_obj, field, value)
        
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

# --- DELETE Operation ---
# Not strictly needed for current plan, but good for completeness.

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
