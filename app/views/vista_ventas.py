"""Vista del módulo de Ventas."""

import sqlite3

from app.controllers import cliente_controller, inventario_controller, venta_controller
from app.utils import validators as v
from app.views.cli_helpers import (
    mostrar_error,
    mostrar_exito,
    mostrar_tabla,
    pausar,
    pedir_decimal,
    pedir_entero,
    pedir_menu,
    pedir_opcion,
    pedir_texto,
    titulo,
)

COLUMNAS_VENTAS = ["id", "fecha", "marca", "modelo", "vin", "cliente_nombre", "vendedor_nombre", "precio_final", "metodo_pago"]


def menu_ventas(usuario_actual: sqlite3.Row) -> None:
    while True:
        opcion = pedir_menu(
            "— Ventas —",
            {
                "1": "Registrar venta",
                "2": "Historial de ventas",
                "0": "Volver al menú principal",
            },
        )
        if opcion == "1":
            _registrar_venta(usuario_actual)
        elif opcion == "2":
            titulo("Historial de Ventas")
            mostrar_tabla("Ventas", COLUMNAS_VENTAS, venta_controller.listar_ventas())
            pausar()
        elif opcion == "0":
            return


def _registrar_venta(usuario_actual: sqlite3.Row) -> None:
    titulo("Registrar Venta")
    disponibles = inventario_controller.listar_disponibles()
    if not disponibles:
        mostrar_error("No hay motocicletas disponibles para vender.")
        pausar()
        return
    mostrar_tabla("Motocicletas Disponibles", ["id", "marca", "modelo", "anio", "precio"], disponibles)
    moto_id = pedir_entero("ID de la motocicleta a vender", validador=lambda x: v.validar_entero_positivo(x, "ID"))

    mostrar_tabla("Clientes", ["id", "nombre", "cedula"], cliente_controller.listar_clientes())
    cliente_id = pedir_entero("ID del cliente comprador", validador=lambda x: v.validar_entero_positivo(x, "ID"))

    precio_final = pedir_decimal("Precio final de venta", validador=lambda x: v.validar_decimal_positivo(x, "Precio"))
    metodo_pago = pedir_opcion("Método de pago", list(venta_controller.METODOS_PAGO))

    try:
        venta = venta_controller.registrar_venta(moto_id, cliente_id, usuario_actual["id"], precio_final, metodo_pago)
        mostrar_exito(
            f"Venta registrada: {venta['marca']} {venta['modelo']} a {venta['cliente_nombre']} "
            f"por {venta['precio_final']}."
        )
    except ValueError as e:
        mostrar_error(str(e))
    pausar()
