"""Modelo de Financiera: acceso a datos de la tabla `financieras`.

Catálogo simple de entidades financieras (bancos, financieras) que un
cliente puede usar para financiar su compra.
"""

import sqlite3

from app.models.database import get_connection


def crear(nombre: str) -> int:
    with get_connection() as conn:
        cur = conn.execute("INSERT INTO financieras (nombre) VALUES (?)", (nombre,))
        conn.commit()
        return cur.lastrowid


def obtener_por_id(financiera_id: int) -> sqlite3.Row | None:
    with get_connection() as conn:
        return conn.execute("SELECT * FROM financieras WHERE id = ?", (financiera_id,)).fetchone()


def obtener_por_nombre(nombre: str) -> sqlite3.Row | None:
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM financieras WHERE nombre = ? COLLATE NOCASE", (nombre,)
        ).fetchone()


def listar() -> list[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute("SELECT * FROM financieras ORDER BY nombre").fetchall()


def eliminar(financiera_id: int) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM financieras WHERE id = ?", (financiera_id,))
        conn.commit()
