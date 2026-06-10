# -*- coding: utf-8 -*-
"""Punto de Entrada Principal de la Aplicación.

Este script es el responsable de lanzar el chatbot. Orquesta la
inicialización de todos los componentes de la aplicación:
1. Inicializa el logging centralizado.
2. Carga la configuración y valida las credenciales.
3. Inicializa el motor del chatbot (ChatbotEngine).
4. Inicializa el bot de la API de WhatsApp (GreenAPIBot).
5. Registra los manejadores de mensajes.
6. Inicia el bot para que escuche eventos de forma continua.
"""
from whatsapp_chatbot_python import GreenAPIBot

from app import config
from app.utils.logger import get_logger
from app.handlers.message_handler import register_handlers
from app.services.chatbot_engine import ChatbotEngine

logger = get_logger(__name__)


def main():
    """Función principal que configura y ejecuta el chatbot."""
    logger.info("Iniciando la aplicación del chatbot...")

    # 1. Validación de credenciales
    if not config.validate_credentials():
        logger.critical(
            "Las credenciales de Green-API no están configuradas. "
            "Revisa tu archivo .env con ID_INSTANCE y API_TOKEN_INSTANCE."
        )
        return

    try:
        # 2. Inicialización del motor del chatbot
        engine = ChatbotEngine(knowledge_base_path=config.KNOWLEDGE_BASE_PATH)

        # 3. Inicialización del bot de Green-API
        bot = GreenAPIBot(
            id_instance=config.ID_INSTANCE,
            api_token_instance=config.API_TOKEN_INSTANCE
        )

        # 4. Registro de los manejadores de eventos
        register_handlers(bot, engine)

        # 5. Inicio del bot
        logger.info("Bot iniciado. Escuchando mensajes...")
        bot.run_forever()

    except Exception as e:
        logger.critical(f"Error fatal al iniciar la aplicación: {e}", exc_info=True)
        print(f"Error al iniciar. Revisa el log: {config.LOG_FILE_PATH}")


if __name__ == "__main__":
    main()
