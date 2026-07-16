import chromadb
from uuid import UUID

from core.memory.domain.models import Memory
from core.memory.domain.enums import MemoryType
from core.memory.repositories.memory_repository import MemoryRepository
from core.memory.repositories.sqlite_memory_repository import SqliteMemoryRepository


class SemanticMemoryRepository(MemoryRepository):
    """
    Combina SQLite (fuente de verdad) con Chroma (índice semántico).
    SQLite guarda el contenido real; Chroma solo guarda el vector + el id.
    """

    def __init__(self, db_path: str = "data/jarvis_memory.db", chroma_path: str = "data/chroma"):
        self._sqlite = SqliteMemoryRepository(db_path)
        self._chroma_client = chromadb.PersistentClient(path=chroma_path)
        self._collection = self._chroma_client.get_or_create_collection(
            "memories", metadata={"hnsw:space": "cosine"}
        )
        self._relevance_threshold = 0.8  

    def save(self, memory: Memory) -> None:
        self._sqlite.save(memory)
        self._collection.add(
            ids=[str(memory.id)],
            documents=[memory.content],
        )

    def get_by_id(self, memory_id: UUID) -> Memory | None:
        return self._sqlite.get_by_id(memory_id)

    def search(self, query: str, memory_type: MemoryType | None = None, limit: int = 5) -> list[Memory]:
        results = self._collection.query(query_texts=[query], n_results=limit)
        ids_encontrados = results["ids"][0]
        distancias = results["distances"][0]

        memorias = []
        for id_str, distancia in zip(ids_encontrados, distancias):
            if distancia > self._relevance_threshold:
                continue
            memoria = self._sqlite.get_by_id(UUID(id_str))
            if memoria is not None:
                if memory_type is None or memoria.memory_type == memory_type:
                    memorias.append(memoria)
        return memorias

    def delete(self, memory_id: UUID) -> None:
        self._sqlite.delete(memory_id)
        self._collection.delete(ids=[str(memory_id)])