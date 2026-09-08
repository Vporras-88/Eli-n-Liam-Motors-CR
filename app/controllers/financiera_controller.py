"""Controlador de Financieras."""

import sqlite3

from app.models import financiera as financiera_model


def crear_financiera(nombre: str) -> sqlite3.Row:
    nombre = nombre.strip()
    if not nombre:
        raise ValueError("El nombre de la financiera no puede estar vacío.")
    if financiera_model.obtener_por_nombre(nombre) is not None:
        raise ValueError(f"Ya existe una financiera registrada con el nombre '{nombre}'.")
    financiera_id = financiera_model.crear(nombre)
    return financiera_model.obtener_por_id(financiera_id)


def listar_financieras() -> list[sqlite3.Row]:
    return financiera_model.listar()


def eliminar_financiera(financiera_id: int) -> None:
    if financiera_model.obtener_por_id(financiera_id) is None:
        raise ValueError("La financiera indicada no existe.")
    financiera_model.eliminar(financiera_id)
