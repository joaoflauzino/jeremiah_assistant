from typing import List, Union

from database.register_engine import (
    DimensionFinanceTable,
    FactTransactionFinance,
    engine,
)
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
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
        try:
            self.session.add(TableObject)
            self.session.commit()
            category_name = getattr(TableObject, "category_name", "Unknown")  # TODO
            return f"An instance was created. Category: {category_name}"
        except IntegrityError as error:
            self.session.rollback()
            raise HTTPException(
                status_code=400, detail=f"Problem registering item. Item may already exist: {error.orig}"
            )
        except Exception as error:
            self.session.rollback()
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {error}")
        finally:
            self.session.close()

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

        field_filter = {
            "DimensionFinanceTable": TableObject.category_name,
            "FactTransactionFinance": TableObject.category_id,
        }

        if not items:
            return self.session.query(TableObject).all()

        # found_registers: Query = self.session.query(TableObject).filter(TableObject.category_name.in_(items))  # type: ignore
        found_registers: Query = self.session.query(TableObject).filter(field_filter[TableObject.__name__].in_(items))  # type: ignore

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
