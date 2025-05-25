from typing import List

from repository.spend_limit import SpendLimitRepository
from service.base import BaseService

from config.exceptions import NotFoundError
from config.request_exceptions import handle_service_errors


class SpendService(BaseService):
    def __init__(self):
        super().__init__()
        self.repository = SpendLimitRepository()

    @handle_service_errors("Categoria(s) informadas podem não existir")
    def get(self, items: List[str | int]) -> list:
        """
        Retrieve spend limit records for the provided category names or IDs.

        Args:
            items (List[str | int]): List of category identifiers (name or ID).

        Returns:
            list: List of matching spend limit records as dictionaries.

        Raises:
            NotFoundError: If no matching categories are found.
        """
        repository_response = self.repository.get(items=items)
        repository_response_transformed = [response.to_dict() for response in repository_response]
        if not repository_response_transformed:
            raise NotFoundError(f"Nenhuma categoria encontrada com os nomes {' '.join(items)}")
        return repository_response_transformed

    @handle_service_errors("Algum erro aconteceu ao tentar criar o limite de gastos, contate o administrador.")
    def create(self, data: dict) -> str:
        """
        Create a new spend limit entry.

        Args:
            data (dict): Data to create the spend limit (category_id, category_name, budget).

        Returns:
            str: Confirmation message from the repository.
        """
        create_repository_response = self.repository.create(data=data)
        return create_repository_response

    @handle_service_errors("Algum erro aconteceu ao tentar atualizar o limite de gastos, contate o administrador.")
    def update(self, data: dict) -> str:
        """
        Update an existing spend limit entry.

        Args:
            data (dict): Data containing the category name and the updated fields.

        Returns:
            str: Confirmation message from the repository.
        """
        update_repository_response = self.repository.update(data=data)  # Corrigido: era create
        return update_repository_response

    @handle_service_errors("Algum erro aconteceu ao tentar deletar o limite de gastos, contate o administrador.")
    def delete(self, data: dict) -> str:
        """
        Delete an existing spend limit entry.

        Args:
            data (dict): Data identifying the category to be deleted (typically by name).

        Returns:
            str: Confirmation message from the repository.
        """
        delete_repository_response = self.repository.delete(data=data)  # Corrigido: era create
        return delete_repository_response
