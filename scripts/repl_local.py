# -*- coding: utf-8 -*-
"""REPL Local para probar el chatbot sin WhatsApp.

Ejecutar con:
    python scripts/repl_local.py

Escribe 'salir', 'exit' o 'q' para terminar.
"""
import sys
sys.path.insert(0, ".")

from app import config
from app.services import state_manager
from app.services.chatbot_engine import ChatbotEngine
from app.services.message_processor import procesar_mensaje
from app.utils.logger import get_logger

logger = get_logger(__name__)

USUARIO = "test_user_local"


def main():
    config.validate_credentials()
    engine = ChatbotEngine(knowledge_base_path=config.KNOWLEDGE_BASE_PATH)

    print("=== Chatbot Local REPL ===")
    print("Escribe 'salir' para terminar.\n")

    while True:
        mensaje = input("Tú: ").strip()
        if mensaje.lower() in ("salir", "exit", "q"):
            print("¡Hasta luego!")
            break

        respuesta = procesar_mensaje(engine, USUARIO, mensaje)
        estado = state_manager.get_state(USUARIO)

        if respuesta:
            print(f"Bot: {respuesta}")
        else:
            print("Bot: [sin respuesta]")

        if estado:
            print(f"     [Estado: {estado}]")
        print()


if __name__ == "__main__":
    main()
