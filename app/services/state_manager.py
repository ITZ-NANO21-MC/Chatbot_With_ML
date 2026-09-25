# -*- coding: utf-8 -*-
"""Módulo de Gestión de Estado.

Mantiene el contexto o estado de la conversación de los usuarios en memoria (RAM).

El acceso concurrente es seguro mediante un RLock: GreenAPIBot procesa los
mensajes de cada usuario desde el hilo de su webhook, y un usuario puede
tener mensajes en tránsito a la vez que otro los consulta.
"""
import threading

_user_states = {}
_user_data = {}
_lock = threading.RLock()

# Constantes de Estado
STATE_MENU_PRINCIPAL = "MENU_PRINCIPAL"
STATE_ESPERANDO_PRODUCTO_STOCK = "ESPERANDO_PRODUCTO_STOCK"
STATE_ESPERANDO_PRODUCTO_PRECIO = "ESPERANDO_PRODUCTO_PRECIO"
STATE_ESPERANDO_DETALLE_FACTURA = "ESPERANDO_DETALLE_FACTURA"


def get_state(user_id: str) -> str:
    """Obtiene el estado actual del usuario.

    Args:
        user_id (str): Identificador único del usuario (ej. número de teléfono).

    Returns:
        str: El estado actual, o None si no tiene estado activo.
    """
    with _lock:
        return _user_states.get(user_id)


def set_state(user_id: str, state: str) -> None:
    """Establece el estado de un usuario.

    Args:
        user_id (str): Identificador único del usuario.
        state (str): El nuevo estado a asignar.
    """
    with _lock:
        _user_states[user_id] = state


def clear_state(user_id: str) -> None:
    """Limpia el estado de un usuario.

    Args:
        user_id (str): Identificador único del usuario.
    """
    with _lock:
        if user_id in _user_states:
            del _user_states[user_id]


def get_datos(user_id: str) -> dict:
    """Obtiene los datos acumulados de un usuario (ej. factura en curso).

    Args:
        user_id (str): Identificador único del usuario.

    Returns:
        dict: Datos asociados al usuario, o None si no hay datos.
    """
    with _lock:
        return _user_data.get(user_id)


def set_datos(user_id: str, datos: dict) -> None:
    """Establece los datos acumulados de un usuario.

    Args:
        user_id (str): Identificador único del usuario.
        datos (dict): Datos a almacenar.
    """
    with _lock:
        _user_data[user_id] = datos


def clear_datos(user_id: str) -> None:
    """Limpia los datos acumulados de un usuario.

    Args:
        user_id (str): Identificador único del usuario.
    """
    with _lock:
        _user_data.pop(user_id, None)
