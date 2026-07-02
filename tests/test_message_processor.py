# -*- coding: utf-8 -*-
"""Pruebas Unitarias para el Procesador de Mensajes.

Este módulo prueba la lógica de comandos, estados multi-turno y
delegación al motor de IA de forma aislada, sin dependencia de
Green-API.
"""
import json
from unittest.mock import MagicMock, patch

import pytest

from app.services import state_manager
from app.services.message_processor import (
    procesar_mensaje,
    WELCOME_MESSAGE,
    HELP_MESSAGE,
    CONTACTO_MESSAGE,
    HORARIO_MESSAGE,
    STOCK_MESSAGE,
    PRECIO_MESSAGE,
)


@pytest.fixture(autouse=True)
def limpiar_estados():
    """Limpia los estados de usuario antes y después de cada prueba."""
    state_manager._user_states.clear()
    yield
    state_manager._user_states.clear()


@pytest.fixture
def engine():
    """Crea un mock del ChatbotEngine."""
    mock = MagicMock()
    mock.responder.return_value = "Respuesta del motor IA."
    return mock


# =============================================================================
# Comando /start y variantes
# =============================================================================

def test_comando_start_establece_menu_y_responde_bienvenida(engine):
    """Al enviar /start debe establecer estado MENU_PRINCIPAL y responder."""
    respuesta = procesar_mensaje(engine, "user1", "/start")
    assert respuesta == WELCOME_MESSAGE
    assert state_manager.get_state("user1") == state_manager.STATE_MENU_PRINCIPAL


def test_comando_hola_es_sinonimo_de_start(engine):
    """'hola' debe tener el mismo comportamiento que /start."""
    respuesta = procesar_mensaje(engine, "user2", "hola")
    assert respuesta == WELCOME_MESSAGE
    assert state_manager.get_state("user2") == state_manager.STATE_MENU_PRINCIPAL


def test_comando_menu_es_sinonimo_de_start(engine):
    """'menu' debe tener el mismo comportamiento que /start."""
    respuesta = procesar_mensaje(engine, "user3", "menu")
    assert respuesta == WELCOME_MESSAGE
    assert state_manager.get_state("user3") == state_manager.STATE_MENU_PRINCIPAL


# =============================================================================
# Opciones del menú principal
# =============================================================================

def test_opcion_1_stock_cambia_estado_y_pide_producto(engine):
    """Opción 1 en menú principal debe ir a ESPERANDO_PRODUCTO_STOCK."""
    state_manager.set_state("user1", state_manager.STATE_MENU_PRINCIPAL)
    respuesta = procesar_mensaje(engine, "user1", "1")
    assert "escribe el nombre del producto" in respuesta
    assert state_manager.get_state("user1") == state_manager.STATE_ESPERANDO_PRODUCTO_STOCK


def test_opcion_2_precio_cambia_estado_y_pide_producto(engine):
    """Opción 2 en menú principal debe ir a ESPERANDO_PRODUCTO_PRECIO."""
    state_manager.set_state("user1", state_manager.STATE_MENU_PRINCIPAL)
    respuesta = procesar_mensaje(engine, "user1", "2")
    assert "escribe el nombre del producto" in respuesta
    assert state_manager.get_state("user1") == state_manager.STATE_ESPERANDO_PRODUCTO_PRECIO


def test_opcion_3_muestra_contacto_y_horario(engine):
    """Opción 3 en menú principal debe mostrar contacto y horario."""
    state_manager.set_state("user1", state_manager.STATE_MENU_PRINCIPAL)
    respuesta = procesar_mensaje(engine, "user1", "3")
    assert CONTACTO_MESSAGE in respuesta
    assert HORARIO_MESSAGE in respuesta


def test_opcion_4_activa_modo_ia_y_limpia_estado(engine):
    """Opción 4 debe limpiar estado y activar modo IA."""
    state_manager.set_state("user1", state_manager.STATE_MENU_PRINCIPAL)
    respuesta = procesar_mensaje(engine, "user1", "4")
    assert "Modo IA activado" in respuesta
    assert state_manager.get_state("user1") is None


def test_opcion_invalida_en_menu_muestra_error(engine):
    """Opción inválida en menú debe mostrar mensaje de error."""
    state_manager.set_state("user1", state_manager.STATE_MENU_PRINCIPAL)
    respuesta = procesar_mensaje(engine, "user1", "9")
    assert "Opción no válida" in respuesta
    # El estado no debe cambiar
    assert state_manager.get_state("user1") == state_manager.STATE_MENU_PRINCIPAL


# =============================================================================
# Flujo de consulta de producto (stock / precio)
# =============================================================================

@patch("app.services.message_processor.inventory_service.buscar_producto")
def test_flujo_stock_producto_encontrado(mock_buscar, engine):
    """Flujo stock: producto encontrado devuelve info de stock."""
    mock_buscar.return_value = {"nombre": "Laptop", "precio": 999.99, "stock": 10}
    state_manager.set_state("user1", state_manager.STATE_ESPERANDO_PRODUCTO_STOCK)

    respuesta = procesar_mensaje(engine, "user1", "Laptop")
    assert "Stock disponible" in respuesta
    assert "Laptop" in respuesta
    assert "10" in respuesta
    # Debe volver al menú principal
    assert state_manager.get_state("user1") == state_manager.STATE_MENU_PRINCIPAL
    mock_buscar.assert_called_once_with("Laptop")


@patch("app.services.message_processor.inventory_service.buscar_producto")
def test_flujo_precio_producto_encontrado(mock_buscar, engine):
    """Flujo precio: producto encontrado devuelve info de precio."""
    mock_buscar.return_value = {"nombre": "Mouse", "precio": 25.50, "stock": 50}
    state_manager.set_state("user1", state_manager.STATE_ESPERANDO_PRODUCTO_PRECIO)

    respuesta = procesar_mensaje(engine, "user1", "Mouse")
    assert "Precio" in respuesta
    assert "Mouse" in respuesta
    assert "25.50" in respuesta
    assert state_manager.get_state("user1") == state_manager.STATE_MENU_PRINCIPAL


@patch("app.services.message_processor.inventory_service.buscar_producto")
def test_flujo_stock_producto_no_encontrado(mock_buscar, engine):
    """Flujo stock: producto no encontrado devuelve mensaje de error."""
    mock_buscar.return_value = None
    state_manager.set_state("user1", state_manager.STATE_ESPERANDO_PRODUCTO_STOCK)

    respuesta = procesar_mensaje(engine, "user1", "xyz")
    assert "No encontré ningún producto" in respuesta
    assert state_manager.get_state("user1") == state_manager.STATE_MENU_PRINCIPAL


# =============================================================================
# Comandos directos
# =============================================================================

def test_comando_ayuda(engine):
    """Comando /ayuda debe devolver el mensaje de ayuda."""
    respuesta = procesar_mensaje(engine, "user1", "/ayuda")
    assert respuesta == HELP_MESSAGE


def test_comando_stock_directo(engine):
    """Comando /stock directo debe responder mensaje de stock."""
    respuesta = procesar_mensaje(engine, "user1", "/stock")
    assert respuesta == STOCK_MESSAGE


def test_comando_precio_directo(engine):
    """Comando /precio directo debe responder mensaje de precio."""
    respuesta = procesar_mensaje(engine, "user1", "/precio")
    assert respuesta == PRECIO_MESSAGE


def test_comando_contacto_directo(engine):
    """Comando /contacto directo debe responder mensaje de contacto."""
    respuesta = procesar_mensaje(engine, "user1", "/contacto")
    assert respuesta == CONTACTO_MESSAGE


def test_comando_horario_directo(engine):
    """Comando /horario directo debe responder mensaje de horario."""
    respuesta = procesar_mensaje(engine, "user1", "/horario")
    assert respuesta == HORARIO_MESSAGE


# =============================================================================
# Delegación al motor de IA
# =============================================================================

def test_mensaje_texto_plano_va_al_motor_ia(engine):
    """Un mensaje sin comando ni estado debe delegar en engine.responder()."""
    respuesta = procesar_mensaje(engine, "user1", "¿qué es inteligencia artificial?")
    assert respuesta == "Respuesta del motor IA."
    engine.responder.assert_called_once_with("¿qué es inteligencia artificial?")


def test_estados_no_interfieren_con_texto_plano(engine):
    """Sin estado activo, un texto plano debe ir al motor IA."""
    respuesta = procesar_mensaje(engine, "user1", "dime un chiste")
    assert respuesta == "Respuesta del motor IA."


# =============================================================================
# Casos borde
# =============================================================================

def test_mensaje_vacio_retorna_none(engine):
    """Mensaje vacío debe retornar None."""
    respuesta = procesar_mensaje(engine, "user1", "")
    assert respuesta is None


def test_mensaje_solo_espacios_retorna_none(engine):
    """Mensaje de solo espacios debe retornar None."""
    respuesta = procesar_mensaje(engine, "user1", "   ")
    assert respuesta is None


def test_mensaje_none_retorna_none(engine):
    """Mensaje None debe retornar None."""
    respuesta = procesar_mensaje(engine, "user1", None)
    assert respuesta is None


def test_usuarios_diferentes_tienen_estados_independientes(engine):
    """Cada usuario debe tener su propio estado independiente."""
    procesar_mensaje(engine, "user_a", "/start")
    procesar_mensaje(engine, "user_b", "texto_plano")

    assert state_manager.get_state("user_a") == state_manager.STATE_MENU_PRINCIPAL
    assert state_manager.get_state("user_b") is None
