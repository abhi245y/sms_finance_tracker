from sqlalchemy.orm import Session, selectinload
from app.models import Transaction, SubCategory, Category

from app.schemas.transaction import TransactionCreate, TransactionUpdate 


DEFAULT_UNCATEGORIZED_SUBCATEGORY_ID = 1000


def get_default_uncategorized_subcategory_id(db: Session) -> int:
    """
    Retrieves the ID of the 'Uncategorized' subcategory under the 'General' category.
    This is a simplified example. You might want to make this more robust,
    e.g., by having fixed IDs in your seed or querying by name.
    """

    general_category = db.query(SubCategory.parent_category_id).join(SubCategory.parent_category).filter(Category.name == "General").first()
    if not general_category:
        raise Exception("Default 'General' category not found. Please seed the database.")
    
    uncategorized_subcat = db.query(SubCategory).filter(
        SubCategory.name == "Uncategorized",
        SubCategory.parent_category_id == general_category.parent_category_id
    ).first()

    if not uncategorized_subcat:
        print(f"WARNING: 'Uncategorized' subcategory under 'General' not found dynamically. Falling back to ID: {DEFAULT_UNCATEGORIZED_SUBCATEGORY_ID}")
        print("Please ensure your database is seeded correctly with a 'General' category and an 'Uncategorized' subcategory under it.")
        return DEFAULT_UNCATEGORIZED_SUBCATEGORY_ID 
    return uncategorized_subcat.id



def create_transaction(db: Session, *, obj_in: TransactionCreate) -> Transaction:
    """
    Create a new transaction record in the database.

    Args:
        db: The database session.
        obj_in: A Pydantic model containing all necessary data for a new transaction.
    
    Returns:
        The newly created SQLAlchemy Transaction object.
    """
    db_obj = Transaction(
        unique_hash=obj_in.unique_hash,
        raw_sms_content=obj_in.raw_sms_content,
        amount=obj_in.amount,
        currency=obj_in.currency,
        merchant_vpa=obj_in.merchant_vpa,
        transaction_datetime_from_sms=obj_in.transaction_datetime_from_sms,
        description=obj_in.description,
        status=obj_in.status, 
        account_id=obj_in.account_id,
        # exclude_from_cashflow=obj_in.exclude_from_cashflow       
    )
    
    if obj_in.subcategory_id is None:
        db_obj.subcategory_id = get_default_uncategorized_subcategory_id(db)
    else:
        if not db.query(SubCategory).filter(SubCategory.id == obj_in.subcategory_id).first():
            print(f"WARNING: Provided subcategory_id {obj_in.subcategory_id} not found. Defaulting to Uncategorized.")
            db_obj.subcategory_id = get_default_uncategorized_subcategory_id(db)
        else:
            db_obj.subcategory_id = obj_in.subcategory_id
    
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update_transaction(
    db: Session,
    *,
    db_obj: Transaction,  
    obj_in: TransactionUpdate
) -> Transaction:
    """
    Update an existing transaction.

    Args:
        db: The database session.
        db_obj: The current transaction object to be updated.
        obj_in: A Pydantic model containing the fields to update.

    Returns:
        The updated transaction object.
    """

    update_data = obj_in.dict(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_obj, field, value)

    db.add(db_obj) 
    db.commit() 
    db.refresh(db_obj)
    
    return get_transaction_by_hash(db, hash_str=db_obj.unique_hash, include_relations=True)

def update_transaction_message_id(db: Session, *, transaction_obj: Transaction, message_id: int) -> Transaction:
    """Updates only the telegram_message_id of a transaction."""
    transaction_obj.telegram_message_id = message_id
    db.add(transaction_obj)
    db.commit()
    db.refresh(transaction_obj)
    return transaction_obj

def _get_transaction_query(db: Session, include_relations: bool = True):
    query = db.query(Transaction)
    if include_relations:
        query = query.options(
            selectinload(Transaction.account), 
            selectinload(Transaction.subcategory).selectinload(SubCategory.parent_category)
        )
    return query

# def get_transaction(db: Session, id: int) -> Transaction | None:
#     return db.query(Transaction).options(
#         joinedload(Transaction.account),
#         joinedload(Transaction.category_obj)
#     ).filter(Transaction.id == id).first()

def get_transaction(db: Session, id: int, include_relations: bool = True) -> Transaction | None:
    return _get_transaction_query(db, include_relations).filter(Transaction.id == id).first()

def get_transactions(db: Session, skip: int = 0, limit: int = 100, include_relations: bool = True) -> list[Transaction]:
    return _get_transaction_query(db, include_relations)\
        .order_by(Transaction.received_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()

def get_transaction_by_hash(db: Session, *, hash_str: str, include_relations: bool = True) -> Transaction | None:
    return _get_transaction_query(db, include_relations).filter(Transaction.unique_hash == hash_str).first()

# def get_transactions(db: Session, skip: int = 0, limit: int = 100) -> list[Transaction]:
#     return db.query(Transaction).options(
#         joinedload(Transaction.account),
#         joinedload(Transaction.category_obj)
#     ).order_by(Transaction.received_at.desc()).offset(skip).limit(limit).all()

# def get_transaction_by_hash(db: Session, *, hash_str: str) -> Transaction | None:
#     return db.query(Transaction).options(
#         joinedload(Transaction.account),
#         joinedload(Transaction.category_obj)
#     ).filter(Transaction.unique_hash == hash_str).first()

