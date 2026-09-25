# -*- coding: utf-8 -*-
"""Pruebas Unitarias para la Gestión de Estado.

Verifica el ciclo de vida de los estados por usuario y el acceso
concurrente seguro (thread-safety).
"""
import threading

import pytest

from app.services import state_manager


@pytest.fixture(autouse=True)
def limpiar_estados():
    """Limpia los estados y datos usados en las pruebas, antes y después de cada test."""
    for usuario in ["user1", "user2", "inexistente"]:
        state_manager.clear_state(usuario)
        state_manager.clear_datos(usuario)
    yield
    for usuario in ["user1", "user2", "inexistente"]:
        state_manager.clear_state(usuario)
        state_manager.clear_datos(usuario)


def test_set_y_get_state():
    """Un estado asignado debe poder leerse."""
    state_manager.set_state("user1", state_manager.STATE_MENU_PRINCIPAL)
    assert state_manager.get_state("user1") == state_manager.STATE_MENU_PRINCIPAL


def test_get_state_sin_estado_devuelve_none():
    """Un usuario sin estado activo debe devolver None."""
    assert state_manager.get_state("inexistente") is None


def test_clear_state_elimina_estado():
    """clear_state debe eliminar el estado del usuario."""
    state_manager.set_state("user1", state_manager.STATE_ESPERANDO_PRODUCTO_STOCK)
    state_manager.clear_state("user1")
    assert state_manager.get_state("user1") is None


def test_estados_aislados_por_usuario():
    """Los estados de distintos usuarios no deben interferirse."""
    state_manager.set_state("user1", state_manager.STATE_MENU_PRINCIPAL)
    state_manager.set_state("user2", state_manager.STATE_ESPERANDO_PRODUCTO_PRECIO)

    assert state_manager.get_state("user1") == state_manager.STATE_MENU_PRINCIPAL
    assert state_manager.get_state("user2") == state_manager.STATE_ESPERANDO_PRODUCTO_PRECIO


def test_acceso_concurrente_no_pierde_estados():
    """Escrituras concurrentes de hilos distintos no deben corromper los estados."""
    def escribir_y_leer(usuario, estado):
        for _ in range(100):
            state_manager.set_state(usuario, estado)
            assert state_manager.get_state(usuario) == estado

    hilos = [
        threading.Thread(
            target=escribir_y_leer,
            args=("user1", state_manager.STATE_MENU_PRINCIPAL),
        ),
        threading.Thread(
            target=escribir_y_leer,
            args=("user2", state_manager.STATE_ESPERANDO_PRODUCTO_STOCK),
        ),
    ]
    for hilo in hilos:
        hilo.start()
    for hilo in hilos:
        hilo.join()

    assert state_manager.get_state("user1") == state_manager.STATE_MENU_PRINCIPAL
    assert state_manager.get_state("user2") == state_manager.STATE_ESPERANDO_PRODUCTO_STOCK


def test_set_y_get_datos():
    """Los datos acumulados deben poder escribirse y leerse."""
    state_manager.set_datos("user1", {"cliente": "Ana"})
    assert state_manager.get_datos("user1") == {"cliente": "Ana"}


def test_get_datos_sin_datos_devuelve_none():
    """Un usuario sin datos acumulados debe devolver None."""
    assert state_manager.get_datos("inexistente") is None


def test_clear_datos_elimina_datos():
    """clear_datos debe eliminar los datos acumulados del usuario."""
    state_manager.set_datos("user1", {"cliente": "Ana"})
    state_manager.clear_datos("user1")
    assert state_manager.get_datos("user1") is None