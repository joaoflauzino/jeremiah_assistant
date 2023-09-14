from database.register_engine import engine
from fastapi import HTTPException
from sqlalchemy.orm import Session


class DataBaseOperations(object):
    def __init__(self) -> None:
        self.session = Session(bind=engine, expire_on_commit=False)

    # trunk-ignore(ruff/D417)
    def create_instance(self, TableObject: object) -> str:
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
    def get_instance(self, items: list, TableObject: object) -> list:
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
        found_registers = self.session.query(TableObject).filter(
            TableObject.category_id.in_(items)
        )

        if found_registers.all():
            self.session.commit()
            self.session.close()
            return found_registers.all()

        raise HTTPException(
            status_code=404,
            detail=f"Categories or transactions {items} were not found",
        )

    # trunk-ignore(ruff/D417)
    def update_instance(self, data: dict, TableObject: object) -> str:
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

        if "transaction_id" in data:
            query = self.session.query(TableObject).filter(
                TableObject.transaction_id == data.get("transaction_id")
            )

        elif "category_id" in data:
            query = self.session.query(TableObject).filter(
                TableObject.category_id == data.get("category_id")
            )

        if query.all():
            query.update(data, synchronize_session=False)
            self.session.commit()
            self.session.close()
            return f"Your transaction was updated: {data}"

        raise HTTPException(
            status_code=404,
            detail=f"{key} id {data.get(key)} not found",
        )

    # trunk-ignore(ruff/D417)
    def delete_instance(self, register: dict, TableObject: object) -> str:
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
        found_register = self.session.query(TableObject).get(register)
        if found_register:
            self.session.delete(found_register)
            self.session.commit()
            self.session.close()
            return f"Instance was deleted: {register}"

        raise HTTPException(
            status_code=404,
            detail=f"Instance {found_register} not found",
        )
