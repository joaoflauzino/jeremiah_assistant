from typing import List

from repository.spend_limit import SpendLimitRepository

from service.base import BaseService

class SpendService(BaseService):

    def __init__(self):
        super().__init__()
        self.repository = SpendLimitRepository()

    def get(self, items: List[str | int]) -> list:
        return self.repository.get(items=items)

    def create(self, data: dict) -> str:
        return self.repository.create(data=data)

    def update(self, data: dict) -> str:
        return self.repository.update(data=data)

    def delete(self, data: dict) -> str:
        return self.repository.delete(data=data)