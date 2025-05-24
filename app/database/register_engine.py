from typing import Type

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base

# Creating database engine
engine = create_engine("postgresql://postgres:postgres@localhost:5432/assistant_db")

Base: Type = declarative_base()


class DimensionSpendFinance(Base):
    __tablename__ = "dimension_finance"
    category_id = Column(Integer, primary_key=True, autoincrement=True)
    category_name = Column(String, nullable=False)
    budget = Column(Float, nullable=False)

    def to_dict(self) -> dict:
        return {
            "category_id": self.category_id,
            "category_name": self.category_name,
            "budget": self.budget,
        }


class FactTransactionFinance(Base):
    __tablename__ = "fact_finance"
    transaction_id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(
        Integer, ForeignKey("dimension_finance.category_id"), nullable=False
    )
    tag = Column(String, nullable=False)
    datetime_transaction = Column(DateTime, nullable=False)
    credit_card = Column(String, nullable=False)
    amount = Column(Float, nullable=False)

    def to_dict(self) -> dict:
        return {
            "transaction_id": self.transaction_id,
            "category_id": self.category_id,
            "tag": self.tag,
            "datetime_transaction": self.datetime_transaction,
            "credit_card": self.credit_card,
            "amount": self.amount
        }


def create_database_engine() -> None:
    """
    Function responsible to create a database engine
    Args: None
    Return: None
    """
    Base.metadata.create_all(engine)
