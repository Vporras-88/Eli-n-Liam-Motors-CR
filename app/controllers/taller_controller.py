"""Controlador de Taller Mecánico (órdenes de trabajo)."""

import sqlite3

from app.models import cliente as cliente_model
from app.models import orden_trabajo as orden_model
from app.models import usuario as usuario_model
from app.models.orden_trabajo import ESTADOS

TRANSICIONES_VALIDAS = {
    "pendiente": {"en_proceso"},
    "en_proceso": {"completada"},
    "completada": {"entregada"},
    "entregada": set(),
}


def crear_orden(
    cliente_id: int,
    moto_marca: str,
    moto_modelo: str,
    moto_placa: str,
    mecanico_id: int | None,
    descripcion_problema: str,
    costo_mano_obra: float,
) -> sqlite3.Row:
    if cliente_model.obtener_por_id(cliente_id) is None:
        raise ValueError("El cliente indicado no existe.")
    if mecanico_id is not None:
        mecanico = usuario_model.obtener_por_id(mecanico_id)
        if mecanico is None or mecanico["rol"] != "mecanico":
            raise ValueError("El mecánico indicado no existe o no tiene el rol adecuado.")
    orden_id = orden_model.crear(
        cliente_id, moto_marca.strip(), moto_modelo.strip(), moto_placa.strip(),
        mecanico_id, descripcion_problema.strip(), costo_mano_obra,
    )
    return orden_model.obtener_por_id(orden_id)


def cambiar_estado_orden(orden_id: int, nuevo_estado: str) -> sqlite3.Row:
    orden = orden_model.obtener_por_id(orden_id)
    if orden is None:
        raise ValueError("La orden indicada no existe.")
    if nuevo_estado not in ESTADOS:
        raise ValueError(f"Estado inválido. Debe ser uno de: {', '.join(ESTADOS)}.")
    if nuevo_estado not in TRANSICIONES_VALIDAS[orden["estado"]]:
        raise ValueError(f"No se puede pasar de '{orden['estado']}' a '{nuevo_estado}'.")
    orden_model.cambiar_estado(orden_id, nuevo_estado)
    return orden_model.obtener_por_id(orden_id)


def agregar_repuesto_a_orden(orden_id: int, repuesto_id: int, cantidad: int) -> None:
    if orden_model.obtener_por_id(orden_id) is None:
        raise ValueError("La orden indicada no existe.")
    orden_model.agregar_repuesto(orden_id, repuesto_id, cantidad)


def obtener_detalle_orden(orden_id: int) -> dict:
    orden = orden_model.obtener_por_id(orden_id)
    if orden is None:
        raise ValueError("La orden indicada no existe.")
    repuestos = orden_model.listar_repuestos_de_orden(orden_id)
    return {
        "orden": orden,
        "repuestos": repuestos,
        "costo_total": orden_model.costo_total(orden_id),
    }


def listar_ordenes(estado: str | None = None) -> list[sqlite3.Row]:
    return orden_model.listar(estado=estado)
