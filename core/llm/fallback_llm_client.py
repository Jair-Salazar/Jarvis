from core.llm.llm_client import LLMClient, LLMResponse


class FallbackLLMClient(LLMClient):
    """Intenta con una lista de clientes en orden; pasa al siguiente si el actual falla."""

    def __init__(self, clients: list[LLMClient]):
        if not clients:
            raise ValueError("Se necesita al menos un LLMClient")
        self._clients = clients

    def generate(self, messages: list[dict], tools: list[dict] | None = None) -> LLMResponse:
        ultimo_error = None
        for cliente in self._clients:
            try:
                return cliente.generate(messages, tools)
            except RuntimeError as e:
                ultimo_error = e
                continue  # este proveedor agotó sus keys, prueba el siguiente

        raise RuntimeError(f"Todos los proveedores de LLM fallaron: {ultimo_error}")