"""Controlador de autenticación: valida credenciales y permisos por rol."""

import sqlite3

from app.models import usuario as usuario_model
from app.utils.security import verificar_password

# Opciones de menú principal habilitadas para cada rol.
PERMISOS_MENU = {
    "admin": {"inventario", "clientes", "ventas", "repuestos", "ventas_repuestos", "taller", "reportes", "usuarios"},
    "vendedor": {"inventario", "clientes", "ventas", "ventas_repuestos", "reportes"},
    "mecanico": {"repuestos", "taller", "reportes"},
}


def login(usuario: str, password: str) -> sqlite3.Row | None:
    """Devuelve la fila del usuario si las credenciales son válidas y está activo."""
    fila = usuario_model.obtener_por_usuario(usuario.strip())
    if fila is None or not fila["activo"]:
        return None
    if not verificar_password(password, fila["password_hash"]):
        return None
    return fila


def puede_acceder(usuario_actual: sqlite3.Row, opcion: str) -> bool:
    return opcion in PERMISOS_MENU.get(usuario_actual["rol"], set())
