import requests

API_URL = "http://127.0.0.1:8000/chat"


def main():
    print("=== JARVIS OS — Cliente de consola ===")
    print("Escribe 'salir' para terminar.\n")

    session_id = None

    while True:
        mensaje = input("Tú: ").strip()
        if mensaje.lower() in ("salir", "exit", "quit"):
            print("JARVIS: Hasta luego.")
            break
        if not mensaje:
            continue

        payload = {"mensaje": mensaje}
        if session_id:
            payload["session_id"] = session_id

        try:
            respuesta = requests.post(API_URL, json=payload, timeout=30)
            respuesta.raise_for_status()
            datos = respuesta.json()
        except requests.exceptions.ConnectionError:
            print("JARVIS: No puedo conectarme al servidor. ¿Está corriendo `uvicorn core.api.main:app --reload`?")
            continue
        except requests.exceptions.RequestException as e:
            print(f"JARVIS: Ocurrió un error: {e}")
            continue

        session_id = datos["session_id"]
        print(f"JARVIS: {datos['respuesta']}\n")


if __name__ == "__main__":
    main()