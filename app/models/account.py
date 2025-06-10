import enum
from sqlalchemy import Column, Integer, String, Enum as SQLAlchemyEnum, UniqueConstraint, Index
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class AccountType(str, enum.Enum):
    SAVINGS_ACCOUNT = "savings_account"
    CREDIT_CARD = "credit_card"
    WALLET = "wallet"
    UNKNOWN = "unknown"

class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)

    account_type = Column(SQLAlchemyEnum(AccountType), nullable=False, default=AccountType.UNKNOWN)
    
    bank_name = Column(String(100), nullable=False, index=True)
    account_last4 = Column(String(4), nullable=False, index=True)


    transactions = relationship("Transaction", back_populates="account")


    __table_args__ = (
        UniqueConstraint('bank_name', 'account_last4', name='uq_bank_account_last4'),
        Index('ix_bank_account_last4_composite', 'bank_name', 'account_last4'),
    )

    def __repr__(self):
        return f"<Account(id={self.id}, name='{self.name}', bank='{self.bank_name}', last4='{self.account_last4}')>"