from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from .enums import MemoryType

@dataclass(frozen=True)
class Memory:
    content: str
    memory_type: MemoryType
    importance: float
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_accessed_at: datetime = field(default_factory=datetime.utcnow)
    id: UUID = field(default_factory=uuid4)

    def is_stale(self, threshold_days: int = 30) -> bool:
        days_since_access = (datetime.utcnow() - self.last_accessed_at).days
        return days_since_access > threshold_days and self.importance < 0.3