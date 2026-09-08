"""Controlador de Clientes."""

import sqlite3

from app.models import cliente as cliente_model

ESTADOS_FINANCIAMIENTO = ("aprobado", "rechazado", "pendiente")

# Marca "no especificado" para distinguir de None (que significa "sin financiera" /
# "sin estado" de forma explícita) al editar un cliente.
_SIN_ESPECIFICAR = object()


def crear_cliente(
    nombre: str,
    cedula: str,
    telefono: str,
    email: str,
    direccion: str,
    financiera_id: int | None = None,
    estado_financiamiento: str | None = None,
) -> sqlite3.Row:
    if cliente_model.obtener_por_cedula(cedula.strip()) is not None:
        raise ValueError(f"Ya existe un cliente registrado con la cédula {cedula}.")
    cliente_id = cliente_model.crear(
        nombre.strip(), cedula.strip(), telefono.strip(), email.strip(), direccion.strip(),
        financiera_id, estado_financiamiento,
    )
    return cliente_model.obtener_por_id(cliente_id)


def editar_cliente(
    cliente_id: int,
    nombre: str,
    telefono: str,
    email: str,
    direccion: str,
    financiera_id: int | None = _SIN_ESPECIFICAR,
    estado_financiamiento: str | None = _SIN_ESPECIFICAR,
) -> sqlite3.Row:
    actual = cliente_model.obtener_por_id(cliente_id)
    if actual is None:
        raise ValueError("El cliente indicado no existe.")
    if financiera_id is _SIN_ESPECIFICAR:
        financiera_id = actual["financiera_id"]
    if estado_financiamiento is _SIN_ESPECIFICAR:
        estado_financiamiento = actual["estado_financiamiento"]
    cliente_model.actualizar(
        cliente_id, nombre.strip(), telefono.strip(), email.strip(), direccion.strip(),
        financiera_id, estado_financiamiento,
    )
    return cliente_model.obtener_por_id(cliente_id)


def eliminar_cliente(cliente_id: int) -> None:
    if cliente_model.obtener_por_id(cliente_id) is None:
        raise ValueError("El cliente indicado no existe.")
    cliente_model.eliminar(cliente_id)


def listar_clientes() -> list[sqlite3.Row]:
    return cliente_model.listar()


def buscar_clientes(texto: str) -> list[sqlite3.Row]:
    return cliente_model.buscar(texto.strip())
