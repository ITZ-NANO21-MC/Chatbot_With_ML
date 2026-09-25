# -*- coding: utf-8 -*-
"""Punto de Entrada Principal de la Aplicación.

Este script es el responsable de lanzar el chatbot. Orquesta la
inicialización de todos los componentes de la aplicación:
1. Inicializa el logging centralizado.
2. Carga la configuración y valida las credenciales.
3. Inicializa el motor del chatbot (ChatbotEngine).
4. Inicializa el bot de la API de WhatsApp (GreenAPIBot).
5. Registra los manejadores de mensajes.
6. Programa el recordatorio diario (notificaciones programadas).
7. Inicia el bot para que escuche eventos de forma continua.
"""
import threading

from whatsapp_chatbot_python import GreenAPIBot

from app import config
from app.utils.logger import get_logger
from app.handlers.message_handler import register_handlers
from app.services.chatbot_engine import ChatbotEngine
from app.services.scheduled_notifications import enviar_recordatorios_diarios

logger = get_logger(__name__)

INTERVALO_RECORDATORIO_SEGUNDOS = 24 * 60 * 60


def _programar_recordatorio(bot: GreenAPIBot) -> None:
    """Envía los recordatorios y reprograma la siguiente ejecución en 24 h.

    Args:
        bot (GreenAPIBot): Instancia del bot de Green-API.
    """
    threading.Timer(
        INTERVALO_RECORDATORIO_SEGUNDOS,
        _programar_recordatorio,
        args=[bot],
    ).start()
    logger.info("Ejecutando recordatorios programados...")
    enviar_recordatorios_diarios(bot)


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
        logger.info("GreenAPIBot creado exitosamente.")

        # 4. Registro de los manejadores de eventos
        register_handlers(bot, engine)
        logger.info("Handlers registrados exitosamente.")

        # 5. Programación de recordatorios diarios
        _programar_recordatorio(bot)

        # 6. Inicio del bot
        logger.info("Bot iniciado. Escuchando mensajes...")
        bot.run_forever()

    except Exception as e:
        logger.critical(f"Error fatal al iniciar la aplicación: {e}", exc_info=True)
        print(f"Error al iniciar. Revisa el log: {config.LOG_FILE_PATH}")


if __name__ == "__main__":
    main()
