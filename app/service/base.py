from abc import ABC, abstractmethod
from typing import List

from config.logs import setup_logger


class BaseService(ABC):
    def __init__(self):
        self.logger = setup_logger(__name__)

    @abstractmethod
    def get(self, items: List[str | int]): ...

    @abstractmethod
    def create(self, data: dict): ...

    @abstractmethod
    def update(self, data: dict): ...

    @abstractmethod
    def delete(self, data: dict): ...
