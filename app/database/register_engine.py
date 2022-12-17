from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    ForeignKey,
    DateTime,
)
from sqlalchemy.ext.declarative import declarative_base

import os

path = os.getcwd()

# Creating database engine
engine = create_engine(f"sqlite:///{path}/database/assistant.db")

Base = declarative_base()


class DimensionFinanceTable(Base):
    __tablename__ = "dimension_finance"
    category_id = Column(Integer, primary_key=True)
    category_name = Column(String, nullable=False)
    budget_type = Column(String)
    budget = Column(Float, nullable=False)


class FactTransactionFinance(Base):
    __tablename__ = "fact_finance"
    transaction_id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(
        Integer, ForeignKey("dimension_finance.category_id"), nullable=False
    )
    datetime_transaction = Column(DateTime, nullable=False)
    amount = Column(Float, nullable=False)


def create_database_engine() -> None:
    """
    Function responsible to create a database engine
    Args: None
    Return: None
    """
    Base.metadata.create_all(engine)
