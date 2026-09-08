"""Controlador de Vendedores (catálogo de nombres asignable a un cliente)."""

import sqlite3

from app.models import vendedor as vendedor_model


def crear_vendedor(nombre: str) -> sqlite3.Row:
    nombre = nombre.strip()
    if not nombre:
        raise ValueError("El nombre del vendedor no puede estar vacío.")
    if vendedor_model.obtener_por_nombre(nombre) is not None:
        raise ValueError(f"Ya existe un vendedor registrado con el nombre '{nombre}'.")
    vendedor_id = vendedor_model.crear(nombre)
    return vendedor_model.obtener_por_id(vendedor_id)


def listar_vendedores() -> list[sqlite3.Row]:
    return vendedor_model.listar()


def eliminar_vendedor(vendedor_id: int) -> None:
    if vendedor_model.obtener_por_id(vendedor_id) is None:
        raise ValueError("El vendedor indicado no existe.")
    vendedor_model.eliminar(vendedor_id)
