# -*- coding: utf-8 -*-
"""Notificaciones Programadas (Fase 6).

Envía recordatorios programados a los clientes registrados en un
archivo JSON de configuración. Es independiente del ciclo de mensajes:
se dispara por un temporizador diario en lugar del flujo entrante.
"""
import json
import os
from typing import Any, Dict, List, Optional

from app import config
from app.utils.logger import get_logger
from app.utils.retry import con_reintentos

logger = get_logger(__name__)

# Reintentos ante fallos transitorios de red en el envío de cada recordatorio.
reintentar_envio = con_reintentos(intentos=3, retraso_base=1.0)

RECORDATORIO_MENSAJE = (
    "📢 *Recordatorio*\n\n"
    "Gracias por elegirnos. Si necesitas ayuda, consultas o tu factura, "
    "escribe /factura o /ayuda. ¡Estamos para servirte!"
)


def _cargar_clientes(registro_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Carga el registro de clientes desde un archivo JSON.

    El formato esperado es una lista de objetos con al menos la clave
    `chat_id`, por ejemplo: [{"chat_id": "5891...@c.us", "nombre": "Ana"}].
    Las entradas sin `chat_id` se ignoran.

    Args:
        registro_path (Optional[str]): Ruta al archivo. Por defecto usa
            `config.CLIENTES_PATH`.

    Returns:
        List[Dict[str, Any]]: Lista de clientes con `chat_id` válido.
    """
    ruta = registro_path or config.CLIENTES_PATH
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            clientes = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.warning(f"No se pudo cargar el registro de clientes: {e}")
        return []

    if not isinstance(clientes, list):
        logger.warning("El registro de clientes no es una lista. Se ignora.")
        return []

    return [cliente for cliente in clientes if cliente.get("chat_id")]


def enviar_recordatorios_diarios(bot: Any, registro_path: Optional[str] = None) -> int:
    """Envía el recordatorio diario a cada cliente registrado.

    Args:
        bot (Any): Instancia del bot de Green-API (usa `bot.api.sending.sendMessage`).
        registro_path (Optional[str]): Ruta al registro de clientes. Por
            defecto usa `config.CLIENTES_PATH`.

    Returns:
        int: Número de recordatorios enviados correctamente.
    """
    clientes = _cargar_clientes(registro_path)
    enviados = 0

    for cliente in clientes:
        chat_id = cliente["chat_id"]
        try:
            reintentar_envio(bot.api.sending.sendMessage)(chat_id, RECORDATORIO_MENSAJE)
            enviados += 1
            logger.info(f"Recordatorio enviado a {chat_id}")
        except Exception as e:
            logger.error(f"Error enviando recordatorio a {chat_id}: {e}", exc_info=True)

    logger.info(f"Recordatorios enviados: {enviados}/{len(clientes)}")
    return enviados