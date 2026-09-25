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
# Rotación del log (Fase 7): tamaño máximo por archivo y cantidad de respaldos.
LOG_MAX_BYTES: int = int(os.getenv("LOG_MAX_BYTES", "5242880"))
LOG_BACKUP_COUNT: int = int(os.getenv("LOG_BACKUP_COUNT", "3"))

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

# --- CONFIGURACIÓN DE FACTURACIÓN (Fase 6) ---
NEGOCIO_NOMBRE: str = os.getenv("NEGOCIO_NOMBRE", "Mi Negocio")
FACTURAS_PATH: str = os.getenv(
    "FACTURAS_PATH",
    os.path.join(_project_root, "app", "data", "facturas")
)

# --- CONFIGURACIÓN DE NOTIFICACIONES (Fase 6) ---
CLIENTES_PATH: str = os.getenv(
    "CLIENTES_PATH",
    os.path.join(_project_root, "app", "data", "clientes.json")
)

# --- CONFIGURACIÓN DE REPORTES (Fase 7) ---
# Teléfono/cuenta WhatsApp del dueño (p. ej. "5891...@c.us"); /reporte
# solo responde a este identificador.
OWNER_PHONE: str = os.getenv("OWNER_PHONE", "")
# Destinatario del reporte por email y credenciales SMTP (se setean en .env).
OWNER_EMAIL: str = os.getenv("OWNER_EMAIL", "")
SMTP_HOST: str = os.getenv("SMTP_HOST", "")
SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER: str = os.getenv("SMTP_USER", "")
SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM: str = os.getenv("SMTP_FROM", SMTP_USER)
# 'true'/'1'/'si' → conexión SMTP_SSL; en otro caso STARTTLS (puerto 587).
SMTP_SSL: bool = os.getenv("SMTP_SSL", "").lower() in ("1", "true", "si", "yes")


def validate_credentials() -> bool:
    """Valida que las credenciales de Green-API estén configuradas.

    Returns:
        bool: True si las credenciales están presentes, False si no.
    """
    if not ID_INSTANCE or not API_TOKEN_INSTANCE:
        return False
    return True