from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from config.exceptions import SpendRepositoryError, SpendIntegrityRepositoryError, NotFoundError
from database.register_engine import DimensionSpendFinance, engine
from repository.base import BaseRepository


class SpendLimitRepository(BaseRepository):
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
                    query = query.filter(DimensionSpendFinance.category_name.in_(items))
                return query.all()

        except SQLAlchemyError as error:
            error_message = f"Erro ao recuperar limite de gastos: {error}"
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
                return f"Categoria criada: {category_name}"

        except IntegrityError as error:
            error_message = f"Erro ao criar categoria: {error}"
            self.logger.error(error_message)
            raise SpendIntegrityRepositoryError(error_message)

        except Exception as error:
            message = "Erro inesperado ao criar categoria"
            self.logger.error(f"{message}: {error}")
            raise SpendRepositoryError(f"{message}: {error}")

    def update(self, data: dict) -> str:
        """
        Update an existing spend limit entry.

        Args:
            data (dict): Data to update the budget.

        Returns:
            str: Confirmation message.
        """
        try:
            category_name = data.get("category_name")
            with Session(bind=engine, expire_on_commit=False) as session:
                entry = (
                    session.query(DimensionSpendFinance)
                    .filter(DimensionSpendFinance.category_name == category_name)
                    .first()
                )
                if not entry:
                    message = f"Categoria '{category_name}' não encontrada "
                    self.logger.error(message)
                    raise NotFoundError(message)


                data["category_id"] = entry.category_id
                session.query(DimensionSpendFinance).filter_by(category_id=entry.category_id).update(data)
                session.commit()

                return f"Limite de gastos ({data.get("category_name")}) atualizado: {data.get("budget")}"

        except SQLAlchemyError as error:
            error_message = f"Erro ao atualizar limite de gastos: {error}"
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
            category_name = data.get("category_name")
            with Session(bind=engine, expire_on_commit=False) as session:
                entry = (
                    session.query(DimensionSpendFinance)
                    .filter(DimensionSpendFinance.category_name == category_name)
                    .first()
                )

                if not entry:
                    message = f"Categoria '{category_name}' não encontrada "
                    self.logger.error(message)
                    raise NotFoundError(message)

                session.delete(entry)
                session.commit()

                return f"Limite de gastos deletado: {category_name}"

        except SQLAlchemyError as error:
            error_message = f"Erro ao deletar limite de gastos: {error}"
            self.logger.error(error_message)
            raise SpendRepositoryError(error_message)
