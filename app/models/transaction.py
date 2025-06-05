from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Enum as SQLAlchemyEnum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.db.base_class import Base

class TransactionStatus(str, enum.Enum):
    PENDING_CATEGORIZATION = "pending_categorization"
    PROCESSED = "processed"
    ERROR = "error"

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    raw_sms_content = Column(Text, nullable=False)
    received_at = Column(DateTime(timezone=True), server_default=func.now())
    # Parsed fields (to be filled later or by user)
    amount = Column(Float, nullable=True)
    currency = Column(String(10), nullable=True, default="INR") # Assuming INR mostly
    transaction_type = Column(String(50), nullable=True) # e.g., "CC", "Savings", "UPI"
    account_identifier = Column(String(100), nullable=True) # e.g., "CC_HDFC_1234", "SB_ICICI_5678"
    description = Column(Text, nullable=True)
    status = Column(SQLAlchemyEnum(TransactionStatus), nullable=False, default=TransactionStatus.PENDING_CATEGORIZATION)
    bank_name = Column(String(100), nullable=True)
    merchant_vpa = Column(String(255), nullable=True)
    transaction_datetime_from_sms = Column(DateTime(timezone=True), nullable=True)
    
    # --- Category Relationship ---
    # This field stores the ID of the related category.
    # "categories.id" refers to the 'id' column in the 'categories' table.
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True, index=True)
    
    # This defines the 'many' side of the 'one-to-many' relationship.
    # 'Category' is the class name of the other model.
    # 'back_populates' links to the 'transactions' attribute in the Category model.
    category_obj = relationship("Category", back_populates="transactions")

    
    def __repr__(self):
        return f"<Transaction(id={self.id}, amount={self.amount}, category_id={self.category_id})>"