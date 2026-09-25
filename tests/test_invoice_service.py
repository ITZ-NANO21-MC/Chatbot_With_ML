# -*- coding: utf-8 -*-
"""Pruebas Unitarias para el Servicio de Facturación.

Verifica la generación de facturas PDF, el número correlativo y la
validación de datos inválidos.
"""
import os

import pytest

from app.services.invoice_service import FacturaDatos, generar_factura


def test_generar_factura_crea_pdf_valido(tmp_path):
    """Un PDF válido debe crearse y comenzar con la cabecera %PDF."""
    datos = FacturaDatos(
        cliente="Ana Perez",
        concepto="Soporte tecnico",
        monto=150.0,
        cedula_rif="V-12345678",
        fecha="2026-09-24",
    )

    ruta = generar_factura(datos, salida_dir=str(tmp_path))

    assert os.path.exists(ruta)
    with open(ruta, "rb") as f:
        contenido = f.read()
    assert contenido.startswith(b"%PDF")
    assert len(contenido) > 0


def test_generar_factura_numero_correlativo(tmp_path):
    """Cada factura generada debe incrementar el número correlativo."""
    generar_factura(FacturaDatos("Ana Perez", "Soporte", 10.0), salida_dir=str(tmp_path))
    generar_factura(FacturaDatos("Luis Gomez", "Mantenimiento", 20.5), salida_dir=str(tmp_path))

    assert (tmp_path / "factura_0001.pdf").exists()
    assert (tmp_path / "factura_0002.pdf").exists()


def test_generar_factura_persiste_contador(tmp_path):
    """El contador debe persistir entre llamadas (archivo JSON)."""
    generar_factura(FacturaDatos("Ana", "Soporte", 10.0), salida_dir=str(tmp_path))

    assert (tmp_path / "contador.json").exists()


@pytest.mark.parametrize("datos", [
    FacturaDatos(cliente="", concepto="Soporte", monto=10.0),
    FacturaDatos(cliente="Ana", concepto="   ", monto=10.0),
    FacturaDatos(cliente="Ana", concepto="Soporte", monto=0),
    FacturaDatos(cliente="Ana", concepto="Soporte", monto=-5.0),
    FacturaDatos(cliente="Ana", concepto="Soporte", monto="abc"),
])
def test_generar_factura_datos_invalidos(tmp_path, datos):
    """Datos inválidos deben lanzar ValueError sin crear el archivo."""
    with pytest.raises(ValueError):
        generar_factura(datos, salida_dir=str(tmp_path))

    assert not any(tmp_path.iterdir())