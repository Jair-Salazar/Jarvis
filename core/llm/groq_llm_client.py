from groq import Groq, RateLimitError

from core.llm.llm_client import LLMClient, LLMResponse


class GroqLLMClient(LLMClient):
    def __init__(self, api_keys: list[str], model: str = "llama-3.3-70b-versatile"):
        if not api_keys:
            raise ValueError("Se necesita al menos una API key de Groq")
        self._api_keys = api_keys
        self._model = model

    def generate(self, messages: list[dict], tools: list[dict] | None = None) -> LLMResponse:
        ultimo_error = None
        for key in self._api_keys:
            try:
                client = Groq(api_key=key)
                kwargs = {"model": self._model, "messages": messages}
                if tools:
                    kwargs["tools"] = tools

                respuesta = client.chat.completions.create(**kwargs)
                mensaje = respuesta.choices[0].message

                tool_calls = []
                if mensaje.tool_calls:
                    for tc in mensaje.tool_calls:
                        tool_calls.append({
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                            "id": tc.id,
                        })

                return LLMResponse(content=mensaje.content or "", tool_calls=tool_calls)

            except RateLimitError as e:
                ultimo_error = e
                continue  # prueba con la siguiente key

        raise RuntimeError(f"Todas las keys de Groq alcanzaron su límite: {ultimo_error}")