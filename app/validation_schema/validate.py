from pydantic import BaseModel
from typing import List
from datetime import datetime


# Schema to Register and Update in dimension credit card table


class RegisterCreditCard(BaseModel):
    card_id: int
    card_name: str
    closing_date: str
    card_limit: float
    record_status: int


class DeleteCreditCard(BaseModel):
    card_id: int


# Schema to Register and Update in dimension table
class Register(BaseModel):
    category_id: int
    category_name: str
    budget_type: str
    budget: float


# Schema to Delete in dimension table
class Delete(BaseModel):
    category_id: int


# Schema to Select in dimension table
class Category(BaseModel):
    category_id: int


# Schema to Select in dimension table
class ListCategory(BaseModel):
    categories_ids: List[Category]


# Schema to register a transcation in fact table
class RegisterTransaction(BaseModel):
    category_id: int
    amount: float


class RegisterUpdateTransaction(BaseModel):
    transaction_id: int
    category_id: int
    amount: float


class DeleteTransaction(BaseModel):
    transaction_id: int
