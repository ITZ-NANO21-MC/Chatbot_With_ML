# -*- coding: utf-8 -*-
"""Módulo de Manejadores de Mensajes.

Este archivo define los manejadores (handlers) para las notificaciones
entrantes de la API de WhatsApp. Separa la lógica de comandos (ej. /start)
de los mensajes de texto plano que se envían al motor de IA.
"""
from whatsapp_chatbot_python import GreenAPIBot, Notification

from app.services.chatbot_engine import ChatbotEngine
from app.utils.logger import get_logger

logger = get_logger(__name__)

# --- Constantes de Comandos ---
COMMAND_START = "/start"
COMMAND_HELP = "/ayuda"
COMMAND_STOCK = "/stock"
COMMAND_PRECIO = "/precio"
COMMAND_CONTACTO = "/contacto"
COMMAND_HORARIO = "/horario"

# --- Respuestas de Comandos ---
WELCOME_MESSAGE = (
    "👋 ¡Hola! Soy tu asistente virtual.\n\n"
    "Puedo ayudarte con consultas frecuentes.\n"
    "Escribe tu pregunta o usa /ayuda para ver las opciones disponibles."
)

STOCK_MESSAGE = "📦 Consultas de stock: ¡Próximamente estará integrado con nuestro inventario!"

PRECIO_MESSAGE = "💰 Consultas de precios: ¡Próximamente podrás consultar precios actualizados!"

CONTACTO_MESSAGE = (
    "📞 *Contacto*\n"
    "Teléfono: +58 412-1234567\n"
    "Email: contacto@empresa.com"
)

HORARIO_MESSAGE = (
    "🕒 *Horario de Atención*\n"
    "Lunes a Viernes: 9:00 AM - 5:00 PM\n"
    "Sábado: 10:00 AM - 2:00 PM"
)

HELP_MESSAGE = (
    "📋 *Comandos disponibles:*\n\n"
    "/start - Mensaje de bienvenida\n"
    "/ayuda - Ver este menú de ayuda\n"
    "/stock - Consultar disponibilidad de productos\n"
    "/precio - Consultar precios\n"
    "/contacto - Ver información de contacto\n"
    "/horario - Ver horario de atención\n\n"
    "También puedes escribirme cualquier pregunta y haré mi mejor esfuerzo "
    "para responderte. 🤖"
)


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
    def handle_incoming_message(notification: Notification) -> None:
        """Manejador principal para todos los mensajes de texto entrantes.

        Intercepta comandos conocidos (ej. /start, /ayuda) y los responde
        directamente. Los demás mensajes se envían al motor de IA.

        Args:
            notification (Notification): El objeto de notificación de la API
                                         que contiene el mensaje y metadatos.
        """
        user_message = notification.message_text

        if not user_message:
            return

        # --- Procesamiento de Comandos ---
        command = user_message.strip().lower()

        if command == COMMAND_START:
            logger.info("Comando /start recibido.")
            notification.answer(WELCOME_MESSAGE)
            return

        if command == COMMAND_HELP:
            logger.info("Comando /ayuda recibido.")
            notification.answer(HELP_MESSAGE)
            return

        if command == COMMAND_STOCK:
            logger.info("Comando /stock recibido.")
            notification.answer(STOCK_MESSAGE)
            return

        if command == COMMAND_PRECIO:
            logger.info("Comando /precio recibido.")
            notification.answer(PRECIO_MESSAGE)
            return

        if command == COMMAND_CONTACTO:
            logger.info("Comando /contacto recibido.")
            notification.answer(CONTACTO_MESSAGE)
            return

        if command == COMMAND_HORARIO:
            logger.info("Comando /horario recibido.")
            notification.answer(HORARIO_MESSAGE)
            return

        # --- Procesamiento de Texto Plano (Motor de IA) ---
        bot_reply = engine.responder(user_message)
        notification.answer(bot_reply)
