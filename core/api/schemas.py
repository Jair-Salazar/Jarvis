from pydantic import BaseModel


class ChatRequest(BaseModel):
    mensaje: str
    session_id: str | None = None  # si no se manda, el servidor crea una nueva sesión


class ChatResponse(BaseModel):
    respuesta: str
    session_id: str