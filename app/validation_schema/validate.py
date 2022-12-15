from pydantic import BaseModel
from typing import List

# Schema to Register and Update
class Register(BaseModel):
    category_id: int
    category_name: str
    subcategory_id: int
    subcategory_name: str
    budget: float


# Schema to a List of Register
class ListRegister(BaseModel):
    registers: List[Register]


# Schema to Delete
class Delete(BaseModel):
    category_id: int
