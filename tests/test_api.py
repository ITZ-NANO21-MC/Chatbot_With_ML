# -*- coding: utf-8 -*-
"""Pruebas Unitarias para los Manejadores de la API (routes).

Este módulo prueba los manejadores de notificaciones de la API,
asegurando que procesan correctamente los eventos entrantes y llaman
a los componentes adecuados (como el motor del chatbot).
"""

import pytest
from unittest.mock import MagicMock
from app.api.routes import register_handlers

@pytest.fixture
def mock_bot():
    """Crea un mock de GreenAPIBot con un router funcional."""
    bot = MagicMock()
    # Simular el decorador de router
    bot.router.message.return_value = lambda func: func
    return bot

@pytest.fixture
def mock_engine():
    """Crea un mock del ChatbotEngine."""
    engine = MagicMock()
    engine.responder.return_value = "Respuesta de prueba"
    return engine

def test_message_handler_integration(mock_bot, mock_engine):
    """
    Prueba la integración del manejador de mensajes.

    Verifica que:
    1. El manejador de mensajes se registra correctamente.
    2. Al recibir una notificación, se llama al motor con el texto correcto.
    3. La respuesta del motor se envía de vuelta usando el método 'answer'.

    Args:
        mock_bot: Fixture que proporciona un bot simulado.
        mock_engine: Fixture que proporciona un motor de chatbot simulado.
    """
    # 1. Registrar los manejadores en el bot simulado
    # Esto adjuntará 'message_handler' al bot
    register_handlers(mock_bot, mock_engine)
    
    # 2. Simular una notificación de mensaje entrante
    mock_notification = MagicMock()
    mock_notification.message_text = "Hola mundo"

    # 3. Encontrar y llamar directamente al manejador registrado
    # El decorador @bot.router.message() devuelve la propia función,
    # así que necesitamos una forma de capturarla. Un enfoque más directo
    # es probar la función 'message_handler' directamente si estuviera disponible,
    # pero aquí está anidada.
    #
    # Truco: vamos a definir un manejador y a capturarlo
    handler_func = []
    mock_bot.router.message.return_value = lambda func: handler_func.append(func)
    
    # Volver a registrar para capturar la función
    register_handlers(mock_bot, mock_engine)
    
    # Asegurarse de que capturamos el manejador
    assert len(handler_func) == 1
    message_handler = handler_func[0]

    # 4. Ejecutar el manejador con la notificación simulada
    message_handler(mock_notification)

    # 5. Verificar las interacciones
    # Se llamó a 'responder' con el texto del mensaje
    mock_engine.responder.assert_called_once_with("Hola mundo")
    # Se llamó a 'answer' con la respuesta del motor
    mock_notification.answer.assert_called_once_with("Respuesta de prueba")
