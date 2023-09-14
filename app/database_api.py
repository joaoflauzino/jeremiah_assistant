from fastapi import FastAPI, status, Query
import uvicorn

from database import register_engine

from fastapi.encoders import jsonable_encoder
from typing import List, Union

from validation_schema.validate import (
    Register,
    Delete,
    RegisterTransaction,
    RegisterUpdateTransaction,
    DeleteTransaction,
)

from database.operations import DataBaseOperations
from database.register_engine import DimensionFinanceTable, FactTransactionFinance

from datetime import datetime


register_engine.create_database_engine()

# FastAPI app
app = FastAPI()


@app.get("/health")
def root():
    return {"message": "It is working!"}


@app.get("/dimension/budget", status_code=status.HTTP_200_OK)
# trunk-ignore(ruff/B008)
def read_budget(items: Union[List[int], None] = Query(default=[1])):
    register = DataBaseOperations()
    rsp = register.get_instance(items, DimensionFinanceTable)
    return rsp[0]


@app.post("/dimension/budget/register", status_code=status.HTTP_201_CREATED)
def register(data: Register):
    data_transformed = jsonable_encoder(data)

    dimension_finance_table_instance = DimensionFinanceTable(
        category_id=data_transformed.get("category_id"),
        category_name=data_transformed.get("category_name"),
        budget_type=data_transformed.get("budget_type"),
        budget=data_transformed.get("budget"),
    )

    register = DataBaseOperations()
    rsp = register.create_instance(dimension_finance_table_instance)
    return f"Register was created: {rsp}"


@app.put("/dimension/budget/update", status_code=status.HTTP_201_CREATED)
def update(data: Register):
    data_transformed = jsonable_encoder(data)
    register = DataBaseOperations()
    rsp = register.update_instance(data_transformed, DimensionFinanceTable)
    return rsp


@app.delete("/dimension/budget/delete", status_code=status.HTTP_200_OK)
def delete(data: Delete):
    register = DataBaseOperations()
    data_transformed = jsonable_encoder(data)
    rsp = register.delete_instance(data_transformed, DimensionFinanceTable)
    return f" These registers were deleted: {rsp}"


@app.get("/transaction/budget/", status_code=status.HTTP_200_OK)
# trunk-ignore(ruff/B008)
def read_transaction(items: Union[List[int], None] = Query(default=[1])):
    register = DataBaseOperations()
    rsp = register.get_instance(items, FactTransactionFinance)
    return rsp


@app.post("/transaction/budget/register", status_code=status.HTTP_201_CREATED)
# trunk-ignore(ruff/F811)
def register(data: RegisterTransaction):
    data_transformed = jsonable_encoder(data)

    transaction_date = datetime.now()

    transaction_finance_table_instance = FactTransactionFinance(
        category_id=data_transformed.get("category_id"),
        datetime_transaction=transaction_date,
        amount=data_transformed.get("amount"),
    )

    register = DataBaseOperations()

    rsp = register.create_instance(transaction_finance_table_instance)
    return f"Register was created: {rsp}"


@app.put("/transaction/budget/update", status_code=status.HTTP_201_CREATED)
# trunk-ignore(ruff/F811)
def update(data: RegisterUpdateTransaction):
    data_transformed = jsonable_encoder(data)
    register = DataBaseOperations()
    rsp = register.update_instance(data_transformed, FactTransactionFinance)
    return rsp


@app.delete("/transaction/budget/delete", status_code=status.HTTP_200_OK)
# trunk-ignore(ruff/F811)
def delete(data: DeleteTransaction):
    register = DataBaseOperations()
    data_transformed = jsonable_encoder(data)
    rsp = register.delete_instance(data_transformed, FactTransactionFinance)
    return f" These registers were deleted: {rsp}"


if __name__ == "__main__":
    uvicorn.run("database_api:app", host="0.0.0.0", port=8000, reload=True, workers=1)
