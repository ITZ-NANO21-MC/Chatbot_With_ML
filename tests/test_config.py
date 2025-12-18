# -*- coding: utf-8 -*-
"""Pruebas Unitarias para el Módulo de Configuración.

Este módulo verifica que la configuración de la aplicación se cargue
correctamente desde las variables de entorno.
"""

import os
import importlib
from app import config

def test_config_loading(monkeypatch):
    """Verifica que las variables de entorno se carguen en el módulo de configuración.

    Utiliza monkeypatch para establecer temporalmente las variables de entorno
    y luego recarga el módulo de configuración para asegurar que toma los
    nuevos valores.

    Args:
        monkeypatch: Fixture de pytest para modificar módulos, diccionarios o
                     variables de entorno.
    """
    # 1. Establecer variables de entorno de prueba
    test_id = "test_instance_123"
    test_token = "test_token_abc"
    monkeypatch.setenv("ID_INSTANCE", test_id)
    monkeypatch.setenv("API_TOKEN_INSTANCE", test_token)

    # 2. Recargar el módulo de configuración para que lea las nuevas variables
    importlib.reload(config)

    # 3. Verificar que las variables del módulo coincidan
    assert config.ID_INSTANCE == test_id
    assert config.API_TOKEN_INSTANCE == test_token
    assert config.LOG_FILE_PATH == "chatbot_operations.log" # Probar valor por defecto

    # Limpiar las variables después de la prueba
    monkeypatch.delenv("ID_INSTANCE")
    monkeypatch.delenv("API_TOKEN_INSTANCE")
