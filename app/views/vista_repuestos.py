"""Vista del módulo de Repuestos y Accesorios."""

from app.controllers import repuesto_controller
from app.models.repuesto import CATEGORIAS
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

COLUMNAS = ["id", "nombre", "categoria", "marca_compatible", "precio", "stock", "proveedor"]


def _listar(filas) -> None:
    mostrar_tabla("Repuestos y Accesorios", COLUMNAS, filas)


def menu_repuestos() -> None:
    while True:
        opcion = pedir_menu(
            "— Repuestos y Accesorios —",
            {
                "1": "Listar repuestos/accesorios",
                "2": "Agregar repuesto/accesorio",
                "3": "Editar repuesto/accesorio",
                "4": "Registrar entrada de stock",
                "5": "Registrar salida de stock",
                "6": "Ver stock bajo",
                "0": "Volver al menú principal",
            },
        )
        if opcion == "1":
            titulo("Listado de Repuestos y Accesorios")
            _listar(repuesto_controller.listar_repuestos())
            pausar()
        elif opcion == "2":
            _agregar_repuesto()
        elif opcion == "3":
            _editar_repuesto()
        elif opcion == "4":
            _mover_stock(entrada=True)
        elif opcion == "5":
            _mover_stock(entrada=False)
        elif opcion == "6":
            titulo("Repuestos con Stock Bajo")
            _listar(repuesto_controller.listar_stock_bajo())
            pausar()
        elif opcion == "0":
            return


def _agregar_repuesto() -> None:
    titulo("Agregar Repuesto/Accesorio")
    nombre = pedir_texto("Nombre")
    categoria = pedir_opcion("Categoría", list(CATEGORIAS))
    marca_compatible = pedir_texto("Marca compatible", opcional=True)
    precio = pedir_decimal("Precio", validador=lambda x: v.validar_decimal_positivo(x, "Precio"))
    stock = pedir_entero("Stock inicial", validador=lambda x: v.validar_entero_no_negativo(x, "Stock"))
    proveedor = pedir_texto("Proveedor", opcional=True)
    try:
        repuesto = repuesto_controller.crear_repuesto(nombre, categoria, marca_compatible, precio, stock, proveedor)
        mostrar_exito(f"'{repuesto['nombre']}' registrado con id {repuesto['id']}.")
    except ValueError as e:
        mostrar_error(str(e))
    pausar()


def _editar_repuesto() -> None:
    titulo("Editar Repuesto/Accesorio")
    _listar(repuesto_controller.listar_repuestos())
    repuesto_id = pedir_entero("ID a editar", validador=lambda x: v.validar_entero_positivo(x, "ID"))
    nombre = pedir_texto("Nuevo nombre")
    marca_compatible = pedir_texto("Nueva marca compatible", opcional=True)
    precio = pedir_decimal("Nuevo precio", validador=lambda x: v.validar_decimal_positivo(x, "Precio"))
    proveedor = pedir_texto("Nuevo proveedor", opcional=True)
    try:
        repuesto = repuesto_controller.editar_repuesto(repuesto_id, nombre, marca_compatible, precio, proveedor)
        mostrar_exito(f"Repuesto id {repuesto['id']} actualizado.")
    except ValueError as e:
        mostrar_error(str(e))
    pausar()


def _mover_stock(entrada: bool) -> None:
    titulo("Entrada de Stock" if entrada else "Salida de Stock")
    _listar(repuesto_controller.listar_repuestos())
    repuesto_id = pedir_entero("ID del repuesto", validador=lambda x: v.validar_entero_positivo(x, "ID"))
    cantidad = pedir_entero("Cantidad", validador=lambda x: v.validar_entero_positivo(x, "Cantidad"))
    try:
        if entrada:
            repuesto = repuesto_controller.registrar_entrada_stock(repuesto_id, cantidad)
        else:
            repuesto = repuesto_controller.registrar_salida_stock(repuesto_id, cantidad)
        mostrar_exito(f"Stock de '{repuesto['nombre']}' actualizado a {repuesto['stock']} unidades.")
    except ValueError as e:
        mostrar_error(str(e))
    pausar()
