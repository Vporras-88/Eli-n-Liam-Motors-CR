"""Controlador de Ventas."""

import sqlite3

from app.models import cliente as cliente_model
from app.models import motocicleta as moto_model
from app.models import venta as venta_model

METODOS_PAGO = ("contado", "tarjeta", "financiamiento")


def registrar_venta(
    moto_id: int, cliente_id: int, vendedor_id: int, precio_final: float, metodo_pago: str, moneda: str = "CRC"
) -> sqlite3.Row:
    if metodo_pago not in METODOS_PAGO:
        raise ValueError(f"Método de pago inválido. Debe ser uno de: {', '.join(METODOS_PAGO)}.")
    if moto_model.obtener_por_id(moto_id) is None:
        raise ValueError("La motocicleta indicada no existe.")
    if cliente_model.obtener_por_id(cliente_id) is None:
        raise ValueError("El cliente indicado no existe.")
    # venta_model.registrar valida atómicamente (en la misma transacción) que la moto siga disponible.
    venta_id = venta_model.registrar(moto_id, cliente_id, vendedor_id, precio_final, metodo_pago, moneda)
    return venta_model.obtener_por_id(venta_id)


def editar_venta(venta_id: int, precio_final: float, metodo_pago: str, moneda: str = "CRC") -> sqlite3.Row:
    if metodo_pago not in METODOS_PAGO:
        raise ValueError(f"Método de pago inválido. Debe ser uno de: {', '.join(METODOS_PAGO)}.")
    if venta_model.obtener_por_id(venta_id) is None:
        raise ValueError("La venta indicada no existe.")
    venta_model.actualizar(venta_id, precio_final, metodo_pago, moneda)
    return venta_model.obtener_por_id(venta_id)


def eliminar_venta(venta_id: int) -> None:
    if venta_model.obtener_por_id(venta_id) is None:
        raise ValueError("La venta indicada no existe.")
    venta_model.eliminar(venta_id)


def listar_ventas(desde: str | None = None, hasta: str | None = None, vendedor_id: int | None = None) -> list[sqlite3.Row]:
    return venta_model.listar(desde=desde, hasta=hasta, vendedor_id=vendedor_id)


def total_ventas(desde: str | None = None, hasta: str | None = None) -> float:
    return venta_model.total_por_rango(desde=desde, hasta=hasta)
