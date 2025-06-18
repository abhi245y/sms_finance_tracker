# app/crud/crud_subcategory.py
from sqlalchemy.orm import Session, selectinload
from typing import Optional, List
from app.models.subcategory import SubCategory as SubCategoryModel
from app.schemas.category import SubCategoryCreate

def get_subcategory(db: Session, subcategory_id: int) -> Optional[SubCategoryModel]:
    """Get a single subcategory by its ID, optionally loading its parent."""
    return db.query(SubCategoryModel)\
        .options(selectinload(SubCategoryModel.parent_category))\
        .filter(SubCategoryModel.id == subcategory_id)\
        .first()

def get_subcategories_for_parent(db: Session, parent_category_id: int) -> List[SubCategoryModel]:
    """Get all subcategories for a given parent category, ordered."""
    return db.query(SubCategoryModel)\
        .filter(SubCategoryModel.parent_category_id == parent_category_id)\
        .order_by(SubCategoryModel.display_order, SubCategoryModel.name)\
        .all()

def create_subcategory(db: Session, obj_in: SubCategoryCreate) -> SubCategoryModel:
    db_obj = SubCategoryModel(**obj_in.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj