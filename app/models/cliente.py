"""Modelo de Cliente: acceso a datos de la tabla `clientes`."""

import sqlite3

from app.models.database import get_connection


def crear(nombre: str, cedula: str, telefono: str, email: str, direccion: str) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            """INSERT INTO clientes (nombre, cedula, telefono, email, direccion, fecha_registro)
               VALUES (?, ?, ?, ?, ?, datetime('now', 'localtime'))""",
            (nombre, cedula, telefono, email, direccion),
        )
        conn.commit()
        return cur.lastrowid


def obtener_por_id(cliente_id: int) -> sqlite3.Row | None:
    with get_connection() as conn:
        return conn.execute("SELECT * FROM clientes WHERE id = ?", (cliente_id,)).fetchone()


def obtener_por_cedula(cedula: str) -> sqlite3.Row | None:
    with get_connection() as conn:
        return conn.execute("SELECT * FROM clientes WHERE cedula = ?", (cedula,)).fetchone()


def listar() -> list[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute("SELECT * FROM clientes ORDER BY nombre").fetchall()


def buscar(texto: str) -> list[sqlite3.Row]:
    patron = f"%{texto}%"
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM clientes WHERE nombre LIKE ? OR cedula LIKE ? ORDER BY nombre",
            (patron, patron),
        ).fetchall()


def actualizar(cliente_id: int, nombre: str, telefono: str, email: str, direccion: str) -> None:
    with get_connection() as conn:
        conn.execute(
            "UPDATE clientes SET nombre = ?, telefono = ?, email = ?, direccion = ? WHERE id = ?",
            (nombre, telefono, email, direccion, cliente_id),
        )
        conn.commit()


def eliminar(cliente_id: int) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM clientes WHERE id = ?", (cliente_id,))
        conn.commit()
