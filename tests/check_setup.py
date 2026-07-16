import os
from dotenv import load_dotenv

from core.llm.groq_llm_client import GroqLLMClient
from core.llm.google_llm_client import GoogleLLMClient
from core.llm.fallback_llm_client import FallbackLLMClient

load_dotenv()

groq_keys = [os.getenv("GROQ_API_KEY_1"), os.getenv("GROQ_API_KEY_2")]
groq_keys = [k for k in groq_keys if k]

google_keys = [os.getenv("GOOGLE_API_KEY_1"), os.getenv("GOOGLE_API_KEY_2")]
google_keys = [k for k in google_keys if k]

groq_client = GroqLLMClient(api_keys=groq_keys)
google_client = GoogleLLMClient(api_keys=google_keys)

jarvis_llm = FallbackLLMClient(clients=[groq_client, google_client])

respuesta = jarvis_llm.generate(
    messages=[
        {"role": "user", "content": "Responde solo con: JARVIS está en línea, sistema de respaldo listo."}
    ]
)

print("Respuesta del modelo:", respuesta.content)