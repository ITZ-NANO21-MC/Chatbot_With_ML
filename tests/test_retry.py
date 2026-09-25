# -*- coding: utf-8 -*-
"""Tests de la utilidad de reintentos (Fase 7, módulo 7.1)."""
from unittest.mock import MagicMock, patch

import pytest

from app.utils.retry import con_reintentos


@patch("app.utils.retry.time.sleep")
def test_exito_al_primer_intento_no_reintenta(mock_sleep):
    """Si la función tiene éxito al primer intento, no se reintenta."""
    funcion = MagicMock(return_value="ok")

    decorada = con_reintentos(intentos=3, retraso_base=1.0)(funcion)
    resultado = decorada()

    assert resultado == "ok"
    funcion.assert_called_once()
    mock_sleep.assert_not_called()


@patch("app.utils.retry.time.sleep")
def test_reintenta_hasta_tener_exito(mock_sleep):
    """Un fallo transitorio debe reintentarse y terminar con éxito."""
    intentos_realizados = []

    def funcion_inestable():
        intentos_realizados.append(1)
        if len(intentos_realizados) < 3:
            raise ConnectionError("Red caída")
        return "entregado"

    decorada = con_reintentos(intentos=5, retraso_base=1.0, factor=2.0)(funcion_inestable)
    resultado = decorada()

    assert resultado == "entregado"
    assert len(intentos_realizados) == 3
    assert mock_sleep.call_count == 2


@patch("app.utils.retry.time.sleep")
def test_siempre_falla_relanza_tras_agotar_intentos(mock_sleep):
    """Si falla siempre, se relanza la última excepción tras los intentos."""
    funcion = MagicMock(side_effect=TimeoutError("timeout"))

    decorada = con_reintentos(intentos=3, retraso_base=0.0)(funcion)

    with pytest.raises(TimeoutError):
        decorada()

    assert funcion.call_count == 3
    assert mock_sleep.call_count == 2


def test_excepcion_no_transitoria_no_se_reintenta():
    """Una excepción fuera de las transitorias se relanza de inmediato."""
    funcion = MagicMock(side_effect=ValueError("lógica rota"))

    decorada = con_reintentos(intentos=3, retraso_base=1.0)(funcion)

    with pytest.raises(ValueError):
        decorada()

    funcion.assert_called_once()


def test_intentos_menor_a_uno_lanza_error():
    """Cero o menos intentos deben ser rechazados al construir el decorador."""
    with pytest.raises(ValueError):
        con_reintentos(intentos=0)


@patch("app.utils.retry.time.sleep")
def test_backoff_aplica_retraso_exponencial(mock_sleep):
    """Con factor 2, las esperas son retraso_base, 2*retraso_base, 4*retraso_base..."""
    funcion = MagicMock(side_effect=ConnectionError("inestable"))

    decorada = con_reintentos(intentos=4, retraso_base=1.0, factor=2.0)(funcion)

    with pytest.raises(ConnectionError):
        decorada()

    esperas = [llamada.args[0] for llamada in mock_sleep.call_args_list]
    assert esperas == [1.0, 2.0, 4.0]


@patch("app.utils.retry.time.sleep")
def test_excepciones_personalizadas_controlan_el_reintento(mock_sleep):
    """El parámetro excepciones permite ampliar qué errores se reintentan."""
    funcion = MagicMock(side_effect=ValueError("API 500 temporal"))

    decorada = con_reintentos(
        intentos=2, retraso_base=0.0, excepciones=(ValueError,)
    )(funcion)

    with pytest.raises(ValueError):
        decorada()

    assert funcion.call_count == 2