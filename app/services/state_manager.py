# -*- coding: utf-8 -*-
"""Módulo de Gestión de Estado.

Mantiene el contexto o estado de la conversación de los usuarios en memoria (RAM).
"""

_user_states = {}

# Constantes de Estado
STATE_MENU_PRINCIPAL = "MENU_PRINCIPAL"


def get_state(user_id: str) -> str:
    """Obtiene el estado actual del usuario.

    Args:
        user_id (str): Identificador único del usuario (ej. número de teléfono).

    Returns:
        str: El estado actual, o None si no tiene estado activo.
    """
    return _user_states.get(user_id)


def set_state(user_id: str, state: str) -> None:
    """Establece el estado de un usuario.

    Args:
        user_id (str): Identificador único del usuario.
        state (str): El nuevo estado a asignar.
    """
    _user_states[user_id] = state


def clear_state(user_id: str) -> None:
    """Limpia el estado de un usuario.

    Args:
        user_id (str): Identificador único del usuario.
    """
    if user_id in _user_states:
        del _user_states[user_id]
