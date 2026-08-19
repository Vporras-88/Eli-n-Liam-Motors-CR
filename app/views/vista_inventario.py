"""Vista del módulo de Inventario de Motocicletas."""

from app.controllers import inventario_controller
from app.models.motocicleta import ESTADOS
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

COLUMNAS = ["id", "marca", "modelo", "anio", "color", "cilindraje", "vin", "precio", "estado"]


def _listar(filas) -> None:
    mostrar_tabla("Motocicletas", COLUMNAS, filas)


def menu_inventario() -> None:
    while True:
        opcion = pedir_menu(
            "— Inventario de Motocicletas —",
            {
                "1": "Listar todas",
                "2": "Listar disponibles",
                "3": "Agregar motocicleta",
                "4": "Editar motocicleta",
                "5": "Cambiar estado",
                "6": "Buscar (marca/modelo/VIN)",
                "0": "Volver al menú principal",
            },
        )
        if opcion == "1":
            titulo("Inventario Completo")
            _listar(inventario_controller.listar_motos())
            pausar()
        elif opcion == "2":
            titulo("Motocicletas Disponibles")
            _listar(inventario_controller.listar_disponibles())
            pausar()
        elif opcion == "3":
            _agregar_moto()
        elif opcion == "4":
            _editar_moto()
        elif opcion == "5":
            _cambiar_estado()
        elif opcion == "6":
            _buscar_moto()
        elif opcion == "0":
            return


def _agregar_moto() -> None:
    titulo("Agregar Motocicleta")
    marca = pedir_texto("Marca")
    modelo = pedir_texto("Modelo")
    anio = pedir_entero("Año", validador=v.validar_anio)
    color = pedir_texto("Color", opcional=True)
    cilindraje = pedir_entero("Cilindraje (cc)", validador=lambda x: v.validar_entero_positivo(x, "Cilindraje"))
    vin = pedir_texto("Número de chasis / VIN")
    precio = pedir_decimal("Precio", validador=lambda x: v.validar_decimal_positivo(x, "Precio"))
    try:
        moto = inventario_controller.crear_moto(marca, modelo, anio, color, cilindraje, vin, precio)
        mostrar_exito(f"Motocicleta {moto['marca']} {moto['modelo']} registrada con id {moto['id']}.")
    except ValueError as e:
        mostrar_error(str(e))
    pausar()


def _editar_moto() -> None:
    titulo("Editar Motocicleta")
    _listar(inventario_controller.listar_motos())
    moto_id = pedir_entero("ID de la motocicleta a editar", validador=lambda x: v.validar_entero_positivo(x, "ID"))
    marca = pedir_texto("Nueva marca")
    modelo = pedir_texto("Nuevo modelo")
    anio = pedir_entero("Nuevo año", validador=v.validar_anio)
    color = pedir_texto("Nuevo color", opcional=True)
    cilindraje = pedir_entero("Nuevo cilindraje (cc)", validador=lambda x: v.validar_entero_positivo(x, "Cilindraje"))
    precio = pedir_decimal("Nuevo precio", validador=lambda x: v.validar_decimal_positivo(x, "Precio"))
    try:
        moto = inventario_controller.editar_moto(moto_id, marca, modelo, anio, color, cilindraje, precio)
        mostrar_exito(f"Motocicleta id {moto['id']} actualizada.")
    except ValueError as e:
        mostrar_error(str(e))
    pausar()


def _cambiar_estado() -> None:
    titulo("Cambiar Estado de Motocicleta")
    _listar(inventario_controller.listar_motos())
    moto_id = pedir_entero("ID de la motocicleta", validador=lambda x: v.validar_entero_positivo(x, "ID"))
    estado = pedir_opcion("Nuevo estado", list(ESTADOS))
    try:
        moto = inventario_controller.cambiar_estado_moto(moto_id, estado)
        mostrar_exito(f"Motocicleta id {moto['id']} ahora está '{moto['estado']}'.")
    except ValueError as e:
        mostrar_error(str(e))
    pausar()


def _buscar_moto() -> None:
    titulo("Buscar Motocicleta")
    texto = pedir_texto("Texto a buscar (marca, modelo o VIN)")
    _listar(inventario_controller.buscar_motos(texto))
    pausar()
