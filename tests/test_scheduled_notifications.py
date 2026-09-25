# -*- coding: utf-8 -*-
"""Tests del servicio de notificaciones programadas (Fase 6, módulo 6.3)."""
import json
import textwrap
from unittest.mock import MagicMock, patch

import pytest

from app.services import scheduled_notifications


@pytest.fixture()
def registro_clientes(tmp_path):
    """Crea un archivo JSON de clientes temporal y devuelve su ruta."""
    ruta = tmp_path / "clientes.json"
    ruta.write_text(
        json.dumps(
            [
                {"chat_id": "589100000001@c.us", "nombre": "Ana"},
                {"chat_id": "589100000002@c.us", "nombre": "Luis"},
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return str(ruta)


@pytest.fixture()
def bot():
    """Bot de Green-API simulado con la cadena api.sending.sendMessage."""
    return MagicMock()


def test_enviar_recordatorios_envia_a_todos(bot, registro_clientes):
    """Debe enviar el recordatorio a cada cliente registrado."""
    enviados = scheduled_notifications.enviar_recordatorios_diarios(
        bot, registro_path=registro_clientes
    )

    assert enviados == 2
    assert bot.api.sending.sendMessage.call_count == 2
    bot.api.sending.sendMessage.assert_any_call(
        "589100000001@c.us", scheduled_notifications.RECORDATORIO_MENSAJE
    )
    bot.api.sending.sendMessage.assert_any_call(
        "589100000002@c.us", scheduled_notifications.RECORDATORIO_MENSAJE
    )


def test_enviar_recordatorios_registro_vacio(bot, tmp_path):
    """Con una lista vacía no debe enviar ningún mensaje."""
    ruta = tmp_path / "clientes.json"
    ruta.write_text("[]", encoding="utf-8")

    enviados = scheduled_notifications.enviar_recordatorios_diarios(
        bot, registro_path=str(ruta)
    )

    assert enviados == 0
    bot.api.sending.sendMessage.assert_not_called()


def test_enviar_recordatorios_archivo_inexistente(bot):
    """Si el archivo no existe no debe fallar y envía cero mensajes."""
    enviados = scheduled_notifications.enviar_recordatorios_diarios(
        bot, registro_path="/ruta/inexistente/clientes.json"
    )

    assert enviados == 0
    bot.api.sending.sendMessage.assert_not_called()


def test_enviar_recordatorios_ignora_entradas_sin_chat_id(bot, tmp_path):
    """Las entradas sin chat_id deben descartarse."""
    ruta = tmp_path / "clientes.json"
    ruta.write_text(
        json.dumps(
            [
                {"chat_id": "589100000001@c.us"},
                {"nombre": "Sin chat"},
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    enviados = scheduled_notifications.enviar_recordatorios_diarios(
        bot, registro_path=str(ruta)
    )

    assert enviados == 1
    bot.api.sending.sendMessage.assert_called_once()


def test_cargar_clientes_archivo_corrupto(bot, tmp_path):
    """Un JSON inválido debe devolver lista vacía sin lanzar excepción."""
    ruta = tmp_path / "clientes.json"
    ruta.write_text("{esto no es json", encoding="utf-8")

    enviados = scheduled_notifications.enviar_recordatorios_diarios(
        bot, registro_path=str(ruta)
    )

    assert enviados == 0
    bot.api.sending.sendMessage.assert_not_called()


def test_enviar_recordatorios_marca_error_en_envio_fallido(bot, registro_clientes):
    """Un error en el envío de un cliente no debe interrumpir a los demás."""
    bot.api.sending.sendMessage.side_effect = [
        Exception("Fallo de red"),
        None,
    ]

    enviados = scheduled_notifications.enviar_recordatorios_diarios(
        bot, registro_path=registro_clientes
    )

    assert enviados == 1
    assert bot.api.sending.sendMessage.call_count == 2


def test_cargar_clientes_no_lista_devuelve_vacio(tmp_path):
    """Un registro que no sea una lista debe devolver lista vacía."""
    ruta = tmp_path / "clientes.json"
    ruta.write_text(textwrap.dedent('''
        {"chat_id": "589100000001@c.us"}
    '''), encoding="utf-8")

    assert scheduled_notifications._cargar_clientes(str(ruta)) == []


def test_cargar_clientes_usa_config_por_defecto(bot, registro_clientes):
    """Sin ruta, debe usar config.CLIENTES_PATH."""
    with patch.object(scheduled_notifications.config, "CLIENTES_PATH", registro_clientes):
        enviados = scheduled_notifications.enviar_recordatorios_diarios(bot)

    assert enviados == 2
    bot.api.sending.sendMessage.assert_called()