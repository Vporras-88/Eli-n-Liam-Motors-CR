"""Controlador de Inventario de Motocicletas."""

import sqlite3

from app.models import motocicleta as moto_model


def crear_moto(marca: str, modelo: str, anio: int, color: str, cilindraje: int, vin: str, precio: float) -> sqlite3.Row:
    if moto_model.obtener_por_vin(vin.strip()) is not None:
        raise ValueError(f"Ya existe una motocicleta registrada con el VIN {vin}.")
    moto_id = moto_model.crear(marca.strip(), modelo.strip(), anio, color.strip(), cilindraje, vin.strip(), precio)
    return moto_model.obtener_por_id(moto_id)


def editar_moto(moto_id: int, marca: str, modelo: str, anio: int, color: str, cilindraje: int, precio: float) -> sqlite3.Row:
    if moto_model.obtener_por_id(moto_id) is None:
        raise ValueError("La motocicleta indicada no existe.")
    moto_model.actualizar(moto_id, marca.strip(), modelo.strip(), anio, color.strip(), cilindraje, precio)
    return moto_model.obtener_por_id(moto_id)


def cambiar_estado_moto(moto_id: int, estado: str) -> sqlite3.Row:
    if estado not in moto_model.ESTADOS:
        raise ValueError(f"Estado inválido. Debe ser uno de: {', '.join(moto_model.ESTADOS)}.")
    if moto_model.obtener_por_id(moto_id) is None:
        raise ValueError("La motocicleta indicada no existe.")
    moto_model.cambiar_estado(moto_id, estado)
    return moto_model.obtener_por_id(moto_id)


def eliminar_moto(moto_id: int) -> None:
    if moto_model.obtener_por_id(moto_id) is None:
        raise ValueError("La motocicleta indicada no existe.")
    moto_model.eliminar(moto_id)


def listar_motos(estado: str | None = None) -> list[sqlite3.Row]:
    return moto_model.listar(estado)


def buscar_motos(texto: str) -> list[sqlite3.Row]:
    return moto_model.buscar(texto.strip())


def listar_disponibles() -> list[sqlite3.Row]:
    return moto_model.listar(estado="disponible")
