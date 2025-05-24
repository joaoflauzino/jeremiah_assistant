from typing import List

from repository.spend_limit import SpendLimitRepository
from service.base import BaseService

from config.exceptions import NotFoundError
from config.request_exceptions import handle_service_errors


class SpendService(BaseService):
    def __init__(self):
        super().__init__()
        self.repository = SpendLimitRepository()

    @handle_service_errors("Categoria(s) podem não existir, contate o administrador.")
    def get(self, items: List[str | int]) -> list:
        repository_response = self.repository.get(items=items)
        repository_response_transformed = [response.to_dict() for response in repository_response]
        if not repository_response_transformed:
            raise NotFoundError(f"Nenhuma categoria encontrada com os nomes {' '.join(items)}")
        return repository_response_transformed

    @handle_service_errors("Algum erro aconteceu ao tentar criar o limite de gastos, contate o administrador.") # Especificar categorias
    def create(self, data: dict) -> str: #informar pydantic model in type hints
        create_repository_response = self.repository.create(data=data)
        return create_repository_response

    @handle_service_errors("Algum erro aconteceu ao tentar atualizar o limite de gastos, contate o administrador.") # Especificar categorias
    def update(self, data: dict) -> str:
        update_repository_response = self.repository.create(data=data)
        return update_repository_response

    @handle_service_errors("Algum erro aconteceu ao tentar deletar o limite de gastos, contate o administrador.")
    def delete(self, data: dict) -> str:
        delete_repository_response = self.repository.create(data=data)
        return delete_repository_response


