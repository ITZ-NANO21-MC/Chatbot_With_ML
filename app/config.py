# -*- coding: utf-8 -*-
"""Módulo de Configuración.

Este archivo centraliza las configuraciones y credenciales
necesarias para la aplicación del chatbot.
Carga las variables de entorno desde un archivo .env y valida
que las credenciales críticas estén presentes.
"""
import os
from dotenv import load_dotenv

# Carga las variables de entorno desde el archivo .env
# Se busca el .env en el directorio raíz del proyecto
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
dotenv_path = os.path.join(_project_root, '.env')
load_dotenv(dotenv_path=dotenv_path)

# --- CREDENCIALES DE GREEN-API ---
ID_INSTANCE: str = os.getenv("ID_INSTANCE", "")
API_TOKEN_INSTANCE: str = os.getenv("API_TOKEN_INSTANCE", "")

# --- CONFIGURACIÓN DEL CHATBOT ---
KNOWLEDGE_BASE_PATH: str = os.getenv(
    "KNOWLEDGE_BASE_PATH",
    os.path.join(_project_root, "app", "data", "knowledge_base.json")
)
LOG_FILE_PATH: str = os.getenv(
    "LOG_FILE_PATH",
    os.path.join(_project_root, "chatbot_operations.log")
)

# --- UMBRALES DE CONFIANZA (configurables) ---
TFIDF_CONFIDENCE_THRESHOLD: float = float(os.getenv("TFIDF_THRESHOLD", "0.3"))
FUZZY_SCORE_THRESHOLD: int = int(os.getenv("FUZZY_THRESHOLD", "70"))

# --- CONFIGURACIÓN DE INVENTARIO (Fase 4) ---
# Tipos soportados: 'sqlite' o 'csv'
INVENTORY_SOURCE_TYPE: str = os.getenv("INVENTORY_SOURCE_TYPE", "sqlite")
INVENTORY_SQLITE_PATH: str = os.getenv(
    "INVENTORY_SQLITE_PATH",
    os.path.join(_project_root, "app", "data", "inventory.db")
)
INVENTORY_CSV_PATH: str = os.getenv(
    "INVENTORY_CSV_PATH",
    os.path.join(_project_root, "app", "data", "inventory.csv")
)


def validate_credentials() -> bool:
    """Valida que las credenciales de Green-API estén configuradas.

    Returns:
        bool: True si las credenciales están presentes, False si no.
    """
    if not ID_INSTANCE or not API_TOKEN_INSTANCE:
        return False
    return True