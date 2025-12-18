# -*- coding: utf-8 -*-
"""Módulo de Rutas de la API.

Este archivo define los manejadores (handlers) para las notificaciones
entrantes de la API de WhatsApp, como los mensajes de texto.
"""
from whatsapp_chatbot_python import GreenAPIBot, Notification
from app.chatbot.engine import ChatbotEngine


def register_handlers(bot: GreenAPIBot, engine: ChatbotEngine):
    """Registra todos los manejadores de eventos del bot.

    Esta función centraliza la asignación de funciones a los eventos
    del bot, como la llegada de un nuevo mensaje.

    Args:
        bot (GreenAPIBot): La instancia del bot de GreenAPI.
        engine (ChatbotEngine): La instancia del motor del chatbot que
                                procesará el texto.
    """

    @bot.router.message()
    def message_handler(notification: Notification) -> None:
        """
        Manejador principal para todos los mensajes de texto entrantes.

        Se activa cada vez que un usuario envía un mensaje de texto. Extrae
        el contenido, lo pasa al motor del chatbot para generar una respuesta
        y la envía de vuelta al usuario.

        Args:
            notification (Notification): El objeto de notificación de la API
                                         que contiene el mensaje y metadatos.
        """
        user_message = notification.message_text
        bot_reply = engine.responder(user_message)
        notification.answer(bot_reply)
