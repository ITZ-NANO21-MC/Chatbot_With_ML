# -*- coding: utf-8 -*-
"""Pruebas Unitarias para el Motor del Chatbot (ChatbotEngine).

Este módulo contiene el conjunto de pruebas para la clase ChatbotEngine,
asegurando que la carga de datos, el entrenamiento y la lógica de
respuesta funcionen como se espera.
"""

import json
import pytest
from app.chatbot.engine import ChatbotEngine

@pytest.fixture
def knowledge_base_file(tmp_path):
    """Crea un archivo JSON de base de conocimiento temporal para las pruebas.

    Args:
        tmp_path: Fixture de pytest que proporciona una ruta de directorio temporal.

    Returns:
        Path: La ruta al archivo JSON temporal creado.
    """
    contenido = {
        "conocimiento": [
            {
                "pregunta_base": "horario de atencion",
                "respuesta": "Nuestro horario es de 9 AM a 6 PM.",
                "sinonimos": ["a que hora abren", "tienda abierta"]
            },
            {
                "pregunta_base": "metodos de pago",
                "respuesta": "Aceptamos tarjeta y efectivo.",
                "sinonimos": ["como puedo pagar", "aceptan credito"]
            }
        ]
    }
    file_path = tmp_path / "knowledge_base.json"
    file_path.write_text(json.dumps(contenido, ensure_ascii=False), encoding='utf-8')
    return file_path

@pytest.fixture
def engine(knowledge_base_file):
    """Inicializa una instancia de ChatbotEngine para ser usada en las pruebas.

    Args:
        knowledge_base_file: Fixture que proporciona la ruta a la base de conocimiento.

    Returns:
        ChatbotEngine: una instancia del motor del chatbot.
    """
    return ChatbotEngine(str(knowledge_base_file))

def test_engine_initialization(engine):
    """Verifica que el motor se inicialice correctamente.

    Comprueba que la base de conocimiento se cargue y que los datos
    se expandan correctamente con los sinónimos.

    Args:
        engine (ChatbotEngine): La instancia del motor a probar.
    """
    assert len(engine.base_preguntas) == 2
    assert len(engine.preguntas_expandidas) == 6  # 2 base + 4 sinónimos
    assert engine.vectorizer is not None
    assert engine.X_train.shape[0] == 6

def test_responder_exact_match(engine):
    """Prueba una coincidencia exacta con una pregunta base (alta confianza).

    Args:
        engine (ChatbotEngine): La instancia del motor a probar.
    """
    pregunta = "horario de atencion"
    respuesta = engine.responder(pregunta)
    assert respuesta == "Nuestro horario es de 9 AM a 6 PM."

def test_responder_synonym_match(engine):
    """Prueba una coincidencia usando un sinónimo (confianza media-alta).

    Args:
        engine (ChatbotEngine): La instancia del motor a probar.
    """
    pregunta = "a que hora abren"
    respuesta = engine.responder(pregunta)
    assert respuesta == "Nuestro horario es de 9 AM a 6 PM."

def test_responder_fuzzy_match(engine):
    """Prueba una coincidencia con un error tipográfico (activando fuzzy matching).

    Args:
        engine (ChatbotEngine): La instancia del motor a probar.
    """
    pregunta = "horario de atencionn"  # Error tipográfico
    respuesta = engine.responder(pregunta)
    assert respuesta == "Nuestro horario es de 9 AM a 6 PM."

def test_responder_low_confidence(engine):
    """Prueba una pregunta no relacionada que no debería encontrar respuesta.

    Args:
        engine (ChatbotEngine): La instancia del motor a probar.
    """
    pregunta = "venden pan?"
    respuesta = engine.responder(pregunta)
    assert respuesta == "No estoy seguro de entender. ¿Podrías intentar con otras palabras?"

def test_responder_empty_input(engine):
    """Prueba cómo maneja el motor una entrada vacía.

    Args:
        engine (ChatbotEngine): La instancia del motor a probar.
    """
    pregunta = ""
    respuesta = engine.responder(pregunta)
    assert respuesta == "No estoy seguro de entender. ¿Podrías intentar con otras palabras?"
