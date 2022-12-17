from sqlalchemy.orm import Session
from database.register_engine import engine
from fastapi import HTTPException


class DataBaseOperations(object):
    def __init__(self) -> None:
        self.session = Session(bind=engine, expire_on_commit=False)

    def create_instance(self, TableObject: object) -> str:
        """
        Function responsible to create database instance
        Args:
            TableObject (object): SqlAlchemy table object
        Return:
            (str): returns a message showing which category was inserted.
        """
        self.session.add(TableObject)
        self.session.commit()
        self.session.close()

        return f"A budget was created. Category: {TableObject.category_id}"

    def get_instance(self, items: list, TableObject: object) -> list:
        """
        Function responsible to get database instances
        Args:
            items (list): a list of itens
            TableObject (object): SqlAlchemy table object
        Return (dict): Database instances
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
            detail=f"Categories {items} were not found",
        )

    def update_instance(self, data: dict, TableObject: object) -> str:
        """
        Function responsible to update database instances
        Args:
            register (dict): a dict register
            TableObject (object): SqlAlchemy table object
        Return:
            (str): A message showing the updated register
        """
        query = self.session.query(TableObject).filter(
            TableObject.category_id == data.get("category_id")
        )

        if query.all():
            query.update(data, synchronize_session=False)
            self.session.commit()
            self.session.close()
            return f"Your budget was updated: {data}"

        raise HTTPException(
            status_code=404,
            detail=f"category id {data.get('category_id')} not found",
        )

    def delete_instance(self, register: dict, TableObject: object) -> str:
        """
        Function responsible to delete database instance
        Args:
            register (dict): A dict with category and subcategory id
            TableObject (object): SqlAlchemy table object
        Return:
            (str): returns a message showing which category and subcategory were deleted.
        """
        found_register = self.session.query(TableObject).get(register)
        if found_register:
            self.session.delete(found_register)
            self.session.commit()
            self.session.close()
            return f"A budget was deleted: {register}"

        raise HTTPException(
            status_code=404,
            detail=f"category id {found_register} not found",
        )
