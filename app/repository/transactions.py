from repository.base import BaseRepository
from database.register_engine import FactTransactionFinance, engine
from sqlalchemy.orm import Query, Session
from typing import List
from config.exceptions import DatabaseError
from datetime import datetime

class TransactionRepository(BaseRepository):
    def __init__(self):
        super().__init__()
        self.session = Session(bind=engine, expire_on_commit=False)

    def get(self, items: List[int]):
        """
        Responsible to get transaction event.
        Args:
        ----
            Items (list): a list of items.
        Return:
        ------
            (dict): Expense transactions
        """
        try:
            if not items:
                query = self.session.query(FactTransactionFinance)
                results = query.all()
            else:
                found_registers: Query = self.session.query(FactTransactionFinance).filter(FactTransactionFinance.in_(items)) # type: ignore
                results = found_registers.all()
            return results

        except DatabaseError as error:
            error_message = f"Error to get registers from transactions: {error}"
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
            transaction_date = datetime.now()

            transaction_finance_table_instance = FactTransactionFinance(
                category_id=data.get("category_id"),
                tag=data.get("tag"),
                datetime_transaction=transaction_date,
                credit_card=data.get("credit_card"),
                amount=data.get("amount"),
            )

            self.session.add(transaction_finance_table_instance)
            self.session.commit()
            category_name = getattr(transaction_finance_table_instance, "category_name", "Unknown")
            return f"An instance was created. Category: {category_name}"

        except DatabaseError as error:
            error_message = f"Error to create transaction: {error}"
            self.logger.error(error_message)
            self.session.rollback()
            raise DatabaseError(error_message)

        finally:
            self.session.close()

    # TO DO
    def update(self, data: dict):
        """
        Responsible to update expense transactions.

        Args:
        ----
            data (dict): a dict to update instance.
            TableObject (object): SqlAlchemy table object.

        Return:
        ------
            (str): A message showing the updated register.
        """
        try:
            query: Query = self.session.query(FactTransactionFinance).filter(
                FactTransactionFinance.category_id == data.get("category_id"))

            category_id = query.all()[0].category_id
            data.update({"category_id": category_id})
            query.update(data, synchronize_session=False)
            self.session.commit()
            self.session.close()
            return f"Your transaction was updated: {data}"

        except DatabaseError as error:
            error_message = f"Error to update transaction: {error}"
            self.logger.error(error_message)
            self.session.rollback()
            raise DatabaseError(error_message)

        finally:
            self.session.close()


    # TO DO
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
            category and subcategory were deleted.
        """
        try:
            found_register = (
                self.session.query(FactTransactionFinance).filter(FactTransactionFinance.category_id == data.get("category_id")).first()
            )
            self.session.delete(found_register)
            self.session.commit()
            self.session.close()
            return f"Instance was deleted: {data}"

        except DatabaseError as error:
            error_message = f"Error to delete transaction: {error}"
            self.logger.error(error_message)
            self.session.rollback()
            raise DatabaseError(error_message)

