from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class LLMResponse:
    content: str
    tool_calls: list[dict]  # herramientas que el modelo decidió llamar, si las hay


class LLMClient(ABC):
    """Contrato que debe cumplir cualquier proveedor de modelo de lenguaje."""

    @abstractmethod
    def generate(self, messages: list[dict], tools: list[dict] | None = None) -> LLMResponse:
        """Envía la conversación al modelo y devuelve su respuesta."""
        raise NotImplementedError