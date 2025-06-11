from sqlalchemy.orm import Session
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate, TransactionUpdate

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
        # Fields from the TransactionCreate schema
        unique_hash=obj_in.unique_hash,
        raw_sms_content=obj_in.raw_sms_content,
        amount=obj_in.amount,
        currency=obj_in.currency,
        merchant_vpa=obj_in.merchant_vpa,
        transaction_datetime_from_sms=obj_in.transaction_datetime_from_sms,
        description=obj_in.description,
        status=obj_in.status,
        
        # The crucial foreign keys
        account_id=obj_in.account_id,
        category_id=obj_in.category_id        
    )
    
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
    
    return db_obj

def get_transaction(db: Session, id: int) -> Transaction | None:
    return db.query(Transaction).filter(Transaction.id == id).first()

def get_transactions(db: Session, skip: int = 0, limit: int = 100) -> list[Transaction]:
    return db.query(Transaction).order_by(Transaction.received_at.desc()).offset(skip).limit(limit).all()

def get_transaction_by_hash(db: Session, *, hash_str: str) -> Transaction:
    return db.query(Transaction).filter(Transaction.unique_hash == hash_str).first()

