from datetime import datetime
from typing import List

from config.exceptions import TransactionRepositoryError
from database.register_engine import FactTransactionFinance, engine
from repository.base import BaseRepository
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError


class TransactionRepository(BaseRepository):
    def __init__(self):
        super().__init__()

    def get(self, items: List[int]):
        """
        Responsible to get transaction events.

        Args:
            items (list): A list of category IDs.

        Returns:
            List[FactTransactionFinance]: Matching transaction records.
        """
        try:
            with Session(bind=engine, expire_on_commit=False) as session:
                query = session.query(FactTransactionFinance)
                if items:
                    query = query.filter(FactTransactionFinance.category_id.in_(items))
                return query.all()

        except SQLAlchemyError as error:
            error_message = f"Error to get registers from transactions: {error}"
            self.logger.error(error_message)
            raise TransactionRepositoryError(error_message)

    def create(self, data: dict) -> str:
        """
        Responsible to create expense transactions.

        Args:
            data (dict): Expense transaction.

        Returns:
            str: Confirmation message.
        """
        try:
            with Session(bind=engine, expire_on_commit=False) as session:
                transaction = FactTransactionFinance(
                    category_id=data.get("category_id"),
                    tag=data.get("tag"),
                    datetime_transaction=datetime.now(),
                    credit_card=data.get("credit_card"),
                    amount=data.get("amount"),
                )
                session.add(transaction)
                session.commit()

                category_name = data.get("")
                return f"An instance was created. Category: {category_name}"

        except SQLAlchemyError as error:
            error_message = f"Error to create transaction: {error}"
            self.logger.error(error_message)
            raise TransactionRepositoryError(error_message)

    def update(self, data: dict) -> str:
        """
        Responsible to update expense transactions.

        Args:
            data (dict): Data to update transaction.

        Returns:
            str: Confirmation message.
        """
        try:
            with Session(bind=engine, expire_on_commit=False) as session:
                entry = (
                    session.query(FactTransactionFinance)
                    .filter(FactTransactionFinance.category_id == data.get("category_id"))
                    .first()
                )

                if not entry:
                    raise TransactionRepositoryError("Transaction not found for update.")

                session.query(FactTransactionFinance).filter_by(category_id=entry.category_id).update(data)
                session.commit()

                return f"Your transaction was updated: {data}"

        except SQLAlchemyError as error:
            error_message = f"Error to update transaction: {error}"
            self.logger.error(error_message)
            raise TransactionRepositoryError(error_message)

    def delete(self, data: dict) -> str:
        """
        Responsible to delete expense transactions.

        Args:
            data (dict): Contains category_id to identify record.

        Returns:
            str: Confirmation message.
        """
        try:
            with Session(bind=engine, expire_on_commit=False) as session:
                entry = (
                    session.query(FactTransactionFinance)
                    .filter(FactTransactionFinance.category_id == data.get("category_id"))
                    .first()
                )

                if not entry:
                    raise TransactionRepositoryError("Transaction not found for deletion.")

                session.delete(entry)
                session.commit()

                return f"Instance was deleted: {data}"

        except SQLAlchemyError as error:
            error_message = f"Error to delete transaction: {error}"
            self.logger.error(error_message)
            raise TransactionRepositoryError(error_message)
