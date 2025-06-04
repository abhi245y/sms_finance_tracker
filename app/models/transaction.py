from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Enum as SQLAlchemyEnum
from sqlalchemy.sql import func
import enum

from app.db.base_class import Base

class TransactionStatus(str, enum.Enum):
    PENDING_CATEGORIZATION = "pending_categorization"
    PROCESSED = "processed"
    ERROR = "error"

class Transaction(Base):
    id = Column(Integer, primary_key=True, index=True)
    raw_sms_content = Column(Text, nullable=False)
    received_at = Column(DateTime(timezone=True), server_default=func.now())
    # Parsed fields (to be filled later or by user)
    amount = Column(Float, nullable=True)
    currency = Column(String(10), nullable=True, default="INR") # Assuming INR mostly
    transaction_type = Column(String(50), nullable=True) # e.g., "CC", "Savings", "UPI"
    account_identifier = Column(String(100), nullable=True) # e.g., "CC_HDFC_1234", "SB_ICICI_5678"
    category = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    status = Column(SQLAlchemyEnum(TransactionStatus), nullable=False, default=TransactionStatus.PENDING_CATEGORIZATION)
    # Could add: merchant_name, transaction_date_from_sms, etc.