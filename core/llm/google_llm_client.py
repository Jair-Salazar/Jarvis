import json
import uuid

from google import genai
from google.genai import types
from google.genai.errors import ClientError

from core.llm.llm_client import LLMClient, LLMResponse


class GoogleLLMClient(LLMClient):
    def __init__(self, api_keys: list[str], model: str = "gemini-flash-latest"):
        if not api_keys:
            raise ValueError("Se necesita al menos una API key de Google")
        self._api_keys = api_keys
        self._model = model

    def generate(self, messages: list[dict], tools: list[dict] | None = None) -> LLMResponse:
        system_instruction, contenido = self._convertir_mensajes(messages)
        gemini_tools = self._convertir_tools(tools) if tools else None

        config = types.GenerateContentConfig(
            system_instruction=system_instruction or None,
            tools=gemini_tools,
        )

        ultimo_error = None
        for key in self._api_keys:
            try:
                client = genai.Client(api_key=key)
                respuesta = client.models.generate_content(
                    model=self._model,
                    contents=contenido,
                    config=config,
                )
                return self._parsear_respuesta(respuesta)

            except ClientError as e:
                if "RESOURCE_EXHAUSTED" in str(e) or getattr(e, "code", None) == 429:
                    ultimo_error = e
                    continue
                raise

        raise RuntimeError(f"Todas las keys de Google alcanzaron su límite: {ultimo_error}")

    @staticmethod
    def _convertir_mensajes(messages: list[dict]) -> tuple[str, list]:
        """Separa el system prompt (Gemini lo maneja aparte) y convierte el resto."""
        system_instruction = ""
        contenido = []

        for m in messages:
            role = m["role"]
            if role == "system":
                system_instruction = m["content"]
            elif role == "user":
                contenido.append(types.Content(role="user", parts=[types.Part(text=m["content"])]))
            elif role == "assistant" and m.get("content"):
                contenido.append(types.Content(role="model", parts=[types.Part(text=m["content"])]))
            elif role == "tool":
                # Simplificación: se le pasa como contexto adicional del usuario,
                # no como function_response nativo — suficiente para nuestro caso de uso actual.
                contenido.append(types.Content(
                    role="user",
                    parts=[types.Part(text=f"[Resultado de herramienta]: {m['content']}")],
                ))

        return system_instruction, contenido

    @staticmethod
    def _convertir_tools(tools: list[dict]) -> list:
        declaraciones = [
            types.FunctionDeclaration(
                name=tool["function"]["name"],
                description=tool["function"]["description"],
                parameters=tool["function"]["parameters"],
            )
            for tool in tools
        ]
        return [types.Tool(function_declarations=declaraciones)]

    @staticmethod
    def _parsear_respuesta(respuesta) -> LLMResponse:
        tool_calls = []
        texto = ""

        for part in respuesta.candidates[0].content.parts:
            if part.function_call:
                tool_calls.append({
                    "name": part.function_call.name,
                    "arguments": json.dumps(dict(part.function_call.args)),
                    "id": str(uuid.uuid4()),
                })
            elif part.text:
                texto += part.text

        return LLMResponse(content=texto, tool_calls=tool_calls)