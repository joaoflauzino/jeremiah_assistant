from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from config.exceptions import SpendRepositoryError, NotFoundError
from database.register_engine import DimensionSpendFinance, engine
from repository.base import BaseRepository


class SpendLimitRepository(BaseRepository):
    def __init__(self):
        super().__init__()

    def get(self, items: Optional[List[int]] = None):
        """
        Fetch spend limit records. If no items are provided, returns all.

        Args:
            items (List[int], optional): A list of category IDs to filter.

        Returns:
            List[DimensionSpendFinance]: Matching records.
        """
        try:
            with Session(bind=engine, expire_on_commit=False) as session:
                query = session.query(DimensionSpendFinance)
                if items:
                    query = query.filter(DimensionSpendFinance.category_name.in_(items))  # type: ignore
                return query.all()

        except SQLAlchemyError as error:
            error_message = f"Error fetching spend limit records: {error}"
            self.logger.error(error_message)
            raise SpendRepositoryError(error_message)

    def create(self, data: dict) -> str:
        """
        Create a new spend limit entry.

        Args:
            data (dict): Expense transaction data.

        Returns:
            str: Confirmation message.
        """
        try:
            with Session(bind=engine, expire_on_commit=False) as session:
                entry = DimensionSpendFinance(
                    category_id=data.get("category_id"),
                    category_name=data.get("category_name"),
                    budget=data.get("budget"),
                )
                session.add(entry)
                session.commit()

                category_name = getattr(entry, "category_name", "Unknown")
                return f"An instance was created. Category: {category_name}"

        except SQLAlchemyError as error:
            error_message = f"Error creating budget entry: {error}"
            self.logger.error(error_message)
            raise SpendRepositoryError(error_message)

    def update(self, data: dict) -> str:
        """
        Update an existing spend limit entry.

        Args:
            data (dict): Data to update the budget.

        Returns:
            str: Confirmation message.
        """
        try:
            with Session(bind=engine, expire_on_commit=False) as session:
                entry = (
                    session.query(DimensionSpendFinance)
                    .filter(DimensionSpendFinance.category_name == data.get("category_name"))
                    .first()
                )

                if not entry:
                    raise SpendRepositoryError("Category not found for update.")

                data["category_id"] = entry.category_id
                session.query(DimensionSpendFinance).filter_by(category_id=entry.category_id).update(data)
                session.commit()

                return f"Budget updated: {data}"

        except SQLAlchemyError as error:
            error_message = f"Error updating budget: {error}"
            self.logger.error(error_message)
            raise SpendRepositoryError(error_message)

    def delete(self, data: dict) -> str:
        """
        Delete a spend limit entry.

        Args:
            data (dict): Contains the category_name to delete.

        Returns:
            str: Confirmation message.
        """
        try:
            with Session(bind=engine, expire_on_commit=False) as session:
                entry = (
                    session.query(DimensionSpendFinance)
                    .filter(DimensionSpendFinance.category_name == data.get("category_name"))
                    .first()
                )

                if not entry:
                    raise NotFoundError("Category not found for deletion.")

                session.delete(entry)
                session.commit()

                return f"Budget deleted: {data}"

        except SQLAlchemyError as error:
            error_message = f"Error deleting budget: {error}"
            self.logger.error(error_message)
            raise SpendRepositoryError(error_message)
