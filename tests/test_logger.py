# -*- coding: utf-8 -*-
"""Tests del módulo de logging rotativo (Fase 7, módulo 7.2)."""
import logging
from unittest.mock import patch

import pytest

from app import config
from app.utils import logger as logger_mod

_RAICES_PRUEBA = (
    "app.test.rotacion",
    "app.test.duplicados",
    "app.test.configuracion",
)


@pytest.fixture(autouse=True)
def _aislar_loggers_de_prueba():
    """Aísla los loggers usados en estas pruebas (sin propagar ni heredar handlers)."""
    for raiz in _RAICES_PRUEBA:
        logger_raiz = logging.getLogger(raiz)
        logger_raiz.propagate = False
        _cerrar_handlers(logger_raiz)
    yield
    for raiz in _RAICES_PRUEBA:
        _cerrar_handlers(logging.getLogger(raiz))


def _cerrar_handlers(logger_raiz: logging.Logger) -> None:
    """Cierra y elimina los handlers del logger."""
    for handler in list(logger_raiz.handlers):
        handler.close()
        logger_raiz.removeHandler(handler)


def test_valores_de_rotacion_son_enteros_positivos():
    """LOG_MAX_BYTES y LOG_BACKUP_COUNT deben parsearse como enteros válidos."""
    assert isinstance(config.LOG_MAX_BYTES, int)
    assert isinstance(config.LOG_BACKUP_COUNT, int)
    assert config.LOG_MAX_BYTES > 0
    assert config.LOG_BACKUP_COUNT >= 1


def test_escritura_al_archivo_configurado(tmp_path):
    """El logger debe escribir al archivo de LOG_FILE_PATH configurado."""
    archivo_log = tmp_path / "configurado.log"

    with patch.object(config, "LOG_FILE_PATH", str(archivo_log)), (
        patch.object(config, "LOG_MAX_BYTES", 4096)
    ), patch.object(config, "LOG_BACKUP_COUNT", 1):
        logger_mod.configurar_logging("app.test.configuracion")
        lgr = logging.getLogger("app.test.configuracion.hijo")
        lgr.setLevel(logging.INFO)
        lgr.info("mensaje de prueba de escritura")

    contenido = archivo_log.read_text(encoding="utf-8")
    assert "mensaje de prueba de escritura" in contenido


def test_la_rotacion_por_tamano_crea_respaldos(tmp_path):
    """Con maxBytes pequeño, escribir mucho debe rotar y crear respaldos .1, .2..."""
    archivo_log = tmp_path / "rotativo.log"

    with patch.object(config, "LOG_FILE_PATH", str(archivo_log)), (
        patch.object(config, "LOG_MAX_BYTES", 1024)
    ), patch.object(config, "LOG_BACKUP_COUNT", 2):
        logger_mod.configurar_logging("app.test.rotacion")
        lgr = logging.getLogger("app.test.rotacion.modulo")
        lgr.setLevel(logging.INFO)
        for i in range(300):
            lgr.info("Línea de prueba %d con bastante contenido para forzar rotación", i)

    assert archivo_log.exists()
    assert archivo_log.stat().st_size <= 1024
    respaldos = sorted(tmp_path.glob("rotativo.log.*"))
    assert len(respaldos) >= 1


def test_configurar_logging_no_duplica_handlers(tmp_path):
    """Llamar dos veces a configurar_logging no debe duplicar handlers."""
    archivo_log = tmp_path / "no_duplicados.log"

    with patch.object(config, "LOG_FILE_PATH", str(archivo_log)), (
        patch.object(config, "LOG_MAX_BYTES", 4096)
    ), patch.object(config, "LOG_BACKUP_COUNT", 1):
        logger_mod.configurar_logging("app.test.duplicados")
        cantidad_1 = len(logging.getLogger("app.test.duplicados").handlers)

        logger_mod.configurar_logging("app.test.duplicados")
        cantidad_2 = len(logging.getLogger("app.test.duplicados").handlers)

    assert cantidad_1 == 2
    assert cantidad_1 == cantidad_2