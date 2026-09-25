# -*- coding: utf-8 -*-
"""Servicio de Facturación (Fase 6).

Genera facturas en PDF usando reportlab a partir de datos simples
(cliente, concepto, monto). El número de factura es correlativo y se
persiste en un contador JSON dentro del directorio de salida.
"""
import json
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from app import config
from app.utils.logger import get_logger

logger = get_logger(__name__)

CONTADOR_FILENAME = "contador.json"


@dataclass
class FacturaDatos:
    """Datos necesarios para generar una factura.

    Attributes:
        cliente (str): Nombre del cliente. Obligatorio.
        concepto (str): Descripción del servicio/producto. Obligatorio.
        monto (float): Importe total de la factura. Debe ser mayor que 0.
        cedula_rif (str): Identificación fiscal del cliente (opcional).
        fecha (Optional[str]): Fecha en formato ISO (YYYY-MM-DD). Por defecto, hoy.
    """
    cliente: str
    concepto: str
    monto: float
    cedula_rif: str = ""
    fecha: Optional[str] = None


def _validar_datos(datos: FacturaDatos) -> None:
    """Valida los datos de la factura.

    Args:
        datos (FacturaDatos): Datos a validar.

    Raises:
        ValueError: Si algún dato obligatorio falta o el monto no es un
            número mayor que cero.
    """
    if not datos.cliente or not datos.cliente.strip():
        raise ValueError("El nombre del cliente no puede estar vacío.")
    if not datos.concepto or not datos.concepto.strip():
        raise ValueError("El concepto no puede estar vacío.")
    try:
        monto = float(datos.monto)
    except (TypeError, ValueError):
        raise ValueError(f"Monto inválido: {datos.monto!r}") from None
    if monto <= 0:
        raise ValueError("El monto debe ser un número mayor que cero.")


def _siguiente_numero(contador_path: str) -> int:
    """Obtiene e incrementa el número de factura correlativo.

    El contador se persiste en un archivo JSON dentro del directorio de
    salida, lo que permite mantener la secuencia entre reinicios.

    Args:
        contador_path (str): Ruta al archivo del contador.

    Returns:
        int: El siguiente número de factura disponible.
    """
    numero = 0
    try:
        with open(contador_path, "r", encoding="utf-8") as f:
            numero = int(json.load(f).get("ultima_factura", 0))
    except (FileNotFoundError, json.JSONDecodeError, ValueError):
        numero = 0

    numero += 1
    os.makedirs(os.path.dirname(contador_path), exist_ok=True)
    with open(contador_path, "w", encoding="utf-8") as f:
        json.dump({"ultima_factura": numero}, f, ensure_ascii=False)
    return numero


def _formatear_monto(monto: float) -> str:
    """Formatea un monto como moneda (ej. $1,234.50).

    Args:
        monto (float): Monto a formatear.

    Returns:
        str: El monto formateado.
    """
    return f"${monto:,.2f}"


def _fecha_legible(fecha: Optional[str]) -> str:
    """Convierte una fecha ISO a formato legible (DD/MM/AAAA).

    Args:
        fecha (Optional[str]): Fecha ISO (YYYY-MM-DD).

    Returns:
        str: Fecha legible, o la fecha actual si no se especifica.
    """
    if fecha:
        return datetime.strptime(fecha, "%Y-%m-%d").strftime("%d/%m/%Y")
    return datetime.now().strftime("%d/%m/%Y")


def generar_factura(datos: FacturaDatos, salida_dir: Optional[str] = None) -> str:
    """Genera un archivo PDF de factura y devuelve su ruta.

    Args:
        datos (FacturaDatos): Datos del cliente, concepto y monto.
        salida_dir (Optional[str]): Directorio de salida. Por defecto usa
            `config.FACTURAS_PATH`.

    Returns:
        str: Ruta absoluta al archivo PDF generado.

    Raises:
        ValueError: Si los datos no son válidos.
        OSError: Si no se puede escribir el archivo PDF.
    """
    _validar_datos(datos)

    salida_dir = salida_dir or config.FACTURAS_PATH
    os.makedirs(salida_dir, exist_ok=True)

    contador_path = os.path.join(salida_dir, CONTADOR_FILENAME)
    numero = _siguiente_numero(contador_path)

    fecha_legible = _fecha_legible(datos.fecha)
    monto = float(datos.monto)
    ruta_pdf = os.path.join(salida_dir, f"factura_{numero:04d}.pdf")

    ancho, alto = LETTER
    margen = 20 * mm

    c = canvas.Canvas(ruta_pdf, pagesize=LETTER)

    # Encabezado
    c.setFont("Helvetica-Bold", 16)
    c.drawString(margen, alto - 25 * mm, config.NEGOCIO_NOMBRE)
    c.setFont("Helvetica-Bold", 12)
    c.drawRightString(ancho - margen, alto - 25 * mm, f"FACTURA N. {numero:04d}")

    c.line(margen, alto - 30 * mm, ancho - margen, alto - 30 * mm)

    # Fecha
    c.setFont("Helvetica", 11)
    c.drawString(margen, alto - 40 * mm, f"Fecha: {fecha_legible}")

    # Datos del cliente
    c.setFont("Helvetica-Bold", 11)
    c.drawString(margen, alto - 58 * mm, "Datos del cliente")
    c.setFont("Helvetica", 11)
    c.drawString(margen, alto - 68 * mm, f"Cliente: {datos.cliente}")
    c.drawString(margen, alto - 76 * mm, f"Cedula/RIF: {datos.cedula_rif or 'N/A'}")

    # Detalle
    c.setFont("Helvetica-Bold", 11)
    c.drawString(margen, alto - 96 * mm, "Detalle")
    c.setFont("Helvetica", 11)
    c.drawString(margen, alto - 106 * mm, f"Concepto: {datos.concepto}")

    # Total
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margen, alto - 136 * mm, f"Total: {_formatear_monto(monto)}")

    c.showPage()
    c.save()

    logger.info(f"Factura {numero:04d} generada en {ruta_pdf}")
    return ruta_pdf