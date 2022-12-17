from pydantic import BaseModel
from typing import List

# Schema to Register and Update
class Register(BaseModel):
    category_id: int
    category_name: str
    budget_type: str
    budget: float


# Schema to Delete
class Delete(BaseModel):
    category_id: int


class Category(BaseModel):
    category_id: int


class ListCategory(BaseModel):
    categories_ids: List[Category]
