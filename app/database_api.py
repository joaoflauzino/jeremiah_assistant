from typing import Any, List, Union

import uvicorn
from fastapi import FastAPI, Query, status
from fastapi.encoders import jsonable_encoder
from service.spend_limit import SpendService
from service.transactions import TransactionService
from validation_schema.database.validate import (
    Delete,
    DeleteTransaction,
    Register,
    RegisterTransaction,
    RegisterUpdateTransaction,
)

app = FastAPI()


@app.get("/health")
def root():
    return {"message": "It is working!"}


@app.get("/dimension/budget", status_code=status.HTTP_200_OK)
def read_budget(items: Union[List[Any]] = Query(default=[])):
    spend_service = SpendService()
    response_service = spend_service.get(items=items)
    return response_service


@app.post("/dimension/budget", status_code=status.HTTP_201_CREATED)
def add_budget(data: Register) -> str:
    data_decoded = jsonable_encoder(data)
    spend_service = SpendService()
    response_service = spend_service.create(data=data_decoded)
    return f"Register was created: {response_service}"


@app.put("/dimension/budget", status_code=status.HTTP_201_CREATED)
def update_budget(data: Register) -> str:
    data_decoded = jsonable_encoder(data)
    spend_service = SpendService()
    response_service = spend_service.update(data=data_decoded)
    return f"Register was updated: {response_service}"


@app.delete("/dimension/budget", status_code=status.HTTP_200_OK)
def delete_budget(data: Delete):
    data_decoded = jsonable_encoder(data)
    spend_service = SpendService()
    response_service = spend_service.delete(data=data_decoded)
    return f" These registers were deleted: {response_service}"


@app.get("/transaction/budget", status_code=status.HTTP_200_OK)
def read_spent(items: Union[List[Any]] = Query(default=[1])) -> list | str:
    spend_service = SpendService()
    categories_response = spend_service.get(items=items)

    transaction_service = TransactionService()
    categories_id = [category["category_id"] for category in categories_response]
    response_transaction = transaction_service.get(items=categories_id)
    return response_transaction


@app.post("/transaction/budget", status_code=status.HTTP_201_CREATED)
def add_spent(data: RegisterTransaction) -> str:
    data_decoded = jsonable_encoder(data)
    data = {
        "category_id": data_decoded.get("category_id"),
        "tag": data_decoded.get("tag"),
        "credit_card": data_decoded.get("credit_card"),
        "amount": data_decoded.get("amount"),
    }

    transaction_service = TransactionService()
    response_service = transaction_service.create(data=data)
    return response_service


@app.put("/transaction/budget", status_code=status.HTTP_201_CREATED)
def update_spent(data: RegisterUpdateTransaction):
    data_decoded = jsonable_encoder(data)
    transaction_service = TransactionService()
    response_service = transaction_service.update(data=data_decoded)
    return response_service


@app.delete("/transaction/budget", status_code=status.HTTP_200_OK)
def delete_spent(data: DeleteTransaction):
    data_decoded = jsonable_encoder(data)
    transaction_service = TransactionService()
    response_service = transaction_service.delete(data=data_decoded)
    return f" These registers were deleted: {response_service}"


if __name__ == "__main__":
    uvicorn.run("database_api:app", host="0.0.0.0", port=8000, reload=True, workers=1)
