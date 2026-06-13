# -*- coding: utf-8 -*-
"""Módulo de Servicio de Inventario.

Abstrae la conexión al inventario físico del negocio, soportando
múltiples fuentes de datos (SQLite local o archivo CSV).
"""
import sqlite3
import csv
from typing import Optional, Dict, Any
from rapidfuzz import process, fuzz

from app import config
from app.utils.logger import get_logger

logger = get_logger(__name__)


def buscar_producto(nombre_producto: str) -> Optional[Dict[str, Any]]:
    """Busca un producto en la fuente de inventario configurada.

    Args:
        nombre_producto (str): El nombre del producto a buscar.

    Returns:
        dict: Un diccionario con 'nombre', 'precio' y 'stock' si se encuentra.
        None: Si no se encuentra ningún producto similar.
    """
    if config.INVENTORY_SOURCE_TYPE.lower() == "sqlite":
        return _buscar_en_sqlite(nombre_producto)
    elif config.INVENTORY_SOURCE_TYPE.lower() == "csv":
        return _buscar_en_csv(nombre_producto)
    else:
        logger.error(
            f"Tipo de fuente de inventario desconocido: {config.INVENTORY_SOURCE_TYPE}"
        )
        return None


def _buscar_en_sqlite(nombre_producto: str) -> Optional[Dict[str, Any]]:
    """Busca en la base de datos SQLite."""
    try:
        # Conectar a la base de datos local
        conn = sqlite3.connect(config.INVENTORY_SQLITE_PATH)
        cursor = conn.cursor()

        # Primero, obtener todos los nombres de productos para hacer búsqueda difusa
        # (Para DBs pequeñas/medianas esto está bien. Para DBs enormes se usaría LIKE o FTS)
        cursor.execute("SELECT nombre, precio, stock FROM productos")
        resultados = cursor.fetchall()
        conn.close()

        if not resultados:
            return None

        # Convertir a lista de nombres
        nombres = [row[0] for row in resultados]

        # Búsqueda difusa para tolerar errores ortográficos
        mejor_coincidencia = process.extractOne(
            query=nombre_producto,
            choices=nombres,
            scorer=fuzz.WRatio,
            score_cutoff=config.FUZZY_SCORE_THRESHOLD
        )

        if mejor_coincidencia:
            nombre_encontrado = mejor_coincidencia[0]
            # Buscar el row original
            for row in resultados:
                if row[0] == nombre_encontrado:
                    return {
                        "nombre": row[0],
                        "precio": float(row[1]),
                        "stock": int(row[2])
                    }
        return None

    except sqlite3.Error as e:
        logger.error(f"Error al buscar en SQLite: {e}")
        return None
    except Exception as e:
        logger.error(f"Error inesperado en SQLite: {e}")
        return None


def _buscar_en_csv(nombre_producto: str) -> Optional[Dict[str, Any]]:
    """Busca en el archivo CSV local."""
    try:
        productos = []
        with open(config.INVENTORY_CSV_PATH, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                productos.append(row)

        if not productos:
            return None

        nombres = [p.get('nombre', '') for p in productos]

        mejor_coincidencia = process.extractOne(
            query=nombre_producto,
            choices=nombres,
            scorer=fuzz.WRatio,
            score_cutoff=config.FUZZY_SCORE_THRESHOLD
        )

        if mejor_coincidencia:
            nombre_encontrado = mejor_coincidencia[0]
            for p in productos:
                if p.get('nombre') == nombre_encontrado:
                    return {
                        "nombre": p.get('nombre'),
                        "precio": float(p.get('precio', 0)),
                        "stock": int(p.get('stock', 0))
                    }
        return None

    except FileNotFoundError:
        logger.error(f"Archivo CSV no encontrado en: {config.INVENTORY_CSV_PATH}")
        return None
    except Exception as e:
        logger.error(f"Error al leer CSV: {e}")
        return None
