from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, Text, Enum as SQLAlchemyEnum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum

from app.db.base_class import Base
from .subcategory import SubCategory
from .account import Account

class TransactionStatus(str, Enum):
    PENDING_ACCOUNT_SELECTION = "pending_account_selection"
    PENDING_CATEGORIZATION = "pending_categorization" 
    PENDING_PROCESSING = "pending_processing" 
    
    PROCESSED = "processed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ERROR = "error"


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    unique_hash = Column(String(64), unique=True, index=True, nullable=False)
    telegram_message_id = Column(Integer, nullable=True, index=True)
    
    linked_transaction_hash = Column(String(64), nullable=True, index=True)
    override_reimbursable = Column(Boolean, nullable=True, default=None)
    
    raw_sms_content = Column(Text, nullable=False)
    received_at = Column(DateTime(timezone=True), server_default=func.now())
    amount = Column(Float, nullable=True)
    currency = Column(String(10), nullable=True, default="INR")
    merchant_vpa = Column(String(255), nullable=True)
    transaction_datetime_from_sms = Column(DateTime(timezone=True), nullable=True)
    
    description = Column(Text, nullable=True)
    status = Column(SQLAlchemyEnum(TransactionStatus), nullable=False, default=TransactionStatus.PENDING_PROCESSING)

    subcategory_id = Column(Integer, ForeignKey("subcategories.id"), nullable=False)
    subcategory = relationship("SubCategory", back_populates="transactions")

    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False, index=True)
    account = relationship("Account", back_populates="transactions")
    
    def __repr__(self):
        return f"<Transaction(id={self.id}, amount={self.amount}, subcategory_id={self.subcategory_id}, account_id={self.account_id})>"