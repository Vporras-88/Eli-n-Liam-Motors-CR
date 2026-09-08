"""Modelo de Repuesto/Accesorio: acceso a datos de la tabla `repuestos`."""

import sqlite3

from app.models.database import get_connection

CATEGORIAS = ("repuesto", "accesorio")
STOCK_BAJO_UMBRAL = 5


def crear(
    nombre: str,
    categoria: str,
    marca_compatible: str,
    precio: float,
    stock: int,
    proveedor: str,
    moneda: str = "CRC",
    imagen: str | None = None,
) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            """INSERT INTO repuestos (nombre, categoria, marca_compatible, precio, moneda, stock, proveedor, imagen)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (nombre, categoria, marca_compatible, precio, moneda, stock, proveedor, imagen),
        )
        conn.commit()
        return cur.lastrowid


def obtener_por_id(repuesto_id: int) -> sqlite3.Row | None:
    with get_connection() as conn:
        return conn.execute("SELECT * FROM repuestos WHERE id = ?", (repuesto_id,)).fetchone()


def listar() -> list[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute("SELECT * FROM repuestos ORDER BY nombre").fetchall()


def listar_stock_bajo(umbral: int = STOCK_BAJO_UMBRAL) -> list[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM repuestos WHERE stock <= ? ORDER BY stock ASC", (umbral,)
        ).fetchall()


def actualizar(
    repuesto_id: int,
    nombre: str,
    marca_compatible: str,
    precio: float,
    proveedor: str,
    moneda: str = "CRC",
    imagen: str | None = None,
) -> None:
    with get_connection() as conn:
        conn.execute(
            """UPDATE repuestos
               SET nombre = ?, marca_compatible = ?, precio = ?, moneda = ?, proveedor = ?, imagen = ?
               WHERE id = ?""",
            (nombre, marca_compatible, precio, moneda, proveedor, imagen, repuesto_id),
        )
        conn.commit()


def ajustar_stock(repuesto_id: int, cantidad_delta: int) -> None:
    """Suma (positivo) o resta (negativo) unidades al stock. Nunca lo deja negativo."""
    with get_connection() as conn:
        actual = conn.execute("SELECT stock FROM repuestos WHERE id = ?", (repuesto_id,)).fetchone()
        if actual is None:
            raise ValueError("El repuesto indicado no existe.")
        nuevo_stock = actual["stock"] + cantidad_delta
        if nuevo_stock < 0:
            raise ValueError("No hay stock suficiente para esta operación.")
        conn.execute("UPDATE repuestos SET stock = ? WHERE id = ?", (nuevo_stock, repuesto_id))
        conn.commit()


def eliminar(repuesto_id: int) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM repuestos WHERE id = ?", (repuesto_id,))
        conn.commit()
