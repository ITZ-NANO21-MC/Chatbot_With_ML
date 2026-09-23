# -*- coding: utf-8 -*-
"""Pruebas Unitarias para el Servicio de Inventario.

Este módulo verifica la búsqueda de productos en ambas fuentes
(SQLite y CSV), incluyendo consultas parciales y sin coincidencia.
"""
import sqlite3

import pytest

from app import config
from app.services import inventory_service


@pytest.fixture
def csv_tmp(tmp_path):
    """Crea un archivo CSV de inventario temporal."""
    path = tmp_path / "inventory.csv"
    path.write_text(
        "nombre,precio,stock\n"
        "Cargador Tipo C Rapido,25.00,20\n"
        "Pantalla iPhone 12,120.50,5\n",
        encoding="utf-8"
    )
    return path


@pytest.fixture
def sqlite_tmp(tmp_path):
    """Crea una base de datos SQLite de inventario temporal."""
    path = tmp_path / "inventory.db"
    conn = sqlite3.connect(path)
    conn.execute(
        "CREATE TABLE productos (nombre TEXT, precio REAL, stock INTEGER)"
    )
    conn.execute(
        "INSERT INTO productos VALUES ('Bateria Samsung S21', 45.0, 12)"
    )
    conn.commit()
    conn.close()
    return path


def test_buscar_csv_consulta_parcial(monkeypatch, csv_tmp):
    """Consulta parcial debe encontrar el producto en CSV."""
    monkeypatch.setattr(config, "INVENTORY_SOURCE_TYPE", "csv")
    monkeypatch.setattr(config, "INVENTORY_CSV_PATH", str(csv_tmp))

    resultado = inventory_service.buscar_producto("cargador tipo c")

    assert resultado == {
        "nombre": "Cargador Tipo C Rapido",
        "precio": 25.0,
        "stock": 20,
    }


def test_buscar_csv_consulta_completa(monkeypatch, csv_tmp):
    """Consulta exacta debe encontrar el producto en CSV."""
    monkeypatch.setattr(config, "INVENTORY_SOURCE_TYPE", "csv")
    monkeypatch.setattr(config, "INVENTORY_CSV_PATH", str(csv_tmp))

    resultado = inventory_service.buscar_producto("Pantalla iPhone 12")

    assert resultado == {
        "nombre": "Pantalla iPhone 12",
        "precio": 120.5,
        "stock": 5,
    }


def test_buscar_csv_sin_coincidencia(monkeypatch, csv_tmp):
    """Consulta no relacionada debe devolver None."""
    monkeypatch.setattr(config, "INVENTORY_SOURCE_TYPE", "csv")
    monkeypatch.setattr(config, "INVENTORY_CSV_PATH", str(csv_tmp))

    assert inventory_service.buscar_producto("zzz inexistente") is None


def test_buscar_sqlite_consulta_parcial(monkeypatch, sqlite_tmp):
    """Consulta parcial debe encontrar el producto en SQLite."""
    monkeypatch.setattr(config, "INVENTORY_SOURCE_TYPE", "sqlite")
    monkeypatch.setattr(config, "INVENTORY_SQLITE_PATH", str(sqlite_tmp))

    resultado = inventory_service.buscar_producto("bateria samsung")

    assert resultado is not None
    assert resultado["nombre"] == "Bateria Samsung S21"
    assert resultado["precio"] == 45.0
    assert resultado["stock"] == 12


def test_buscar_sqlite_sin_coincidencia(monkeypatch, sqlite_tmp):
    """Consulta no relacionada debe devolver None en SQLite."""
    monkeypatch.setattr(config, "INVENTORY_SOURCE_TYPE", "sqlite")
    monkeypatch.setattr(config, "INVENTORY_SQLITE_PATH", str(sqlite_tmp))

    assert inventory_service.buscar_producto("zzz inexistente") is None