"""Modelo de Venta de Repuesto/Accesorio: acceso a datos de la tabla `ventas_repuestos`.

`registrar` ejecuta en una sola transacción la creación de la venta y el
descuento de stock del repuesto, evitando vender más unidades de las
disponibles si dos operaciones se solaparan.
"""

import sqlite3

from app.models.database import get_connection


def registrar(
    repuesto_id: int, cliente_id: int, vendedor_id: int, cantidad: int, precio_unitario: float, metodo_pago: str
) -> int:
    with get_connection() as conn:
        repuesto = conn.execute("SELECT stock FROM repuestos WHERE id = ?", (repuesto_id,)).fetchone()
        if repuesto is None:
            raise ValueError("El repuesto indicado no existe.")
        if repuesto["stock"] < cantidad:
            raise ValueError("No hay stock suficiente para esta venta.")

        cur = conn.execute(
            """INSERT INTO ventas_repuestos (repuesto_id, cliente_id, vendedor_id, fecha, cantidad, precio_unitario, metodo_pago)
               VALUES (?, ?, ?, datetime('now', 'localtime'), ?, ?, ?)""",
            (repuesto_id, cliente_id, vendedor_id, cantidad, precio_unitario, metodo_pago),
        )
        conn.execute("UPDATE repuestos SET stock = stock - ? WHERE id = ?", (cantidad, repuesto_id))
        conn.commit()
        return cur.lastrowid


def obtener_por_id(venta_id: int) -> sqlite3.Row | None:
    with get_connection() as conn:
        return conn.execute(
            """SELECT vr.*, r.nombre AS repuesto_nombre, r.categoria, c.nombre AS cliente_nombre, u.nombre AS vendedor_nombre
               FROM ventas_repuestos vr
               JOIN repuestos r ON r.id = vr.repuesto_id
               JOIN clientes c ON c.id = vr.cliente_id
               JOIN usuarios u ON u.id = vr.vendedor_id
               WHERE vr.id = ?""",
            (venta_id,),
        ).fetchone()


def listar(desde: str | None = None, hasta: str | None = None, vendedor_id: int | None = None) -> list[sqlite3.Row]:
    query = """
        SELECT vr.*, r.nombre AS repuesto_nombre, r.categoria, c.nombre AS cliente_nombre, u.nombre AS vendedor_nombre
        FROM ventas_repuestos vr
        JOIN repuestos r ON r.id = vr.repuesto_id
        JOIN clientes c ON c.id = vr.cliente_id
        JOIN usuarios u ON u.id = vr.vendedor_id
        WHERE 1 = 1
    """
    params: list = []
    if desde:
        query += " AND date(vr.fecha) >= date(?)"
        params.append(desde)
    if hasta:
        query += " AND date(vr.fecha) <= date(?)"
        params.append(hasta)
    if vendedor_id:
        query += " AND vr.vendedor_id = ?"
        params.append(vendedor_id)
    query += " ORDER BY vr.fecha DESC"
    with get_connection() as conn:
        return conn.execute(query, params).fetchall()


def total_por_rango(desde: str | None = None, hasta: str | None = None) -> float:
    filas = listar(desde=desde, hasta=hasta)
    return sum(f["cantidad"] * f["precio_unitario"] for f in filas)
