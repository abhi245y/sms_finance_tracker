from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    display_order = Column(Integer, nullable=False, default=0, server_default='0')
    subcategories = relationship("SubCategory", back_populates="parent_category", order_by="SubCategory.display_order")


    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}')>"