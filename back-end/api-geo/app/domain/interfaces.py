from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID


class IGeoPointRepository(ABC):

    @abstractmethod
    def create(self, db, geopoint) -> object:
        pass

    @abstractmethod
    def get_by_place_id(self, db, place_id: UUID) -> Optional[object]:
        pass

    @abstractmethod
    def get_all(self, db) -> List[object]:
        pass

    @abstractmethod
    def exists_by_place_id(self, db, place_id: UUID) -> bool:
        pass