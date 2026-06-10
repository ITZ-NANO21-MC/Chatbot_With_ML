# -*- coding: utf-8 -*-
"""Módulo de Logging Centralizado."""
import logging
from app import config

# Configuración centralizada de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE_PATH),
        logging.StreamHandler()
    ]
)

def get_logger(name: str) -> logging.Logger:
    """Retorna un logger configurado.
    
    Args:
        name (str): Nombre del módulo que solicita el logger.
        
    Returns:
        logging.Logger: Instancia del logger.
    """
    return logging.getLogger(name)
