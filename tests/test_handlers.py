# -*- coding: utf-8 -*-
"""Pruebas Unitarias para los Manejadores de la API (message_handler).

Este módulo prueba la capa de integración con Green-API, verificando
que el handler extrae correctamente los datos de Notification y delega
en message_processor.procesar_mensaje().
"""
import pytest
from unittest.mock import MagicMock, patch

from app.handlers.message_handler import register_handlers
from app.services.message_processor import Respuesta


@pytest.fixture
def mock_bot():
    """Crea un mock de GreenAPIBot con un router funcional."""
    bot = MagicMock()
    bot.router.message.return_value = lambda func: func
    return bot


@pytest.fixture
def mock_engine():
    """Crea un mock del ChatbotEngine."""
    return MagicMock()


def test_handler_delega_en_procesar_mensaje(mock_bot, mock_engine):
    """Verifica que el handler llame a procesar_mensaje_con_archivo y envíe texto."""
    # Capturar la función handler que se registra
    handlers = []
    mock_bot.router.message.return_value = lambda func: handlers.append(func)

    register_handlers(mock_bot, mock_engine)
    assert len(handlers) == 1

    handler = handlers[0]

    # Simular notificación
    mock_notification = MagicMock()
    mock_notification.message_text = "Hola"
    mock_notification.sender = "user123"

    # Mockear procesar_mensaje_con_archivo dentro del handler
    with patch(
        "app.handlers.message_handler.procesar_mensaje_con_archivo"
    ) as mock_procesar:
        mock_procesar.return_value = Respuesta("¡Hola! ¿En qué puedo ayudarte?")
        handler(mock_notification)

        mock_procesar.assert_called_once_with(mock_engine, "user123", "Hola")
        mock_notification.answer.assert_called_once_with("¡Hola! ¿En qué puedo ayudarte?")
        mock_notification.answer_with_file.assert_not_called()


def test_handler_envia_archivo_cuando_hay_pdf(mock_bot, mock_engine):
    """Una respuesta con archivo debe enviarse con answer_with_file."""
    handlers = []
    mock_bot.router.message.return_value = lambda func: handlers.append(func)
    register_handlers(mock_bot, mock_engine)
    handler = handlers[0]

    mock_notification = MagicMock()
    mock_notification.message_text = "150"
    mock_notification.sender = "user123"

    with patch(
        "app.handlers.message_handler.procesar_mensaje_con_archivo"
    ) as mock_procesar:
        mock_procesar.return_value = Respuesta(
            "✅ Factura generada.", archivo="/tmp/facturas/factura_0001.pdf"
        )
        handler(mock_notification)

        mock_notification.answer.assert_not_called()
        mock_notification.answer_with_file.assert_called_once_with(
            "/tmp/facturas/factura_0001.pdf",
            file_name="factura_0001.pdf",
            caption="✅ Factura generada.",
        )


def test_handler_mensaje_vacio_no_envia_respuesta(mock_bot, mock_engine):
    """Mensaje vacío no debe llamar a answer."""
    handlers = []
    mock_bot.router.message.return_value = lambda func: handlers.append(func)
    register_handlers(mock_bot, mock_engine)
    handler = handlers[0]

    mock_notification = MagicMock()
    mock_notification.message_text = ""
    mock_notification.sender = "user123"

    with patch(
        "app.handlers.message_handler.procesar_mensaje_con_archivo"
    ) as mock_procesar:
        mock_procesar.return_value = None
        handler(mock_notification)

        mock_notification.answer.assert_not_called()
        mock_notification.answer_with_file.assert_not_called()


def test_handler_error_envia_mensaje_fallo(mock_bot, mock_engine):
    """Una excepción en procesar_mensaje debe enviar mensaje de error."""
    handlers = []
    mock_bot.router.message.return_value = lambda func: handlers.append(func)
    register_handlers(mock_bot, mock_engine)
    handler = handlers[0]

    mock_notification = MagicMock()
    mock_notification.message_text = "Hola"
    mock_notification.sender = "user123"

    with patch(
        "app.handlers.message_handler.procesar_mensaje_con_archivo"
    ) as mock_procesar:
        mock_procesar.side_effect = RuntimeError("Fallo inesperado")
        handler(mock_notification)

        mock_notification.answer.assert_called_once_with(
            "⚠️ Ocurrió un error procesando tu mensaje. Por favor intenta de nuevo."
        )


def test_handler_usuario_desconocido_usa_unknown(mock_bot, mock_engine):
    """Si sender es None, debe usar 'unknown' como usuario."""
    handlers = []
    mock_bot.router.message.return_value = lambda func: handlers.append(func)
    register_handlers(mock_bot, mock_engine)
    handler = handlers[0]

    mock_notification = MagicMock()
    mock_notification.message_text = "Hola"
    mock_notification.sender = ""

    with patch(
        "app.handlers.message_handler.procesar_mensaje_con_archivo"
    ) as mock_procesar:
        mock_procesar.return_value = Respuesta("Respuesta")
        handler(mock_notification)

        mock_procesar.assert_called_once_with(mock_engine, "unknown", "Hola")
        mock_notification.answer.assert_called_once_with("Respuesta")
