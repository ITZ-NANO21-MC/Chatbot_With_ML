# -*- coding: utf-8 -*-
"""Módulo de Manejadores de Mensajes.

Este archivo define los manejadores (handlers) para las notificaciones
entrantes de la API de WhatsApp. Separa la lógica de comandos (ej. /start)
de los mensajes de texto plano que se envían al motor de IA.
"""
from whatsapp_chatbot_python import GreenAPIBot, Notification

from app.services.chatbot_engine import ChatbotEngine
from app.services import state_manager, inventory_service
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
    "Por favor, elige una opción enviando el número correspondiente:\n"
    "1️⃣ Consultar stock\n"
    "2️⃣ Consultar precios\n"
    "3️⃣ Información de contacto y horario\n"
    "4️⃣ Hablar con el asistente inteligente (IA)"
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

        user_id = notification.sender
        if not user_id:
            user_id = "unknown"

        # --- Procesamiento de Comandos ---
        command = user_message.strip().lower()

        if command in [COMMAND_START, "hola", "menu", "menú"]:
            logger.info(f"Mostrando menú principal a {user_id}")
            state_manager.set_state(user_id, state_manager.STATE_MENU_PRINCIPAL)
            notification.answer(WELCOME_MESSAGE)
            return

        current_state = state_manager.get_state(user_id)
        if current_state == state_manager.STATE_MENU_PRINCIPAL:
            if command == "1":
                state_manager.set_state(user_id, state_manager.STATE_ESPERANDO_PRODUCTO_STOCK)
                notification.answer("📦 Por favor, escribe el nombre del producto para consultar su stock:")
                return
            elif command == "2":
                state_manager.set_state(user_id, state_manager.STATE_ESPERANDO_PRODUCTO_PRECIO)
                notification.answer("💰 Por favor, escribe el nombre del producto para consultar su precio:")
                return
            elif command == "3":
                notification.answer(f"{CONTACTO_MESSAGE}\n\n{HORARIO_MESSAGE}")
                return
            elif command == "4":
                state_manager.clear_state(user_id)
                notification.answer("Modo IA activado 🤖. Escribe tu pregunta libremente:")
                return
            else:
                notification.answer("⚠️ Opción no válida. Por favor, envía 1, 2, 3 o 4.")
                return

        if current_state in [state_manager.STATE_ESPERANDO_PRODUCTO_STOCK, state_manager.STATE_ESPERANDO_PRODUCTO_PRECIO]:
            producto_info = inventory_service.buscar_producto(user_message)
            state_manager.set_state(user_id, state_manager.STATE_MENU_PRINCIPAL)
            
            if not producto_info:
                notification.answer(
                    f"❌ No encontré ningún producto que coincida con '{user_message}'.\n\n" + WELCOME_MESSAGE
                )
                return
                
            if current_state == state_manager.STATE_ESPERANDO_PRODUCTO_STOCK:
                notification.answer(
                    f"📦 *Stock disponible*\n"
                    f"Producto: {producto_info['nombre']}\n"
                    f"Cantidad: {producto_info['stock']} unidades\n\n" + WELCOME_MESSAGE
                )
            else:
                notification.answer(
                    f"💰 *Precio*\n"
                    f"Producto: {producto_info['nombre']}\n"
                    f"Precio: ${producto_info['precio']:.2f}\n\n" + WELCOME_MESSAGE
                )
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
