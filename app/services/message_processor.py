# -*- coding: utf-8 -*-
"""Procesador de Mensajes del Chatbot.

Este módulo contiene la lógica de negocio para procesar mensajes
de usuario, incluyendo comandos, manejo de estados multi-turno y
delegación al motor de IA. Está diseñado para ser independiente de
la infraestructura de Green-API, permitiendo pruebas locales.
"""
from typing import Optional

from app.services import state_manager, inventory_service
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


def procesar_mensaje(engine: ChatbotEngine, usuario: str, mensaje: str) -> Optional[str]:
    """Procesa un mensaje de usuario y retorna la respuesta del bot.

    Maneja comandos conocidos, estados multi-turno (menú, espera de
    producto) y finalmente delega en el motor de IA para texto plano.

    Args:
        engine (ChatbotEngine): Instancia del motor del chatbot.
        usuario (str): Identificador único del usuario (ej. número).
        mensaje (str): Texto del mensaje enviado por el usuario.

    Returns:
        Optional[str]: La respuesta del bot, o None si el mensaje
                       estaba vacío y no se generó respuesta.
    """
    logger.debug(f"Mensaje recibido de '{usuario}': '{mensaje}'")

    if not mensaje:
        logger.warning(f"Mensaje vacío de {usuario}. Ignorando.")
        return None

    comando = mensaje.strip().lower()

    # --- Comandos de inicio / menú ---
    if comando in [COMMAND_START, "hola", "menu", "menú"]:
        logger.info(f"Mostrando menú principal a {usuario}")
        state_manager.set_state(usuario, state_manager.STATE_MENU_PRINCIPAL)
        return WELCOME_MESSAGE

    # --- Manejo de estados multi-turno ---
    estado_actual = state_manager.get_state(usuario)

    if estado_actual == state_manager.STATE_MENU_PRINCIPAL:
        if comando == "1":
            state_manager.set_state(usuario, state_manager.STATE_ESPERANDO_PRODUCTO_STOCK)
            return "📦 Por favor, escribe el nombre del producto para consultar su stock:"
        elif comando == "2":
            state_manager.set_state(usuario, state_manager.STATE_ESPERANDO_PRODUCTO_PRECIO)
            return "💰 Por favor, escribe el nombre del producto para consultar su precio:"
        elif comando == "3":
            return f"{CONTACTO_MESSAGE}\n\n{HORARIO_MESSAGE}"
        elif comando == "4":
            state_manager.clear_state(usuario)
            return "Modo IA activado 🤖. Escribe tu pregunta libremente:"
        else:
            return "⚠️ Opción no válida. Por favor, envía 1, 2, 3 o 4."

    if estado_actual in [
        state_manager.STATE_ESPERANDO_PRODUCTO_STOCK,
        state_manager.STATE_ESPERANDO_PRODUCTO_PRECIO,
    ]:
        producto_info = inventory_service.buscar_producto(mensaje)
        state_manager.set_state(usuario, state_manager.STATE_MENU_PRINCIPAL)

        if not producto_info:
            return (
                f"❌ No encontré ningún producto que coincida con '{mensaje}'.\n\n"
                + WELCOME_MESSAGE
            )

        if estado_actual == state_manager.STATE_ESPERANDO_PRODUCTO_STOCK:
            return (
                f"📦 *Stock disponible*\n"
                f"Producto: {producto_info['nombre']}\n"
                f"Cantidad: {producto_info['stock']} unidades\n\n"
                + WELCOME_MESSAGE
            )
        else:
            return (
                f"💰 *Precio*\n"
                f"Producto: {producto_info['nombre']}\n"
                f"Precio: ${producto_info['precio']:.2f}\n\n"
                + WELCOME_MESSAGE
            )

    # --- Comandos directos ---
    if comando == COMMAND_HELP:
        logger.info("Comando /ayuda recibido.")
        return HELP_MESSAGE

    if comando == COMMAND_STOCK:
        logger.info("Comando /stock recibido.")
        return STOCK_MESSAGE

    if comando == COMMAND_PRECIO:
        logger.info("Comando /precio recibido.")
        return PRECIO_MESSAGE

    if comando == COMMAND_CONTACTO:
        logger.info("Comando /contacto recibido.")
        return CONTACTO_MESSAGE

    if comando == COMMAND_HORARIO:
        logger.info("Comando /horario recibido.")
        return HORARIO_MESSAGE

    # --- Procesamiento por el motor de IA ---
    return engine.responder(mensaje)
