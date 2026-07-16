import os
from dotenv import load_dotenv

from core.llm.groq_llm_client import GroqLLMClient
from core.llm.google_llm_client import GoogleLLMClient
from core.llm.fallback_llm_client import FallbackLLMClient
from core.memory.repositories.semantic_memory_repository import SemanticMemoryRepository
from core.conversation.conversation_engine import ConversationEngine

load_dotenv()

groq_keys = [k for k in [os.getenv("GROQ_API_KEY_1"), os.getenv("GROQ_API_KEY_2")] if k]
google_keys = [k for k in [os.getenv("GOOGLE_API_KEY_1"), os.getenv("GOOGLE_API_KEY_2")] if k]

llm = FallbackLLMClient(clients=[
    GroqLLMClient(api_keys=groq_keys),
    GoogleLLMClient(api_keys=google_keys),
])
memoria = SemanticMemoryRepository()
jarvis = ConversationEngine(llm=llm, memory=memoria)

print("--- Mensaje 1: le damos un dato para guardar ---")
r1 = jarvis.responder("Recuerda que mi lenguaje de programación favorito es Python.")
print("JARVIS:", r1)

print("\n--- Mensaje 2: le preguntamos algo que requiere buscar en memoria ---")
r2 = jarvis.responder("¿Cuál es mi lenguaje de programación favorito?")
print("JARVIS:", r2)