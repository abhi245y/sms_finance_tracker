from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.exc import IntegrityError

from app.models.category import Category as CategoryModel
from app.schemas.category import CategoryCreate, CategoryUpdate

# --- READ Operations ---

def get_category(db: Session, category_id: int) -> Optional[CategoryModel]:
    """
    Get a single category by its ID.
    """
    return db.query(CategoryModel).filter(CategoryModel.id == category_id).first()

def get_category_by_name(db: Session, name: str) -> Optional[CategoryModel]:
    """
    Get a single category by its name.
    """
    return db.query(CategoryModel).filter(CategoryModel.name == name).first()

def get_categories(db: Session, skip: int = 0, limit: int = 100) -> List[CategoryModel]:
    """
    Get a list of all categories, with pagination.
    """
    return db.query(CategoryModel).order_by(CategoryModel.name).offset(skip).limit(limit).all()

def get_all_category_names(db: Session) -> List[str]:
    """
    Get a list of all category names.
    This is what the Shortcut will primarily use.
    """
    # query(CategoryModel.name) selects only the 'name' column.
    # .all() returns a list of tuples, e.g., [('Food',), ('Groceries',)].
    # We use a list comprehension to flatten it.
    results = db.query(CategoryModel.name).order_by(CategoryModel.name).all()
    return [result[0] for result in results]

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
    update_data = obj_in.dict(exclude_unset=True) # Get only fields that were actually provided
    
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
