"""Modelo de Orden de Trabajo (taller mecánico) y sus repuestos utilizados."""

import sqlite3

from app.models.database import get_connection

ESTADOS = ("pendiente", "en_proceso", "completada", "entregada")


def crear(
    cliente_id: int,
    moto_marca: str,
    moto_modelo: str,
    moto_placa: str,
    mecanico_id: int | None,
    descripcion_problema: str,
    costo_mano_obra: float,
) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            """INSERT INTO ordenes_trabajo
               (cliente_id, moto_marca, moto_modelo, moto_placa, mecanico_id,
                descripcion_problema, estado, costo_mano_obra, fecha_ingreso)
               VALUES (?, ?, ?, ?, ?, ?, 'pendiente', ?, datetime('now', 'localtime'))""",
            (cliente_id, moto_marca, moto_modelo, moto_placa, mecanico_id, descripcion_problema, costo_mano_obra),
        )
        conn.commit()
        return cur.lastrowid


def obtener_por_id(orden_id: int) -> sqlite3.Row | None:
    with get_connection() as conn:
        return conn.execute("SELECT * FROM ordenes_trabajo WHERE id = ?", (orden_id,)).fetchone()


def listar(estado: str | None = None) -> list[sqlite3.Row]:
    query = """
        SELECT o.*, c.nombre AS cliente_nombre, u.nombre AS mecanico_nombre
        FROM ordenes_trabajo o
        JOIN clientes c ON c.id = o.cliente_id
        LEFT JOIN usuarios u ON u.id = o.mecanico_id
    """
    params: tuple = ()
    if estado:
        query += " WHERE o.estado = ?"
        params = (estado,)
    query += " ORDER BY o.fecha_ingreso DESC"
    with get_connection() as conn:
        return conn.execute(query, params).fetchall()


def cambiar_estado(orden_id: int, estado: str) -> None:
    with get_connection() as conn:
        if estado == "entregada":
            conn.execute(
                "UPDATE ordenes_trabajo SET estado = ?, fecha_salida = datetime('now', 'localtime') WHERE id = ?",
                (estado, orden_id),
            )
        else:
            conn.execute("UPDATE ordenes_trabajo SET estado = ? WHERE id = ?", (estado, orden_id))
        conn.commit()


def agregar_repuesto(orden_id: int, repuesto_id: int, cantidad: int) -> None:
    """Registra el uso de un repuesto en la orden y descuenta su stock, en una sola transacción."""
    with get_connection() as conn:
        repuesto = conn.execute("SELECT precio, stock FROM repuestos WHERE id = ?", (repuesto_id,)).fetchone()
        if repuesto is None:
            raise ValueError("El repuesto indicado no existe.")
        if repuesto["stock"] < cantidad:
            raise ValueError(f"Stock insuficiente: disponible {repuesto['stock']}, solicitado {cantidad}.")

        conn.execute(
            """INSERT INTO orden_repuestos (orden_id, repuesto_id, cantidad, precio_unitario)
               VALUES (?, ?, ?, ?)""",
            (orden_id, repuesto_id, cantidad, repuesto["precio"]),
        )
        conn.execute(
            "UPDATE repuestos SET stock = stock - ? WHERE id = ?",
            (cantidad, repuesto_id),
        )
        conn.commit()


def listar_repuestos_de_orden(orden_id: int) -> list[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute(
            """SELECT orr.*, r.nombre AS repuesto_nombre
               FROM orden_repuestos orr
               JOIN repuestos r ON r.id = orr.repuesto_id
               WHERE orr.orden_id = ?""",
            (orden_id,),
        ).fetchall()


def costo_total(orden_id: int) -> float:
    orden = obtener_por_id(orden_id)
    if orden is None:
        raise ValueError("La orden indicada no existe.")
    repuestos = listar_repuestos_de_orden(orden_id)
    total_repuestos = sum(r["cantidad"] * r["precio_unitario"] for r in repuestos)
    return orden["costo_mano_obra"] + total_repuestos
