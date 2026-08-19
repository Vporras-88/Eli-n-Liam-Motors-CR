"""Vista del módulo de Clientes."""

from app.controllers import cliente_controller
from app.utils import validators as v
from app.views.cli_helpers import (
    mostrar_error,
    mostrar_exito,
    mostrar_tabla,
    pausar,
    pedir_entero,
    pedir_menu,
    pedir_texto,
    titulo,
)

COLUMNAS = ["id", "nombre", "cedula", "telefono", "email", "direccion"]


def _listar(filas) -> None:
    mostrar_tabla("Clientes", COLUMNAS, filas)


def menu_clientes() -> None:
    while True:
        opcion = pedir_menu(
            "— Gestión de Clientes —",
            {
                "1": "Listar clientes",
                "2": "Agregar cliente",
                "3": "Editar cliente",
                "4": "Buscar cliente (nombre o cédula)",
                "0": "Volver al menú principal",
            },
        )
        if opcion == "1":
            titulo("Listado de Clientes")
            _listar(cliente_controller.listar_clientes())
            pausar()
        elif opcion == "2":
            _agregar_cliente()
        elif opcion == "3":
            _editar_cliente()
        elif opcion == "4":
            _buscar_cliente()
        elif opcion == "0":
            return


def _agregar_cliente() -> None:
    titulo("Agregar Cliente")
    nombre = pedir_texto("Nombre completo")
    cedula = pedir_texto("Cédula", validador=v.validar_cedula)
    telefono = pedir_texto("Teléfono (0000-0000)", validador=v.validar_telefono, opcional=True)
    email = pedir_texto("Email", validador=v.validar_email, opcional=True)
    direccion = pedir_texto("Dirección", opcional=True)
    try:
        cliente = cliente_controller.crear_cliente(nombre, cedula, telefono, email, direccion)
        mostrar_exito(f"Cliente '{cliente['nombre']}' registrado con id {cliente['id']}.")
    except ValueError as e:
        mostrar_error(str(e))
    pausar()


def _editar_cliente() -> None:
    titulo("Editar Cliente")
    _listar(cliente_controller.listar_clientes())
    cliente_id = pedir_entero("ID del cliente a editar", validador=lambda x: v.validar_entero_positivo(x, "ID"))
    nombre = pedir_texto("Nuevo nombre")
    telefono = pedir_texto("Nuevo teléfono", validador=v.validar_telefono, opcional=True)
    email = pedir_texto("Nuevo email", validador=v.validar_email, opcional=True)
    direccion = pedir_texto("Nueva dirección", opcional=True)
    try:
        cliente = cliente_controller.editar_cliente(cliente_id, nombre, telefono, email, direccion)
        mostrar_exito(f"Cliente id {cliente['id']} actualizado.")
    except ValueError as e:
        mostrar_error(str(e))
    pausar()


def _buscar_cliente() -> None:
    titulo("Buscar Cliente")
    texto = pedir_texto("Texto a buscar (nombre o cédula)")
    _listar(cliente_controller.buscar_clientes(texto))
    pausar()
