from core.llm.llm_client import LLMClient
from core.memory.repositories.memory_repository import MemoryRepository
from core.conversation.tools import TOOL_SCHEMAS, ejecutar_herramienta

SYSTEM_PROMPT = (
    "Eres JARVIS, un asistente personal con memoria persistente. "
    "Cuando una herramienta te devuelva un resultado, úsalo directamente para responder — "
    "si buscar_memoria encontró información, esa información es correcta y debes usarla, "
    "nunca digas que no tienes datos si la herramienta ya te los dio. "
    "No vuelvas a llamar la misma herramienta con argumentos iguales o casi iguales. "
    "Responde en texto plano tan pronto tengas suficiente información."
)

class ConversationEngine:
    """Orquesta la conversación entre el usuario, el modelo de lenguaje y la memoria."""

    def __init__(self, llm: LLMClient, memory: MemoryRepository, max_rondas_herramientas: int = 3):
        self._llm = llm
        self._memory = memory
        self._max_rondas = max_rondas_herramientas

    def responder(self, mensaje_usuario: str, historial: list[dict] | None = None) -> str:
        mensajes = list(historial) if historial else [{"role": "system", "content": SYSTEM_PROMPT}]
        mensajes.append({"role": "user", "content": mensaje_usuario})
        ya_ejecutadas = set()  # (nombre, argumentos) ya usados en este turno

        for ronda in range(self._max_rondas):
            es_ultima_ronda = ronda == self._max_rondas - 1
            herramientas = None if es_ultima_ronda else TOOL_SCHEMAS

            respuesta = self._llm.generate(messages=mensajes, tools=herramientas)

            if not respuesta.tool_calls:
                return respuesta.content

            mensajes.append({"role": "assistant", "content": respuesta.content or ""})

            for tool_call in respuesta.tool_calls:
                clave = (tool_call["name"], tool_call["arguments"])
                if clave in ya_ejecutadas:
                    resultado = "Ya ejecutaste esta acción en este turno. Usa el resultado anterior y responde en texto."
                else:
                    resultado = ejecutar_herramienta(
                        nombre=tool_call["name"],
                        argumentos_json=tool_call["arguments"],
                        repo=self._memory,
                    )
                    ya_ejecutadas.add(clave)

                mensajes.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": resultado,
                })

        return "No pude completar la respuesta después de varios intentos usando herramientas."