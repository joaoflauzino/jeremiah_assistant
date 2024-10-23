from abc import ABC, abstractmethod
from typing import List

from config.logs import setup_logger

class BaseService(ABC):
    def __init__(self):
        self.logger = setup_logger(__name__)

    @abstractmethod
    def get(self, items: List[str | int]):
        pass

    @abstractmethod
    def create(self, data: dict):
        pass

    @abstractmethod
    def update(self, data: dict):
        pass

    @abstractmethod
    def delete(self, data: dict):
        pass