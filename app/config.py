# -*- coding: utf-8 -*-
"""Módulo de Configuración.

Este archivo centraliza las configuraciones y credenciales
necesarias para la aplicación del chatbot.
Carga las variables de entorno desde un archivo .env.
"""
import os
from dotenv import load_dotenv

# Carga las variables de entorno desde el archivo .env
# Se asume que el archivo .env se encuentra en el directorio raíz del proyecto (Chatbot_wha)
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(dotenv_path=dotenv_path)

# --- CREDENCIALES DE GREEN-API ---
ID_INSTANCE: str = os.getenv("ID_INSTANCE")
API_TOKEN_INSTANCE: str = os.getenv("API_TOKEN_INSTANCE")

# --- CONFIGURACIÓN DEL CHATBOT ---
KNOWLEDGE_BASE_PATH: str = os.getenv("KNOWLEDGE_BASE_PATH", "app/data/knowledge_base.json")
LOG_FILE_PATH: str = os.getenv("LOG_FILE_PATH", "chatbot_operations.log")