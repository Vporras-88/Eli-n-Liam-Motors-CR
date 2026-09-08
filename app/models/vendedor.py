"""Modelo de Vendedor: acceso a datos de la tabla `vendedores`.

Catálogo simple de nombres de vendedores que se puede asignar a un
cliente (independiente de los usuarios del sistema con rol 'vendedor').
"""

import sqlite3

from app.models.database import get_connection


def crear(nombre: str) -> int:
    with get_connection() as conn:
        cur = conn.execute("INSERT INTO vendedores (nombre) VALUES (?)", (nombre,))
        conn.commit()
        return cur.lastrowid


def obtener_por_id(vendedor_id: int) -> sqlite3.Row | None:
    with get_connection() as conn:
        return conn.execute("SELECT * FROM vendedores WHERE id = ?", (vendedor_id,)).fetchone()


def obtener_por_nombre(nombre: str) -> sqlite3.Row | None:
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM vendedores WHERE nombre = ? COLLATE NOCASE", (nombre,)
        ).fetchone()


def listar() -> list[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute("SELECT * FROM vendedores ORDER BY nombre").fetchall()


def eliminar(vendedor_id: int) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM vendedores WHERE id = ?", (vendedor_id,))
        conn.commit()
