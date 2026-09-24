# -*- coding: utf-8 -*-
"""Módulo de Manejadores de Mensajes.

Este archivo define los manejadores (handlers) para las notificaciones
entrantes de la API de WhatsApp. Es una capa delgada que delega toda
la lógica de negocio en message_processor.
"""
from whatsapp_chatbot_python import GreenAPIBot, Notification

from app.services.chatbot_engine import ChatbotEngine
from app.services.message_processor import procesar_mensaje
from app.utils.logger import get_logger

logger = get_logger(__name__)


def register_handlers(bot: GreenAPIBot, engine: ChatbotEngine):
    """Registra todos los manejadores de eventos del bot.

    Args:
        bot (GreenAPIBot): La instancia del bot de GreenAPI.
        engine (ChatbotEngine): La instancia del motor del chatbot.
    """

    @bot.router.message()
    def handle_incoming_message(notification: Notification) -> None:
        """Manejador principal para todos los mensajes de texto entrantes.

        Args:
            notification (Notification): El objeto de notificación de la API.
        """
        user_message = notification.message_text
        user_id = notification.sender or "unknown"

        try:
            respuesta = procesar_mensaje(engine, user_id, user_message)
            if respuesta:
                notification.answer(respuesta)
        except Exception as e:
            logger.error(f"Error procesando mensaje de {user_id}: {e}", exc_info=True)
            try:
                notification.answer("⚠️ Ocurrió un error procesando tu mensaje. Por favor intenta de nuevo.")
            except Exception:
                logger.error("No se pudo enviar mensaje de error al usuario.", exc_info=True)

