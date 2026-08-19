"""Controlador de Usuarios (solo accesible para admin)."""

import sqlite3

from app.models import usuario as usuario_model
from app.models.usuario import ROLES


def crear_usuario(nombre: str, usuario: str, password: str, rol: str) -> sqlite3.Row:
    if rol not in ROLES:
        raise ValueError(f"Rol inválido. Debe ser uno de: {', '.join(ROLES)}.")
    if usuario_model.obtener_por_usuario(usuario.strip()) is not None:
        raise ValueError(f"Ya existe un usuario con el nombre de usuario '{usuario}'.")
    usuario_id = usuario_model.crear(nombre.strip(), usuario.strip(), password, rol)
    return usuario_model.obtener_por_id(usuario_id)


def editar_usuario(usuario_id: int, nombre: str, rol: str) -> sqlite3.Row:
    if rol not in ROLES:
        raise ValueError(f"Rol inválido. Debe ser uno de: {', '.join(ROLES)}.")
    if usuario_model.obtener_por_id(usuario_id) is None:
        raise ValueError("El usuario indicado no existe.")
    usuario_model.actualizar(usuario_id, nombre.strip(), rol)
    return usuario_model.obtener_por_id(usuario_id)


def cambiar_password(usuario_id: int, password_nueva: str) -> None:
    if usuario_model.obtener_por_id(usuario_id) is None:
        raise ValueError("El usuario indicado no existe.")
    usuario_model.cambiar_password(usuario_id, password_nueva)


def activar_desactivar(usuario_id: int, activo: bool) -> sqlite3.Row:
    if usuario_model.obtener_por_id(usuario_id) is None:
        raise ValueError("El usuario indicado no existe.")
    usuario_model.set_activo(usuario_id, activo)
    return usuario_model.obtener_por_id(usuario_id)


def listar_usuarios() -> list[sqlite3.Row]:
    return usuario_model.listar()


def listar_mecanicos() -> list[sqlite3.Row]:
    return usuario_model.listar_por_rol("mecanico")
