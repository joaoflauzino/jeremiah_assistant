from typing import List

from pydantic import BaseModel


# Schema to Register and Update in dimension table
class Register(BaseModel):
    category_name: str
    budget: float


# Schema to Delete in dimension table
class Delete(BaseModel):
    category_name: str


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
