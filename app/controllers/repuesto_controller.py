"""Controlador de Repuestos y Accesorios."""

import sqlite3

from app.models import repuesto as repuesto_model
from app.models.repuesto import CATEGORIAS, STOCK_BAJO_UMBRAL


def crear_repuesto(nombre: str, categoria: str, marca_compatible: str, precio: float, stock: int, proveedor: str) -> sqlite3.Row:
    if categoria not in CATEGORIAS:
        raise ValueError(f"Categoría inválida. Debe ser una de: {', '.join(CATEGORIAS)}.")
    repuesto_id = repuesto_model.crear(nombre.strip(), categoria, marca_compatible.strip(), precio, stock, proveedor.strip())
    return repuesto_model.obtener_por_id(repuesto_id)


def editar_repuesto(repuesto_id: int, nombre: str, marca_compatible: str, precio: float, proveedor: str) -> sqlite3.Row:
    if repuesto_model.obtener_por_id(repuesto_id) is None:
        raise ValueError("El repuesto indicado no existe.")
    repuesto_model.actualizar(repuesto_id, nombre.strip(), marca_compatible.strip(), precio, proveedor.strip())
    return repuesto_model.obtener_por_id(repuesto_id)


def registrar_entrada_stock(repuesto_id: int, cantidad: int) -> sqlite3.Row:
    if repuesto_model.obtener_por_id(repuesto_id) is None:
        raise ValueError("El repuesto indicado no existe.")
    repuesto_model.ajustar_stock(repuesto_id, cantidad)
    return repuesto_model.obtener_por_id(repuesto_id)


def registrar_salida_stock(repuesto_id: int, cantidad: int) -> sqlite3.Row:
    if repuesto_model.obtener_por_id(repuesto_id) is None:
        raise ValueError("El repuesto indicado no existe.")
    repuesto_model.ajustar_stock(repuesto_id, -cantidad)
    return repuesto_model.obtener_por_id(repuesto_id)


def eliminar_repuesto(repuesto_id: int) -> None:
    if repuesto_model.obtener_por_id(repuesto_id) is None:
        raise ValueError("El repuesto indicado no existe.")
    repuesto_model.eliminar(repuesto_id)


def listar_repuestos() -> list[sqlite3.Row]:
    return repuesto_model.listar()


def listar_stock_bajo() -> list[sqlite3.Row]:
    return repuesto_model.listar_stock_bajo(STOCK_BAJO_UMBRAL)
