"""Modelo de Usuario: acceso a datos de la tabla `usuarios`."""

import sqlite3

from app.models.database import get_connection
from app.utils.security import hash_password

ROLES = ("admin", "vendedor", "mecanico")


def crear(nombre: str, usuario: str, password_plano: str, rol: str) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            """INSERT INTO usuarios (nombre, usuario, password_hash, rol, activo, fecha_creacion)
               VALUES (?, ?, ?, ?, 1, datetime('now', 'localtime'))""",
            (nombre, usuario, hash_password(password_plano), rol),
        )
        conn.commit()
        return cur.lastrowid


def obtener_por_id(usuario_id: int) -> sqlite3.Row | None:
    with get_connection() as conn:
        return conn.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,)).fetchone()


def obtener_por_usuario(usuario: str) -> sqlite3.Row | None:
    with get_connection() as conn:
        return conn.execute("SELECT * FROM usuarios WHERE usuario = ?", (usuario,)).fetchone()


def listar(solo_activos: bool = False) -> list[sqlite3.Row]:
    query = "SELECT * FROM usuarios"
    if solo_activos:
        query += " WHERE activo = 1"
    query += " ORDER BY nombre"
    with get_connection() as conn:
        return conn.execute(query).fetchall()


def listar_por_rol(rol: str, solo_activos: bool = True) -> list[sqlite3.Row]:
    query = "SELECT * FROM usuarios WHERE rol = ?"
    if solo_activos:
        query += " AND activo = 1"
    query += " ORDER BY nombre"
    with get_connection() as conn:
        return conn.execute(query, (rol,)).fetchall()


def actualizar(usuario_id: int, nombre: str, rol: str) -> None:
    with get_connection() as conn:
        conn.execute(
            "UPDATE usuarios SET nombre = ?, rol = ? WHERE id = ?",
            (nombre, rol, usuario_id),
        )
        conn.commit()


def cambiar_password(usuario_id: int, password_plano: str) -> None:
    with get_connection() as conn:
        conn.execute(
            "UPDATE usuarios SET password_hash = ? WHERE id = ?",
            (hash_password(password_plano), usuario_id),
        )
        conn.commit()


def set_activo(usuario_id: int, activo: bool) -> None:
    with get_connection() as conn:
        conn.execute(
            "UPDATE usuarios SET activo = ? WHERE id = ?",
            (1 if activo else 0, usuario_id),
        )
        conn.commit()
