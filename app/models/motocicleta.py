"""Modelo de Motocicleta: acceso a datos de la tabla `motocicletas`."""

import sqlite3

from app.models.database import get_connection

ESTADOS = ("disponible", "reservada", "vendida")


def crear(marca: str, modelo: str, anio: int, color: str, cilindraje: int, vin: str, precio: float) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            """INSERT INTO motocicletas
               (marca, modelo, anio, color, cilindraje, vin, precio, estado, fecha_ingreso)
               VALUES (?, ?, ?, ?, ?, ?, ?, 'disponible', datetime('now', 'localtime'))""",
            (marca, modelo, anio, color, cilindraje, vin, precio),
        )
        conn.commit()
        return cur.lastrowid


def obtener_por_id(moto_id: int) -> sqlite3.Row | None:
    with get_connection() as conn:
        return conn.execute("SELECT * FROM motocicletas WHERE id = ?", (moto_id,)).fetchone()


def obtener_por_vin(vin: str) -> sqlite3.Row | None:
    with get_connection() as conn:
        return conn.execute("SELECT * FROM motocicletas WHERE vin = ?", (vin,)).fetchone()


def listar(estado: str | None = None) -> list[sqlite3.Row]:
    query = "SELECT * FROM motocicletas"
    params: tuple = ()
    if estado:
        query += " WHERE estado = ?"
        params = (estado,)
    query += " ORDER BY marca, modelo"
    with get_connection() as conn:
        return conn.execute(query, params).fetchall()


def buscar(texto: str) -> list[sqlite3.Row]:
    patron = f"%{texto}%"
    with get_connection() as conn:
        return conn.execute(
            """SELECT * FROM motocicletas
               WHERE marca LIKE ? OR modelo LIKE ? OR vin LIKE ?
               ORDER BY marca, modelo""",
            (patron, patron, patron),
        ).fetchall()


def actualizar(moto_id: int, marca: str, modelo: str, anio: int, color: str, cilindraje: int, precio: float) -> None:
    with get_connection() as conn:
        conn.execute(
            """UPDATE motocicletas
               SET marca = ?, modelo = ?, anio = ?, color = ?, cilindraje = ?, precio = ?
               WHERE id = ?""",
            (marca, modelo, anio, color, cilindraje, precio, moto_id),
        )
        conn.commit()


def cambiar_estado(moto_id: int, estado: str) -> None:
    with get_connection() as conn:
        conn.execute("UPDATE motocicletas SET estado = ? WHERE id = ?", (estado, moto_id))
        conn.commit()


def eliminar(moto_id: int) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM motocicletas WHERE id = ?", (moto_id,))
        conn.commit()
