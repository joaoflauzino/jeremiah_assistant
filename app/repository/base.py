from abc import ABC, abstractmethod
from typing import List
from config.logs import setup_logger

class BaseRepository(ABC):
    def __init__(self):
        self.logger = setup_logger(__name__)

    @abstractmethod
    def get(self, items: List[int | str]) -> list:
        pass

    @abstractmethod
    def create(self, data: dict) -> str:
        pass

    @abstractmethod
    def update(self, data: dict) -> str:
        pass

    @abstractmethod
    def delete(self, data: dict) -> str:
        pass
