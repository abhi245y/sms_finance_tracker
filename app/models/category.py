from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)

    # This defines the 'one' side of the 'one-to-many' relationship.
    # 'Transaction' is the class name of the other model.
    # 'back_populates' links to the 'category_obj' attribute in the Transaction model.
    transactions = relationship("Transaction", back_populates="category_obj")


    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}')>"