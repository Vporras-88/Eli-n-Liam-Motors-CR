"""Modelo de Cliente: acceso a datos de la tabla `clientes`."""

import sqlite3

from app.models.database import get_connection


def crear(
    nombre: str,
    cedula: str,
    telefono: str,
    email: str,
    direccion: str,
    financiera_id: int | None = None,
    estado_financiamiento: str | None = None,
    vendedor_id: int | None = None,
) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            """INSERT INTO clientes
               (nombre, cedula, telefono, email, direccion, financiera_id, estado_financiamiento, vendedor_id, fecha_registro)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now', 'localtime'))""",
            (nombre, cedula, telefono, email, direccion, financiera_id, estado_financiamiento, vendedor_id),
        )
        conn.commit()
        return cur.lastrowid


_SELECT_CON_RELACIONES = """
    SELECT clientes.*, financieras.nombre AS financiera_nombre, vendedores.nombre AS vendedor_nombre
    FROM clientes
    LEFT JOIN financieras ON financieras.id = clientes.financiera_id
    LEFT JOIN vendedores ON vendedores.id = clientes.vendedor_id
"""


def obtener_por_id(cliente_id: int) -> sqlite3.Row | None:
    with get_connection() as conn:
        return conn.execute(f"{_SELECT_CON_RELACIONES} WHERE clientes.id = ?", (cliente_id,)).fetchone()


def obtener_por_cedula(cedula: str) -> sqlite3.Row | None:
    with get_connection() as conn:
        return conn.execute("SELECT * FROM clientes WHERE cedula = ?", (cedula,)).fetchone()


def listar() -> list[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute(f"{_SELECT_CON_RELACIONES} ORDER BY clientes.nombre").fetchall()


def buscar(texto: str) -> list[sqlite3.Row]:
    patron = f"%{texto}%"
    with get_connection() as conn:
        return conn.execute(
            f"{_SELECT_CON_RELACIONES} WHERE clientes.nombre LIKE ? OR clientes.cedula LIKE ? ORDER BY clientes.nombre",
            (patron, patron),
        ).fetchall()


def actualizar(
    cliente_id: int,
    nombre: str,
    telefono: str,
    email: str,
    direccion: str,
    financiera_id: int | None = None,
    estado_financiamiento: str | None = None,
    vendedor_id: int | None = None,
) -> None:
    with get_connection() as conn:
        conn.execute(
            """UPDATE clientes
               SET nombre = ?, telefono = ?, email = ?, direccion = ?,
                   financiera_id = ?, estado_financiamiento = ?, vendedor_id = ?
               WHERE id = ?""",
            (nombre, telefono, email, direccion, financiera_id, estado_financiamiento, vendedor_id, cliente_id),
        )
        conn.commit()


def eliminar(cliente_id: int) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM clientes WHERE id = ?", (cliente_id,))
        conn.commit()
