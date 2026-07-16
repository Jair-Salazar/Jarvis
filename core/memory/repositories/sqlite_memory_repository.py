import sqlite3
from pathlib import Path
from uuid import UUID
from datetime import datetime

from core.memory.domain.models import Memory
from core.memory.domain.enums import MemoryType
from core.memory.repositories.memory_repository import MemoryRepository


class SqliteMemoryRepository(MemoryRepository):
    def __init__(self, db_path: str = "data/jarvis_memory.db"):
        self._db_path = Path(db_path)
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self._db_path)

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    memory_type TEXT NOT NULL,
                    importance REAL NOT NULL,
                    created_at TEXT NOT NULL,
                    last_accessed_at TEXT NOT NULL
                )
            """)

    def save(self, memory: Memory) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO memories (id, content, memory_type, importance, created_at, last_accessed_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    str(memory.id),
                    memory.content,
                    memory.memory_type.value,
                    memory.importance,
                    memory.created_at.isoformat(),
                    memory.last_accessed_at.isoformat(),
                ),
            )

    def get_by_id(self, memory_id: UUID) -> Memory | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM memories WHERE id = ?", (str(memory_id),)
            ).fetchone()
        return self._row_to_memory(row) if row else None

    def search(self, query: str, memory_type: MemoryType | None = None, limit: int = 5) -> list[Memory]:
        sql = "SELECT * FROM memories WHERE content LIKE ?"
        params: list = [f"%{query}%"]
        if memory_type is not None:
            sql += " AND memory_type = ?"
            params.append(memory_type.value)
        sql += " ORDER BY importance DESC LIMIT ?"
        params.append(limit)
        with self._connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [self._row_to_memory(row) for row in rows]

    def delete(self, memory_id: UUID) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM memories WHERE id = ?", (str(memory_id),))

    @staticmethod
    def _row_to_memory(row) -> Memory:
        id_, content, memory_type, importance, created_at, last_accessed_at = row
        return Memory(
            id=UUID(id_),
            content=content,
            memory_type=MemoryType(memory_type),
            importance=importance,
            created_at=datetime.fromisoformat(created_at),
            last_accessed_at=datetime.fromisoformat(last_accessed_at),
        )