# -*- coding: utf-8 -*-
"""Módulo de Logging Centralizado.

Configura un logger de proyecto ("app") con dos handlers:
un archivo rotativo por tamaño (`RotatingFileHandler`) y salida a consola.
Es idempotente: `configurar_logging()` no duplica handlers si ya existen.
"""
import logging
import logging.handlers

from app import config

_FORMATO = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'


def _handler_archivo_rotatorio() -> logging.Handler:
    """Construye el handler de archivo con rotación por tamaño.

    Returns:
        logging.Handler: Handler rotativo apuntando a `config.LOG_FILE_PATH`.
    """
    return logging.handlers.RotatingFileHandler(
        config.LOG_FILE_PATH,
        maxBytes=config.LOG_MAX_BYTES,
        backupCount=config.LOG_BACKUP_COUNT,
        encoding="utf-8",
    )


def configurar_logging(raiz: str = "app") -> logging.Logger:
    """(Re)configura el logger del proyecto con handlers rotativos y consola.

    Si el logger ya tiene handlers, no se agregan nuevamente (idempotente).

    Args:
        raiz (str): Nombre del logger raíz del proyecto.

    Returns:
        logging.Logger: Logger raíz configurado.
    """
    logger_raiz = logging.getLogger(raiz)
    logger_raiz.setLevel(logging.INFO)

    if logger_raiz.handlers:
        return logger_raiz

    formatter = logging.Formatter(_FORMATO)

    handler_archivo = _handler_archivo_rotatorio()
    handler_archivo.setFormatter(formatter)

    handler_consola = logging.StreamHandler()
    handler_consola.setFormatter(formatter)

    logger_raiz.addHandler(handler_archivo)
    logger_raiz.addHandler(handler_consola)
    return logger_raiz


# Configuración inicial al importar el módulo.
configurar_logging()


def get_logger(name: str) -> logging.Logger:
    """Retorna un logger configurado.

    Args:
        name (str): Nombre del módulo que solicita el logger.

    Returns:
        logging.Logger: Instancia del logger.
    """
    return logging.getLogger(name)