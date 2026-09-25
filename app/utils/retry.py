# -*- coding: utf-8 -*-
"""Utilidad de reintentos con backoff exponencial.

Permite envolver funciones de I/O de red (envíos a la API de WhatsApp)
para que errores transitorios (timeout, conexión) se reintenten
automáticamente antes de relanzar la excepción al llamador.
"""
import time
from functools import wraps
from typing import Callable, Tuple, Type

from app.utils.logger import get_logger

logger = get_logger(__name__)

# Excepciones consideradas transitorias por defecto.
EXCEPCIONES_TRANSITORIAS: Tuple[Type[BaseException], ...] = (
    ConnectionError,
    TimeoutError,
    OSError,
)


def con_reintentos(
    intentos: int = 3,
    retraso_base: float = 1.0,
    factor: float = 2.0,
    excepciones: Tuple[Type[BaseException], ...] = EXCEPCIONES_TRANSITORIAS,
) -> Callable:
    """Retorna un decorador que reintenta la función ante fallos transitorios.

    Args:
        intentos (int): Número máximo de intentos (debe ser >= 1).
        retraso_base (float): Segundos de espera entre el primer y el segundo intento.
        factor (float): Multiplicador de backoff exponencial entre intentos.
        excepciones (tuple): Excepciones consideradas transitorias; cualquier otra
            se relanza de inmediato sin reintentar.

    Returns:
        Callable: Decorador para aplicar a la función objetivo.
    """
    if intentos < 1:
        raise ValueError("'intentos' debe ser mayor o igual a 1")

    def decorator(func: Callable) -> Callable:
        nombre_funcion = getattr(func, "__name__", "función")

        @wraps(func)
        def wrapper(*args, **kwargs):
            ultima_excepcion: BaseException = None
            for intento in range(1, intentos + 1):
                try:
                    return func(*args, **kwargs)
                except excepciones as e:
                    ultima_excepcion = e
                    if intento < intentos:
                        espera = retraso_base * (factor ** (intento - 1))
                        logger.warning(
                            "Intento %d/%d de %s falló: %s. Reintentando en %.1fs.",
                            intento, intentos, nombre_funcion, e, espera,
                        )
                        time.sleep(espera)
            logger.error(
                "Se agotaron los %d intentos de %s: %s",
                intentos, nombre_funcion, ultima_excepcion,
            )
            raise ultima_excepcion
        return wrapper
    return decorator