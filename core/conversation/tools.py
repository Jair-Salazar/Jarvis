import json

from core.memory.domain.models import Memory
from core.memory.domain.enums import MemoryType
from core.memory.repositories.memory_repository import MemoryRepository

# Definición en formato estándar de tool calling (compatible con Groq/OpenAI)
TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "buscar_memoria",
            "description": "Busca en la memoria de JARVIS información relevante sobre el usuario, proyectos o conversaciones pasadas.",
            "parameters": {
                "type": "object",
                "properties": {
                    "consulta": {
                        "type": "string",
                        "description": "Qué se quiere buscar, en lenguaje natural."
                    }
                },
                "required": ["consulta"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "guardar_memoria",
            "description": "Guarda un dato importante para recordar en el futuro: una preferencia, un hecho sobre el usuario, o un evento relevante.",
            "parameters": {
                "type": "object",
                "properties": {
                    "contenido": {
                        "type": "string",
                        "description": "El dato a recordar, en una oración clara."
                    },
                    "tipo": {
                        "type": "string",
                        "enum": ["episodic", "semantic"],
                        "description": "'episodic' si es algo que pasó en un momento dado, 'semantic' si es un hecho permanente."
                    },
                },
                "required": ["contenido", "tipo"],
            },
        },
    },
]


def ejecutar_herramienta(nombre: str, argumentos_json: str, repo: MemoryRepository) -> str:
    """Ejecuta la herramienta que el modelo pidió, contra el repositorio real de memoria."""
    argumentos = json.loads(argumentos_json)

    if nombre == "buscar_memoria":
        resultados = repo.search(query=argumentos["consulta"], limit=3)
        if not resultados:
            return "No se encontró nada relevante en la memoria."
        return "\n".join(f"- {m.content}" for m in resultados)

    if nombre == "guardar_memoria":
        contenido = argumentos["contenido"]

        # Evita duplicados por significado, no solo por texto exacto
        similares = repo.search(query=contenido, limit=1)
        if similares:
            return "Ya existe un recuerdo muy similar guardado, no se duplicó."

        memoria = Memory(
            content=contenido,
            memory_type=MemoryType(argumentos["tipo"]),
            importance=0.6,
        )
        repo.save(memoria)
        return "Guardado en memoria correctamente."

    return f"Herramienta desconocida: {nombre}"