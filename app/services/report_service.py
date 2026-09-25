# -*- coding: utf-8 -*-
"""Servicio de Reportes (Fase 7).

Envía el log de operaciones por email al dueño usando SMTP de la
biblioteca estándar (`smtplib`), sin dependencias externas.
"""
import os
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from typing import Optional

from app import config
from app.utils.logger import get_logger

logger = get_logger(__name__)

REPORTE_TITULO = "Reporte del chatbot"


def _configuracion_completa() -> bool:
    """Verifica que las credenciales SMTP y del destinatario estén presentes.

    Returns:
        bool: True si la configuración es suficiente para enviar correos.
    """
    return bool(
        config.OWNER_EMAIL
        and config.SMTP_HOST
        and config.SMTP_USER
        and config.SMTP_PASSWORD
    )


def _adjuntar_archivo(mensaje: MIMEMultipart, ruta: str) -> None:
    """Adjunta un archivo al mensaje multiparte.

    Args:
        mensaje (MIMEMultipart): Mensaje al que adjuntar.
        ruta (str): Ruta del archivo a leer.

    Raises:
        OSError: Si el archivo no puede leerse.
    """
    with open(ruta, "rb") as archivo:
        adjunto = MIMEApplication(archivo.read(), _subtype="octet-stream")
    adjunto.add_header(
        "Content-Disposition", "attachment", filename=os.path.basename(ruta)
    )
    mensaje.attach(adjunto)


def _seleccionar_log() -> str:
    """Elige qué archivo de log adjuntar.

    Prefiere el log actual si no está vacío; de lo contrario usa el
    respaldo rotativo más reciente que contenga datos.

    Returns:
        str: Ruta del archivo de log seleccionado.
    """
    ruta_actual = config.LOG_FILE_PATH
    for ruta in [ruta_actual] + [
        f"{ruta_actual}.{i}" for i in range(1, config.LOG_BACKUP_COUNT + 1)
    ]:
        if os.path.exists(ruta) and os.path.getsize(ruta) > 0:
            return ruta
    return ruta_actual


def _conectar_smtp() -> smtplib.SMTP:
    """Abre y autentica una conexión SMTP según la configuración.

    Returns:
        smtplib.SMTP: Cliente SMTP autenticado.

    Raises:
        smtplib.SMTPException: Si la conexión o autenticación falla.
    """
    if config.SMTP_SSL:
        cliente = smtplib.SMTP_SSL(config.SMTP_HOST, config.SMTP_PORT, timeout=30)
    else:
        cliente = smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT, timeout=30)
        cliente.ehlo()
        cliente.starttls()
        cliente.ehlo()
    cliente.login(config.SMTP_USER, config.SMTP_PASSWORD)
    return cliente


def enviar_reporte_email(
    destinatario: Optional[str] = None,
    asunto: Optional[str] = None,
    ruta_adjunto: Optional[str] = None,
) -> None:
    """Envía un reporte por email al dueño, adjuntando el log de operaciones.

    Args:
        destinatario (Optional[str]): Dirección destino (por defecto `OWNER_EMAIL`).
        asunto (Optional[str]): Asunto personalizado.
        ruta_adjunto (Optional[str]): Archivo a adjuntar (por defecto el log actual).

    Raises:
        ValueError: Si la configuración SMTP es incompleta.
        OSError: Si no se puede adjuntar o escribir el correo.
        smtplib.SMTPException: Si el envío falla.
    """
    if not _configuracion_completa():
        raise ValueError(
            "Configuración SMTP incompleta: revisa OWNER_EMAIL y las variables SMTP_*."
        )

    to = destinatario or config.OWNER_EMAIL
    ruta = ruta_adjunto or _seleccionar_log()

    mensaje = MIMEMultipart()
    mensaje["From"] = config.SMTP_FROM or config.SMTP_USER
    mensaje["To"] = to
    mensaje["Date"] = formatdate(localtime=True)
    mensaje["Subject"] = asunto or REPORTE_TITULO

    cuerpo = (
        "Hola,\n\n"
        "Se adjunta el log de operaciones del chatbot.\n\n"
        "— Bot de asistencia"
    )
    mensaje.attach(MIMEText(cuerpo, "plain", "utf-8"))

    if ruta and os.path.exists(ruta):
        _adjuntar_archivo(mensaje, ruta)
    else:
        logger.warning(f"Archivo de log no encontrado para adjuntar: {ruta}")

    cliente = None
    try:
        cliente = _conectar_smtp()
        cliente.send_message(mensaje)
        logger.info(f"Reporte enviado a {to} (adjunto: {ruta}).")
    finally:
        if cliente is not None:
            try:
                cliente.quit()
            except smtplib.SMTPException:
                logger.warning("No se pudo cerrar la conexión SMTP correctamente.")