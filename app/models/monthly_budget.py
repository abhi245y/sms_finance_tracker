from sqlalchemy import Column, Integer, Float, UniqueConstraint
from app.db.base_class import Base

class MonthlyBudget(Base):
    __tablename__ = "monthly_budgets"

    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    budget_amount = Column(Float, nullable=False)

    __table_args__ = (UniqueConstraint('year', 'month', name='uq_year_month_budget'),)

    def __repr__(self):
        return f"<MonthlyBudget(id={self.id}, year={self.year}, month={self.month}, budget={self.budget_amount})>"