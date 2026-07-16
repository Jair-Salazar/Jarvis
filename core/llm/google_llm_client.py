from google import genai
from google.genai.errors import ClientError

from core.llm.llm_client import LLMClient, LLMResponse


class GoogleLLMClient(LLMClient):
    def __init__(self, api_keys: list[str], model: str = "gemini-flash-latest"):
        if not api_keys:
            raise ValueError("Se necesita al menos una API key de Google")
        self._api_keys = api_keys
        self._model = model

    def generate(self, messages: list[dict], tools: list[dict] | None = None) -> LLMResponse:
        contenido = self._convertir_mensajes(messages)

        ultimo_error = None
        for key in self._api_keys:
            try:
                client = genai.Client(api_key=key)
                respuesta = client.models.generate_content(
                    model=self._model,
                    contents=contenido,
                )
                return LLMResponse(content=respuesta.text or "", tool_calls=[])

            except ClientError as e:
                if "RESOURCE_EXHAUSTED" in str(e) or getattr(e, "code", None) == 429:
                    ultimo_error = e
                    continue  # prueba con la siguiente key
                raise  # cualquier otro error de cliente, falla ruidoso

        raise RuntimeError(f"Todas las keys de Google alcanzaron su límite: {ultimo_error}")

    @staticmethod
    def _convertir_mensajes(messages: list[dict]) -> str:
        """Google recibe texto plano por ahora; conversión simple de nuestro formato de mensajes."""
        return "\n".join(f"{m['role']}: {m['content']}" for m in messages)  