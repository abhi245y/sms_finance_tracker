from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint, Boolean
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class SubCategory(Base):
    __tablename__ = "subcategories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    
    icon_name = Column(String(100), nullable=True)
    display_order = Column(Integer, nullable=False, default=0, server_default='0')
    
    is_reimbursable = Column(Boolean, nullable=False, default=False, server_default='0')
    exclude_from_budget = Column(Boolean, nullable=False, default=False, server_default='0')
    
    parent_category_id = Column(Integer, ForeignKey("categories.id"), nullable=False, index=True)
    parent_category = relationship("Category", back_populates="subcategories") 
    transactions = relationship("Transaction", back_populates="subcategory")
    
    
    __table_args__ = (
        UniqueConstraint('name', 'parent_category_id', name='uq_subcategory_name_parent'),
    )

    def __repr__(self):
        return f"<SubCategory(id={self.id}, name='{self.name}', parent_id={self.parent_category_id})>"
