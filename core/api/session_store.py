import uuid


class SessionStore:
    """Guarda el historial de conversación de cada sesión, en memoria del proceso."""

    def __init__(self):
        self._sesiones: dict[str, list[dict]] = {}

    def crear_sesion(self) -> str:
        session_id = str(uuid.uuid4())
        self._sesiones[session_id] = []
        return session_id

    def obtener_historial(self, session_id: str) -> list[dict]:
        if session_id not in self._sesiones:
            self._sesiones[session_id] = []
        return self._sesiones[session_id]

    def guardar_historial(self, session_id: str, historial: list[dict]) -> None:
        self._sesiones[session_id] = historial