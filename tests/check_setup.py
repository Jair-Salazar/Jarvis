from core.memory.domain.models import Memory
from core.memory.domain.enums import MemoryType
from core.memory.repositories.semantic_memory_repository import SemanticMemoryRepository

repo = SemanticMemoryRepository()

recuerdo = Memory(
    content="El usuario prefiere Python sobre C#",
    memory_type=MemoryType.SEMANTIC,
    importance=0.8,
)

repo.save(recuerdo)
print("Guardado con id:", recuerdo.id)

print("\n--- Búsqueda semántica: 'lenguajes de programación' ---")
resultados = repo.search("lenguajes de programación")
for r in resultados:
    print(" -", r.content)

print("\n--- Búsqueda semántica: 'qué comida le gusta' ---")
resultados2 = repo.search("qué comida le gusta")
for r in resultados2:
    print(" -", r.content)