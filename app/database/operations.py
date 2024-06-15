from typing import List, Union

from database.register_engine import (
    DimensionFinanceTable,
    FactTransactionFinance,
    engine,
)
from fastapi import HTTPException
from sqlalchemy.orm import Query, Session


class DataBaseOperations(object):
    def __init__(self) -> None:
        self.session = Session(bind=engine, expire_on_commit=False)

    # trunk-ignore(ruff/D417)
    def create_instance(self, TableObject: Union[DimensionFinanceTable, FactTransactionFinance]) -> str:
        """
        Responsible to create database instance.

        Args:
        ----
            TableObject (object): SqlAlchemy table object.

        Return:
        ------
            (str): returns a message showing which category was inserted.
        """
        self.session.add(TableObject)
        self.session.commit()
        self.session.close()

        return f"A instance was created. Category: {TableObject.category_id}"

    # trunk-ignore(ruff/D417)
    def get_instance(
        self, items: List[str], TableObject: Union[DimensionFinanceTable, FactTransactionFinance]
    ) -> List[dict]:
        """
        Responsible to get database instance.

        Args:
        ----
            Items (list): a list of itens.
            TableObject (object): SqlAlchemy table object.

        Return:
        ------
            (dict): Database instance.
        """
        if not items:
            return self.session.query(TableObject).all()

        found_registers: Query = self.session.query(TableObject).filter(TableObject.category_name.in_(items))  # type: ignore

        if found_registers.all():
            self.session.commit()
            self.session.close()
            return found_registers.all()

        raise HTTPException(
            status_code=404,
            detail=f"Categories or transactions {items} were not found",
        )

    # trunk-ignore(ruff/D417)
    def update_instance(self, data: dict, TableObject: Union[DimensionFinanceTable, FactTransactionFinance]) -> str:
        """
        Responsible to update database instance.

        Args:
        ----
            data (dict): a dict to update instance.
            TableObject (object): SqlAlchemy table object.

        Return:
        ------
            (str): A message showing the updated register.
        """

        key = "category_id"

        query: Query = self.session.query(TableObject).filter(TableObject.category_name == data.get("category_name"))

        if query.all():
            category_id = query.all()[0].category_id
            data.update({"category_id": category_id})
            query.update(data, synchronize_session=False)
            self.session.commit()
            self.session.close()
            return f"Your transaction was updated: {data}"

        raise HTTPException(
            status_code=404,
            detail=f"{key} id {data.get(key)} not found",
        )

    # trunk-ignore(ruff/D417)
    def delete_instance(self, register: dict, TableObject: Union[DimensionFinanceTable, FactTransactionFinance]) -> str:
        """
        Responsible to delete database instance.

        Args:
        ----
            register (dict): A dict with category and subcategory id
            TableObject (object): SqlAlchemy table object

        Return:
        ------
            (str): returns a message showing which
            category and subcategory were deleted.
        """
        found_register = (
            self.session.query(TableObject).filter(TableObject.category_name == register.get("category_name")).first()
        )
        if found_register:
            self.session.delete(found_register)
            self.session.commit()
            self.session.close()
            return f"Instance was deleted: {register}"

        raise HTTPException(
            status_code=404,
            detail=f"Instance {found_register} not found",
        )
