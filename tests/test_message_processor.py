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
    procesar_mensaje_con_archivo,
    Respuesta,
    WELCOME_MESSAGE,
    HELP_MESSAGE,
    CONTACTO_MESSAGE,
    HORARIO_MESSAGE,
    STOCK_PROMPT,
    PRECIO_PROMPT,
    FACTURA_PROMPT_CLIENTE,
    FACTURA_PROMPT_RIF,
    FACTURA_PROMPT_CONCEPTO,
    FACTURA_PROMPT_MONTO,
    FACTURA_MONTO_INVALIDO,
    FACTURA_EXITO,
)


@pytest.fixture(autouse=True)
def limpiar_estados():
    """Limpia los estados y datos de usuario antes y después de cada prueba."""
    state_manager._user_states.clear()
    state_manager._user_data.clear()
    yield
    state_manager._user_states.clear()
    state_manager._user_data.clear()


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


@patch("app.services.message_processor.inventory_service.buscar_producto")
def test_comando_stock_directo(mock_buscar, engine):
    """Comando /stock debe pedir el producto y pasar al estado de espera de stock."""
    respuesta = procesar_mensaje(engine, "user1", "/stock")
    assert respuesta == STOCK_PROMPT
    assert state_manager.get_state("user1") == state_manager.STATE_ESPERANDO_PRODUCTO_STOCK
    mock_buscar.assert_not_called()


@patch("app.services.message_processor.inventory_service.buscar_producto")
def test_comando_precio_directo(mock_buscar, engine):
    """Comando /precio debe pedir el producto y pasar al estado de espera de precio."""
    respuesta = procesar_mensaje(engine, "user1", "/precio")
    assert respuesta == PRECIO_PROMPT
    assert state_manager.get_state("user1") == state_manager.STATE_ESPERANDO_PRODUCTO_PRECIO
    mock_buscar.assert_not_called()


@patch("app.services.message_processor.inventory_service.buscar_producto")
def test_comando_stock_ejecuta_flujo_inventario(mock_buscar, engine):
    """Tras /stock, enviar un producto debe consultar el inventario real."""
    mock_buscar.return_value = {"nombre": "Laptop", "precio": 999.99, "stock": 10}

    procesar_mensaje(engine, "user1", "/stock")
    respuesta = procesar_mensaje(engine, "user1", "Laptop")

    assert "Stock disponible" in respuesta
    assert "Laptop" in respuesta
    assert state_manager.get_state("user1") == state_manager.STATE_MENU_PRINCIPAL
    mock_buscar.assert_called_once_with("Laptop")


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


# =============================================================================
# Flujo de facturación (/factura)
# =============================================================================

def test_comando_factura_inicia_flujo(engine):
    """Comando /factura debe iniciar el flujo de recolección de datos."""
    respuesta = procesar_mensaje(engine, "user1", "/factura")

    assert respuesta == FACTURA_PROMPT_CLIENTE
    assert state_manager.get_state("user1") == state_manager.STATE_ESPERANDO_DETALLE_FACTURA
    assert state_manager.get_datos("user1") == {}


@patch("app.services.message_processor.invoice_service.generar_factura")
def test_flujo_factura_completo_genera_pdf(mock_generar, engine):
    """El flujo completo de 4 pasos debe generar la factura y adjuntar el PDF."""
    mock_generar.return_value = "/tmp/facturas/factura_0001.pdf"

    procesar_mensaje(engine, "user1", "/factura")
    assert procesar_mensaje(engine, "user1", "Ana Perez") == FACTURA_PROMPT_RIF
    assert procesar_mensaje(engine, "user1", "V-12345678") == FACTURA_PROMPT_CONCEPTO
    assert procesar_mensaje(engine, "user1", "Soporte mensual") == FACTURA_PROMPT_MONTO

    respuesta = procesar_mensaje_con_archivo(engine, "user1", "120.50")

    assert respuesta == Respuesta(FACTURA_EXITO, archivo="/tmp/facturas/factura_0001.pdf")
    assert state_manager.get_state("user1") == state_manager.STATE_MENU_PRINCIPAL
    assert state_manager.get_datos("user1") is None

    mock_generar.assert_called_once()
    factura = mock_generar.call_args.args[0]
    assert factura.cliente == "Ana Perez"
    assert factura.cedula_rif == "V-12345678"
    assert factura.concepto == "Soporte mensual"
    assert factura.monto == 120.5


@patch("app.services.message_processor.invoice_service.generar_factura")
def test_flujo_factura_monto_invalido_mantiene_flujo(mock_generar, engine):
    """Un monto inválido debe pedir reintentar sin perder los datos previos."""
    mock_generar.return_value = "/tmp/facturas/factura_0001.pdf"

    procesar_mensaje(engine, "user1", "/factura")
    procesar_mensaje(engine, "user1", "Ana Perez")
    procesar_mensaje(engine, "user1", "V-12345678")
    procesar_mensaje(engine, "user1", "Soporte mensual")

    respuesta_error = procesar_mensaje(engine, "user1", "abc")

    assert respuesta_error == FACTURA_MONTO_INVALIDO
    assert state_manager.get_state("user1") == state_manager.STATE_ESPERANDO_DETALLE_FACTURA
    assert state_manager.get_datos("user1")["concepto"] == "Soporte mensual"

    respuesta_ok = procesar_mensaje(engine, "user1", "150,5")

    assert respuesta_ok == FACTURA_EXITO
    mock_generar.assert_called_once()
    assert mock_generar.call_args.args[0].monto == 150.5


@patch("app.services.message_processor.invoice_service.generar_factura")
def test_flujo_factura_monto_no_positivo_error(mock_generar, engine):
    """Monto <= 0 debe mostrar mensaje de error generado y cerrar el flujo."""
    mock_generar.side_effect = ValueError(
        "El monto debe ser un número mayor que cero."
    )

    procesar_mensaje(engine, "user1", "/factura")
    procesar_mensaje(engine, "user1", "Ana Perez")
    procesar_mensaje(engine, "user1", "V-12345678")
    procesar_mensaje(engine, "user1", "Soporte mensual")

    respuesta = procesar_mensaje(engine, "user1", "0")

    assert "No se pudo generar la factura" in respuesta
    assert state_manager.get_state("user1") is None
    assert state_manager.get_datos("user1") is None
