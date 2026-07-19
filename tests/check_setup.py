import os
from dotenv import load_dotenv

from core.llm.google_llm_client import GoogleLLMClient
from core.memory.repositories.semantic_memory_repository import SemanticMemoryRepository
from core.conversation.conversation_engine import ConversationEngine

load_dotenv()

google_keys = [k for k in [os.getenv("GOOGLE_API_KEY_1"), os.getenv("GOOGLE_API_KEY_2")] if k]

llm = GoogleLLMClient(api_keys=google_keys)
memoria = SemanticMemoryRepository()
jarvis = ConversationEngine(llm=llm, memory=memoria)

respuesta = jarvis.responder("Ábreme la calculadora")
print("JARVIS:", respuesta)