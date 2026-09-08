"""Controlador de Clientes."""

import sqlite3

from app.models import cliente as cliente_model


def crear_cliente(nombre: str, cedula: str, telefono: str, email: str, direccion: str) -> sqlite3.Row:
    if cliente_model.obtener_por_cedula(cedula.strip()) is not None:
        raise ValueError(f"Ya existe un cliente registrado con la cédula {cedula}.")
    cliente_id = cliente_model.crear(nombre.strip(), cedula.strip(), telefono.strip(), email.strip(), direccion.strip())
    return cliente_model.obtener_por_id(cliente_id)


def editar_cliente(cliente_id: int, nombre: str, telefono: str, email: str, direccion: str) -> sqlite3.Row:
    if cliente_model.obtener_por_id(cliente_id) is None:
        raise ValueError("El cliente indicado no existe.")
    cliente_model.actualizar(cliente_id, nombre.strip(), telefono.strip(), email.strip(), direccion.strip())
    return cliente_model.obtener_por_id(cliente_id)


def eliminar_cliente(cliente_id: int) -> None:
    if cliente_model.obtener_por_id(cliente_id) is None:
        raise ValueError("El cliente indicado no existe.")
    cliente_model.eliminar(cliente_id)


def listar_clientes() -> list[sqlite3.Row]:
    return cliente_model.listar()


def buscar_clientes(texto: str) -> list[sqlite3.Row]:
    return cliente_model.buscar(texto.strip())
