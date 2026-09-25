# -*- coding: utf-8 -*-
"""Tests del servicio de reportes por email (Fase 7, módulo 7.3)."""
from unittest.mock import MagicMock, patch

import pytest

from app.services import report_service


@pytest.fixture()
def config_smtp_completa():
    """Configura las credenciales SMTP y del dueño para la prueba."""
    with patch.object(report_service.config, "OWNER_EMAIL", "dueno@correo.com"), (
        patch.object(report_service.config, "SMTP_HOST", "smtp.ejemplo.com")
    ), patch.object(report_service.config, "SMTP_PORT", 587), (
        patch.object(report_service.config, "SMTP_USER", "bot@correo.com")
    ), patch.object(report_service.config, "SMTP_PASSWORD", "secreto"), (
        patch.object(report_service.config, "SMTP_FROM", "bot@correo.com")
    ), patch.object(report_service.config, "SMTP_SSL", False):
        yield


def test_sin_configuracion_lanza_valueerror():
    """Sin credenciales SMTP, enviar_reporte_email debe lanzar ValueError."""
    with (
        patch.object(report_service.config, "OWNER_EMAIL", ""),
        patch.object(report_service.config, "SMTP_HOST", ""),
    ):
        with pytest.raises(ValueError):
            report_service.enviar_reporte_email()


@patch("app.services.report_service.smtplib.SMTP")
def test_envia_email_con_adjunto_del_log(mock_smtp, config_smtp_completa, tmp_path):
    """Se envía el correo con el log adjunto y se cierra la conexión."""
    archivo_log = tmp_path / "chatbot_operations.log"
    archivo_log.write_text("línea de log de prueba\n", encoding="utf-8")

    with patch.object(report_service.config, "LOG_FILE_PATH", str(archivo_log)):
        report_service.enviar_reporte_email()

    mock_smtp.assert_called_once_with("smtp.ejemplo.com", 587, timeout=30)
    instancia = mock_smtp.return_value
    instancia.starttls.assert_called_once()
    instancia.login.assert_called_once_with("bot@correo.com", "secreto")
    instancia.send_message.assert_called_once()
    instancia.quit.assert_called_once()

    mensaje_enviado = instancia.send_message.call_args.args[0]
    assert mensaje_enviado["To"] == "dueno@correo.com"
    assert mensaje_enviado["From"] == "bot@correo.com"
    assert "chatbot_operations.log" in mensaje_enviado.get_payload()[1].get(
        "Content-Disposition"
    )


@patch("app.services.report_service.smtplib.SMTP_SSL")
def test_smtp_ssl_usa_conexion_segura(mock_smtp_ssl, config_smtp_completa):
    """Con SMTP_SSL habilitado se usa SMTP_SSL en lugar de SMTP + STARTTLS."""
    with patch.object(report_service.config, "SMTP_SSL", True):
        report_service.enviar_reporte_email()

    mock_smtp_ssl.assert_called_once_with("smtp.ejemplo.com", 587, timeout=30)
    mock_smtp_ssl.return_value.starttls.assert_not_called()
    mock_smtp_ssl.return_value.quit.assert_called_once()


@patch("app.services.report_service.smtplib.SMTP")
def test_envia_email_incluye_destinatario_y_asunto_personalizados(
    mock_smtp, config_smtp_completa, tmp_path
):
    """Se respetan destinatario y asunto personalizados."""
    archivo_log = tmp_path / "log.txt"
    archivo_log.write_text("x\n", encoding="utf-8")

    with patch.object(report_service.config, "LOG_FILE_PATH", str(archivo_log)):
        report_service.enviar_reporte_email(
            destinatario="jefe@correo.com", asunto="Reporte diario"
        )

    mensaje_enviado = mock_smtp.return_value.send_message.call_args.args[0]
    assert mensaje_enviado["To"] == "jefe@correo.com"
    assert mensaje_enviado["Subject"] == "Reporte diario"


def test_seleccionar_log_prefiere_el_actual(tmp_path):
    """El log actual no vacío debe preferirse sobre los respaldos."""
    actual = tmp_path / "chatbot_operations.log"
    actual.write_text("contenido actual\n", encoding="utf-8")
    respaldo = tmp_path / "chatbot_operations.log.1"
    respaldo.write_text("contenido viejo\n", encoding="utf-8")

    with patch.object(report_service.config, "LOG_FILE_PATH", str(actual)), (
        patch.object(report_service.config, "LOG_BACKUP_COUNT", 1)
    ):
        assert report_service._seleccionar_log() == str(actual)


def test_seleccionar_log_usa_respaldo_si_el_actual_esta_vacio(tmp_path):
    """Con el log actual vacío, debe tomarse el respaldo más reciente."""
    actual = tmp_path / "chatbot_operations.log"
    actual.write_text("", encoding="utf-8")
    respaldo = tmp_path / "chatbot_operations.log.1"
    respaldo.write_text("contenido viejo\n", encoding="utf-8")

    with patch.object(report_service.config, "LOG_FILE_PATH", str(actual)), (
        patch.object(report_service.config, "LOG_BACKUP_COUNT", 1)
    ):
        assert report_service._seleccionar_log() == str(respaldo)