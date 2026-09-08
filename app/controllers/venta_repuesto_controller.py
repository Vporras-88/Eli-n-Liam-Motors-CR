"""Controlador de Ventas de Repuestos y Accesorios."""

import sqlite3

from app.controllers.venta_controller import METODOS_PAGO
from app.models import cliente as cliente_model
from app.models import repuesto as repuesto_model
from app.models import venta_repuesto as venta_repuesto_model


def registrar_venta(
    repuesto_id: int,
    cliente_id: int,
    vendedor_id: int,
    cantidad: int,
    precio_unitario: float,
    metodo_pago: str,
    moneda: str = "CRC",
) -> sqlite3.Row:
    if metodo_pago not in METODOS_PAGO:
        raise ValueError(f"Método de pago inválido. Debe ser uno de: {', '.join(METODOS_PAGO)}.")
    if repuesto_model.obtener_por_id(repuesto_id) is None:
        raise ValueError("El repuesto indicado no existe.")
    if cliente_model.obtener_por_id(cliente_id) is None:
        raise ValueError("El cliente indicado no existe.")
    # venta_repuesto_model.registrar valida atómicamente (en la misma transacción) que haya stock suficiente.
    venta_id = venta_repuesto_model.registrar(
        repuesto_id, cliente_id, vendedor_id, cantidad, precio_unitario, metodo_pago, moneda
    )
    return venta_repuesto_model.obtener_por_id(venta_id)


def editar_venta(venta_id: int, cantidad: int, precio_unitario: float, metodo_pago: str, moneda: str = "CRC") -> sqlite3.Row:
    if metodo_pago not in METODOS_PAGO:
        raise ValueError(f"Método de pago inválido. Debe ser uno de: {', '.join(METODOS_PAGO)}.")
    if venta_repuesto_model.obtener_por_id(venta_id) is None:
        raise ValueError("La venta indicada no existe.")
    # venta_repuesto_model.actualizar valida atómicamente que haya stock suficiente para el nuevo total.
    venta_repuesto_model.actualizar(venta_id, cantidad, precio_unitario, metodo_pago, moneda)
    return venta_repuesto_model.obtener_por_id(venta_id)


def eliminar_venta(venta_id: int) -> None:
    if venta_repuesto_model.obtener_por_id(venta_id) is None:
        raise ValueError("La venta indicada no existe.")
    venta_repuesto_model.eliminar(venta_id)


def listar_ventas(desde: str | None = None, hasta: str | None = None, vendedor_id: int | None = None) -> list[sqlite3.Row]:
    return venta_repuesto_model.listar(desde=desde, hasta=hasta, vendedor_id=vendedor_id)


def total_ventas(desde: str | None = None, hasta: str | None = None) -> float:
    return venta_repuesto_model.total_por_rango(desde=desde, hasta=hasta)
