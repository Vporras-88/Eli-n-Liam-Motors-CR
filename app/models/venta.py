"""Modelo de Venta: acceso a datos de la tabla `ventas`.

`registrar` ejecuta en una sola transacción la creación de la venta y el
cambio de estado de la moto a 'vendida', evitando vender dos veces la misma
unidad si dos operaciones se solaparan.
"""

import sqlite3

from app.models.database import get_connection


def registrar(
    moto_id: int, cliente_id: int, vendedor_id: int, precio_final: float, metodo_pago: str, moneda: str = "CRC"
) -> int:
    with get_connection() as conn:
        moto = conn.execute("SELECT estado FROM motocicletas WHERE id = ?", (moto_id,)).fetchone()
        if moto is None:
            raise ValueError("La motocicleta indicada no existe.")
        if moto["estado"] != "disponible":
            raise ValueError("La motocicleta ya no está disponible para la venta.")

        cur = conn.execute(
            """INSERT INTO ventas (moto_id, cliente_id, vendedor_id, fecha, precio_final, moneda, metodo_pago)
               VALUES (?, ?, ?, datetime('now', 'localtime'), ?, ?, ?)""",
            (moto_id, cliente_id, vendedor_id, precio_final, moneda, metodo_pago),
        )
        conn.execute("UPDATE motocicletas SET estado = 'vendida' WHERE id = ?", (moto_id,))
        conn.commit()
        return cur.lastrowid


def actualizar(venta_id: int, precio_final: float, metodo_pago: str, moneda: str = "CRC") -> None:
    with get_connection() as conn:
        conn.execute(
            "UPDATE ventas SET precio_final = ?, moneda = ?, metodo_pago = ? WHERE id = ?",
            (precio_final, moneda, metodo_pago, venta_id),
        )
        conn.commit()


def eliminar(venta_id: int) -> None:
    """Elimina la venta y, si la moto sigue marcada como vendida, la vuelve a dejar disponible."""
    with get_connection() as conn:
        venta = conn.execute("SELECT moto_id FROM ventas WHERE id = ?", (venta_id,)).fetchone()
        if venta is None:
            raise ValueError("La venta indicada no existe.")
        conn.execute("DELETE FROM ventas WHERE id = ?", (venta_id,))
        conn.execute(
            "UPDATE motocicletas SET estado = 'disponible' WHERE id = ? AND estado = 'vendida'",
            (venta["moto_id"],),
        )
        conn.commit()


def obtener_por_id(venta_id: int) -> sqlite3.Row | None:
    with get_connection() as conn:
        return conn.execute(
            """SELECT v.*, m.marca, m.modelo, m.vin, c.nombre AS cliente_nombre, u.nombre AS vendedor_nombre
               FROM ventas v
               JOIN motocicletas m ON m.id = v.moto_id
               JOIN clientes c ON c.id = v.cliente_id
               JOIN usuarios u ON u.id = v.vendedor_id
               WHERE v.id = ?""",
            (venta_id,),
        ).fetchone()


def listar(desde: str | None = None, hasta: str | None = None, vendedor_id: int | None = None) -> list[sqlite3.Row]:
    query = """
        SELECT v.*, m.marca, m.modelo, m.vin, c.nombre AS cliente_nombre, u.nombre AS vendedor_nombre
        FROM ventas v
        JOIN motocicletas m ON m.id = v.moto_id
        JOIN clientes c ON c.id = v.cliente_id
        JOIN usuarios u ON u.id = v.vendedor_id
        WHERE 1 = 1
    """
    params: list = []
    if desde:
        query += " AND date(v.fecha) >= date(?)"
        params.append(desde)
    if hasta:
        query += " AND date(v.fecha) <= date(?)"
        params.append(hasta)
    if vendedor_id:
        query += " AND v.vendedor_id = ?"
        params.append(vendedor_id)
    query += " ORDER BY v.fecha DESC"
    with get_connection() as conn:
        return conn.execute(query, params).fetchall()


def total_por_rango(desde: str | None = None, hasta: str | None = None) -> float:
    filas = listar(desde=desde, hasta=hasta)
    return sum(f["precio_final"] for f in filas)
