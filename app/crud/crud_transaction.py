from sqlalchemy.orm import Session
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate, TransactionUpdate

def create_transaction(db: Session, *, obj_in: TransactionCreate) -> Transaction:
    db_obj = Transaction(
        raw_sms_content=obj_in.raw_sms_content,
        # Initially, we might only have raw_sms_content
        # Other fields can be updated later by parsing or user input
        amount=obj_in.amount,
        currency=obj_in.currency,
        transaction_type=obj_in.transaction_type,
        account_identifier=obj_in.account_identifier,
        category=obj_in.category,
        description=obj_in.description,
        status=obj_in.status
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def get_transaction(db: Session, id: int) -> Transaction | None:
    return db.query(Transaction).filter(Transaction.id == id).first()

def get_transactions(db: Session, skip: int = 0, limit: int = 100) -> list[Transaction]:
    return db.query(Transaction).order_by(Transaction.received_at.desc()).offset(skip).limit(limit).all()

# Add update and delete functions later as needed
