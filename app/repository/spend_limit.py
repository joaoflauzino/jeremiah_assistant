from repository.base import BaseRepository

from typing import List

from config.exceptions import DatabaseError
from sqlalchemy.orm import Query, Session

from database.register_engine import DimensionSpendFinance, engine

class SpendLimitRepository(BaseRepository):
    def __init__(self):
        super().__init__()
        self.session = Session(bind=engine, expire_on_commit=False)

    def get(self, items: List[int]):
        """
        Responsible to get spend limit event.
        Args:
        ----
            Items (list): a list of items.
        Return:
        ------
            (dict): Spend transactions
        """
        try:
            if not items:
                query = self.session.query(DimensionSpendFinance)
                results = query.all()
            else:
                found_registers: Query = self.session.query(DimensionSpendFinance).filter(DimensionSpendFinance.category_name.in_(items)) # type: ignore
                results = found_registers.all()
            return results

        except DatabaseError as error:
            error_message = f"Error to get registers from spend limit: {error}"
            self.logger.error(error_message)
            raise DatabaseError(error_message)

        finally:
            self.session.close()

    def create(self, data: dict):
        """
        Responsible to create expense transactions.

        Args:
        ----
            data (object): Expense transaction.

        Return:
        ------
            (str): returns a message showing which category was inserted.
        """

        try:
            dimension_finance_table_instance = DimensionSpendFinance(
                category_id = data.get("category_id"),
                category_name = data.get("category_name"),
                budget = data.get("budget")
            )
            self.session.add(dimension_finance_table_instance)
            self.session.commit()
            category_name = getattr(dimension_finance_table_instance, "category_name", "Unknown")
            return f"An instance was created. Category: {category_name}"

        except DatabaseError as error:
            error_message = f"Error to create budget: {error}"
            self.logger.error(error_message)
            self.session.rollback()
            raise DatabaseError(error_message)

        finally:
            self.session.close()

    def update(self, data: dict):
        """
        Responsible to update expense transactions.

        Args:
        ----
            data (dict): a dict to update budget.
        Return:
        ------
            (str): A message showing the updated register.
        """
        try:
            query: Query = self.session.query(DimensionSpendFinance).filter(
                DimensionSpendFinance.category_name == data.get("category_name"))

            category_id = query.all()[0].category_id
            data.update({"category_id": category_id})
            query.update(data, synchronize_session=False)
            self.session.commit()
            self.session.close()
            return f"Your budget was updated: {data}"

        except DatabaseError as error:
            error_message = f"Error to update budget: {error}"
            self.logger.error(error_message)
            self.session.rollback()
            raise DatabaseError(error_message)

        finally:
            self.session.close()


    def delete(self, data: dict):
        """
        Responsible to delete expense transactions.

        Args:
        ----
            register (dict): A dict with category and subcategory id
            TableObject (object): SqlAlchemy table object

        Return:
        ------
            (str): returns a message showing which
            category was deleted.
        """
        try:
            found_register = (
                self.session.query(DimensionSpendFinance).filter(DimensionSpendFinance.category_name == data.get("category_name")).first()
            )
            self.session.delete(found_register)
            self.session.commit()
            self.session.close()
            return f"Budget was deleted: {data}"

        except DatabaseError as error:
            error_message = f"Error to delete budget: {error}"
            self.logger.error(error_message)
            self.session.rollback()
            raise DatabaseError(error_message)
