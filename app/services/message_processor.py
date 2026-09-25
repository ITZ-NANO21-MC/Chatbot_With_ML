# -*- coding: utf-8 -*-
"""Procesador de Mensajes del Chatbot.

Este módulo contiene la lógica de negocio para procesar mensajes
de usuario, incluyendo comandos, manejo de estados multi-turno y
delegación al motor de IA. Está diseñado para ser independiente de
la infraestructura de Green-API, permitiendo pruebas locales.
"""
from dataclasses import dataclass
from typing import Optional

from app.services import state_manager, inventory_service, invoice_service
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
COMMAND_FACTURA = "/factura"

# --- Respuestas de Comandos ---
WELCOME_MESSAGE = (
    "👋 ¡Hola! Soy tu asistente virtual.\n\n"
    "Por favor, elige una opción enviando el número correspondiente:\n"
    "1️⃣ Consultar stock\n"
    "2️⃣ Consultar precios\n"
    "3️⃣ Información de contacto y horario\n"
    "4️⃣ Hablar con el asistente inteligente (IA)"
)

STOCK_PROMPT = "📦 Por favor, escribe el nombre del producto para consultar su stock:"

PRECIO_PROMPT = "💰 Por favor, escribe el nombre del producto para consultar su precio:"

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
    "/factura - Generar una factura en PDF\n"
    "/contacto - Ver información de contacto\n"
    "/horario - Ver horario de atención\n\n"
    "También puedes escribirme cualquier pregunta y haré mi mejor esfuerzo "
    "para responderte. 🤖"
)

# --- Mensajes de facturación (Fase 6) ---
FACTURA_PROMPT_CLIENTE = (
    "🧾 Vamos a generar tu factura.\n"
    "Primero, escribe el nombre del cliente:"
)
FACTURA_PROMPT_RIF = "Ahora, escribe la cédula o RIF del cliente:"
FACTURA_PROMPT_CONCEPTO = "Escribe el concepto o servicio:"
FACTURA_PROMPT_MONTO = "Por último, escribe el monto total (ej. 150.50):"
FACTURA_MONTO_INVALIDO = "⚠️ Monto inválido. Envía solo un número (ej. 150.50):"
FACTURA_EXITO = "✅ Factura generada. Aquí tienes el archivo:"


@dataclass
class Respuesta:
    """Respuesta estructurada del procesador de mensajes.

    Attributes:
        texto (Optional[str]): Texto a enviar al usuario.
        archivo (Optional[str]): Ruta de un archivo opcional (ej. PDF).
    """
    texto: Optional[str]
    archivo: Optional[str] = None


def procesar_mensaje(engine: ChatbotEngine, usuario: str, mensaje: str) -> Optional[str]:
    """Procesa un mensaje y retorna solo el texto de la respuesta.

    Es un envoltorio compatible hacia atrás sobre la versión
    estructurada, descartando el archivo adjunto (si lo hubiera).

    Args:
        engine (ChatbotEngine): Instancia del motor del chatbot.
        usuario (str): Identificador único del usuario (ej. número).
        mensaje (str): Texto del mensaje enviado por el usuario.

    Returns:
        Optional[str]: El texto de la respuesta del bot, o None si el
                       mensaje estaba vacío.
    """
    respuesta = procesar_mensaje_con_archivo(engine, usuario, mensaje)
    return respuesta.texto if respuesta else None


def procesar_mensaje_con_archivo(
    engine: ChatbotEngine, usuario: str, mensaje: str
) -> Optional[Respuesta]:
    """Procesa un mensaje de usuario y retorna la respuesta del bot.

    Maneja comandos conocidos, estados multi-turno (menú, espera de
    producto, facturación) y finalmente delega en el motor de IA para
    texto plano. Puede incluir un archivo adjunto (ej. factura PDF).

    Args:
        engine (ChatbotEngine): Instancia del motor del chatbot.
        usuario (str): Identificador único del usuario (ej. número).
        mensaje (str): Texto del mensaje enviado por el usuario.

    Returns:
        Optional[Respuesta]: La respuesta del bot, o None si el mensaje
                             estaba vacío y no se generó respuesta.
    """
    logger.debug(f"Mensaje recibido de '{usuario}': '{mensaje}'")

    if not mensaje or not mensaje.strip():
        logger.warning(f"Mensaje vacío de {usuario}. Ignorando.")
        return None

    comando = mensaje.strip().lower()

    # --- Comandos de inicio / menú ---
    if comando in [COMMAND_START, "hola", "menu", "menú"]:
        logger.info(f"Mostrando menú principal a {usuario}")
        state_manager.set_state(usuario, state_manager.STATE_MENU_PRINCIPAL)
        return Respuesta(WELCOME_MESSAGE)

    # --- Comandos directos de inventario (acceso desde cualquier estado) ---
    if comando == COMMAND_STOCK:
        state_manager.set_state(usuario, state_manager.STATE_ESPERANDO_PRODUCTO_STOCK)
        return Respuesta(STOCK_PROMPT)

    if comando == COMMAND_PRECIO:
        state_manager.set_state(usuario, state_manager.STATE_ESPERANDO_PRODUCTO_PRECIO)
        return Respuesta(PRECIO_PROMPT)

    # --- Comando de facturación ---
    if comando == COMMAND_FACTURA:
        state_manager.set_state(usuario, state_manager.STATE_ESPERANDO_DETALLE_FACTURA)
        state_manager.set_datos(usuario, {})
        return Respuesta(FACTURA_PROMPT_CLIENTE)

    # --- Manejo de estados multi-turno ---
    estado_actual = state_manager.get_state(usuario)

    if estado_actual == state_manager.STATE_MENU_PRINCIPAL:
        if comando == "1":
            state_manager.set_state(usuario, state_manager.STATE_ESPERANDO_PRODUCTO_STOCK)
            return Respuesta(STOCK_PROMPT)
        elif comando == "2":
            state_manager.set_state(usuario, state_manager.STATE_ESPERANDO_PRODUCTO_PRECIO)
            return Respuesta(PRECIO_PROMPT)
        elif comando == "3":
            return Respuesta(f"{CONTACTO_MESSAGE}\n\n{HORARIO_MESSAGE}")
        elif comando == "4":
            state_manager.clear_state(usuario)
            return Respuesta("Modo IA activado 🤖. Escribe tu pregunta libremente:")
        else:
            return Respuesta("⚠️ Opción no válida. Por favor, envía 1, 2, 3 o 4.")

    if estado_actual in [
        state_manager.STATE_ESPERANDO_PRODUCTO_STOCK,
        state_manager.STATE_ESPERANDO_PRODUCTO_PRECIO,
    ]:
        producto_info = inventory_service.buscar_producto(mensaje)
        state_manager.set_state(usuario, state_manager.STATE_MENU_PRINCIPAL)

        if not producto_info:
            return Respuesta(
                f"❌ No encontré ningún producto que coincida con '{mensaje}'.\n\n"
                + WELCOME_MESSAGE
            )

        if estado_actual == state_manager.STATE_ESPERANDO_PRODUCTO_STOCK:
            return Respuesta(
                f"📦 *Stock disponible*\n"
                f"Producto: {producto_info['nombre']}\n"
                f"Cantidad: {producto_info['stock']} unidades\n\n"
                + WELCOME_MESSAGE
            )
        else:
            return Respuesta(
                f"💰 *Precio*\n"
                f"Producto: {producto_info['nombre']}\n"
                f"Precio: ${producto_info['precio']:.2f}\n\n"
                + WELCOME_MESSAGE
            )

    if estado_actual == state_manager.STATE_ESPERANDO_DETALLE_FACTURA:
        return _procesar_factura(usuario, mensaje)

    # --- Comandos directos ---
    if comando == COMMAND_HELP:
        logger.info("Comando /ayuda recibido.")
        return Respuesta(HELP_MESSAGE)

    if comando == COMMAND_CONTACTO:
        logger.info("Comando /contacto recibido.")
        return Respuesta(CONTACTO_MESSAGE)

    if comando == COMMAND_HORARIO:
        logger.info("Comando /horario recibido.")
        return Respuesta(HORARIO_MESSAGE)

    # --- Procesamiento por el motor de IA ---
    return Respuesta(engine.responder(mensaje))


def _procesar_factura(usuario: str, mensaje: str) -> Respuesta:
    """Recoge por pasos los datos de una factura y genera el PDF.

    El flujo espera: cliente → cédula/rif → concepto → monto. Al recibir
    el monto válido, se genera la factura con `invoice_service`.

    Args:
        usuario (str): Identificador único del usuario.
        mensaje (str): Texto enviado por el usuario (siguiente dato).

    Returns:
        Respuesta: Próxima pregunta, mensaje de error o factura generada.
    """
    datos = state_manager.get_datos(usuario) or {}

    if "cliente" not in datos:
        datos["cliente"] = mensaje
        state_manager.set_datos(usuario, datos)
        return Respuesta(FACTURA_PROMPT_RIF)

    if "cedula_rif" not in datos:
        datos["cedula_rif"] = mensaje
        state_manager.set_datos(usuario, datos)
        return Respuesta(FACTURA_PROMPT_CONCEPTO)

    if "concepto" not in datos:
        datos["concepto"] = mensaje
        state_manager.set_datos(usuario, datos)
        return Respuesta(FACTURA_PROMPT_MONTO)

    try:
        monto = float(mensaje.replace(",", "."))
    except ValueError:
        return Respuesta(FACTURA_MONTO_INVALIDO)

    datos["monto"] = monto

    try:
        factura = invoice_service.FacturaDatos(
            cliente=datos["cliente"],
            cedula_rif=datos.get("cedula_rif", ""),
            concepto=datos["concepto"],
            monto=monto,
        )
        ruta = invoice_service.generar_factura(factura)
    except ValueError as e:
        state_manager.clear_state(usuario)
        state_manager.clear_datos(usuario)
        return Respuesta(f"⚠️ No se pudo generar la factura: {e}")
    except OSError as e:
        state_manager.clear_state(usuario)
        state_manager.clear_datos(usuario)
        logger.error(f"Error de escritura de la factura: {e}", exc_info=True)
        return Respuesta("⚠️ No se pudo guardar la factura. Intenta de nuevo más tarde.")

    state_manager.set_state(usuario, state_manager.STATE_MENU_PRINCIPAL)
    state_manager.clear_datos(usuario)
    logger.info(f"Factura generada para {usuario}: {datos['cliente']}")
    return Respuesta(FACTURA_EXITO, archivo=ruta)
