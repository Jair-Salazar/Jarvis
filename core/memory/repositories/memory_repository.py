from abc import ABC, abstractmethod
from uuid import UUID

from core.memory.domain.models import Memory
from core.memory.domain.enums import MemoryType


class MemoryRepository(ABC):
    """Contrato que debe cumplir cualquier forma de almacenar memoria."""

    @abstractmethod
    def save(self, memory: Memory) -> None:
        """Guarda un recuerdo nuevo."""
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, memory_id: UUID) -> Memory | None:
        """Recupera un recuerdo por su id exacto."""
        raise NotImplementedError

    @abstractmethod
    def search(self, query: str, memory_type: MemoryType | None = None, limit: int = 5) -> list[Memory]:
        """Busca recuerdos relevantes para una consulta."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, memory_id: UUID) -> None:
        """Elimina un recuerdo (uso raro; normalmente se archiva, no se borra)."""
        raise NotImplementedError