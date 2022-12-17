from fastapi import FastAPI, status, Query
import uvicorn

from database import register_engine

from fastapi.encoders import jsonable_encoder
from typing import List, Union

from validation_schema.validate import Register, Delete

from database.operations import DataBaseOperations
from database.register_engine import DimensionFinanceTable


register_engine.create_database_engine()

# FastAPI app
app = FastAPI()


@app.get("/health")
def root():
    return {"message": "It is working!"}


@app.get("/budget/", status.HTTP_200_OK)
def read_budget(items: Union[List[int], None] = Query(default=[1])):
    register = DataBaseOperations()
    response = register.get_instance(items, DimensionFinanceTable)
    return response


@app.post("/budget/register", status_code=status.HTTP_201_CREATED)
def register(data: Register):
    data_transformed = jsonable_encoder(data)

    dimension_finance_table_instance = DimensionFinanceTable(
        category_id=data_transformed.get("category_id"),
        category_name=data_transformed.get("category_name"),
        budget_type=data_transformed.get("budget_type"),
        budget=data_transformed.get("budget"),
    )

    register = DataBaseOperations()
    response = register.create_instance(dimension_finance_table_instance)
    return f"Register was created: {response}"


@app.put("/update", status_code=status.HTTP_201_CREATED)
def update(data: Register):
    data_transformed = jsonable_encoder(data)
    register = DataBaseOperations()
    response = register.update_instance(data_transformed, DimensionFinanceTable)
    return response


@app.delete("/budget/category/delete", status_code=status.HTTP_200_OK)
def delete(data: Delete):
    register = DataBaseOperations()
    data_transformed = jsonable_encoder(data)
    response = register.delete_instance(data_transformed, DimensionFinanceTable)
    return f" These registers were deleted: {response}"


if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=5000, reload=True, workers=1)
