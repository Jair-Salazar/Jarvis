import os
from dotenv import load_dotenv
from fastapi import FastAPI

from core.api.schemas import ChatRequest, ChatResponse
from core.api.session_store import SessionStore
from core.llm.groq_llm_client import GroqLLMClient
from core.llm.google_llm_client import GoogleLLMClient
from core.llm.fallback_llm_client import FallbackLLMClient
from core.memory.repositories.semantic_memory_repository import SemanticMemoryRepository
from core.conversation.conversation_engine import ConversationEngine

load_dotenv()

app = FastAPI(title="JARVIS OS")

# Se construyen una sola vez, cuando arranca el servidor — no en cada petición
groq_keys = [k for k in [os.getenv("GROQ_API_KEY_1"), os.getenv("GROQ_API_KEY_2")] if k]
google_keys = [k for k in [os.getenv("GOOGLE_API_KEY_1"), os.getenv("GOOGLE_API_KEY_2")] if k]

llm = FallbackLLMClient(clients=[
    GroqLLMClient(api_keys=groq_keys),
    GoogleLLMClient(api_keys=google_keys),
])
memoria = SemanticMemoryRepository()
motor = ConversationEngine(llm=llm, memory=memoria)
sesiones = SessionStore()


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    session_id = request.session_id or sesiones.crear_sesion()
    historial = sesiones.obtener_historial(session_id)

    respuesta_texto = motor.responder(request.mensaje, historial=historial)

    historial.append({"role": "user", "content": request.mensaje})
    historial.append({"role": "assistant", "content": respuesta_texto})
    sesiones.guardar_historial(session_id, historial)

    return ChatResponse(respuesta=respuesta_texto, session_id=session_id)


@app.get("/health")
def health() -> dict:
    return {"status": "JARVIS está en línea"}