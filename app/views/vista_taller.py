"""Vista del módulo de Taller Mecánico."""

from app.controllers import cliente_controller, repuesto_controller, taller_controller, usuario_controller
from app.models.orden_trabajo import ESTADOS
from app.utils import validators as v
from app.views.cli_helpers import (
    console,
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

COLUMNAS_ORDENES = [
    "id", "cliente_nombre", "moto_marca", "moto_modelo", "moto_placa",
    "mecanico_nombre", "estado", "costo_mano_obra", "fecha_ingreso",
]


def menu_taller() -> None:
    while True:
        opcion = pedir_menu(
            "— Taller Mecánico —",
            {
                "1": "Nueva orden de trabajo",
                "2": "Ver órdenes",
                "3": "Actualizar estado de una orden",
                "4": "Agregar repuesto usado a una orden",
                "5": "Ver detalle y costo total de una orden",
                "0": "Volver al menú principal",
            },
        )
        if opcion == "1":
            _nueva_orden()
        elif opcion == "2":
            _ver_ordenes()
        elif opcion == "3":
            _actualizar_estado()
        elif opcion == "4":
            _agregar_repuesto()
        elif opcion == "5":
            _ver_detalle()
        elif opcion == "0":
            return


def _nueva_orden() -> None:
    titulo("Nueva Orden de Trabajo")
    mostrar_tabla("Clientes", ["id", "nombre", "cedula"], cliente_controller.listar_clientes())
    cliente_id = pedir_entero("ID del cliente", validador=lambda x: v.validar_entero_positivo(x, "ID"))

    moto_marca = pedir_texto("Marca de la moto")
    moto_modelo = pedir_texto("Modelo de la moto")
    moto_placa = pedir_texto("Placa", opcional=True)

    mecanicos = usuario_controller.listar_mecanicos()
    mecanico_id = None
    if mecanicos:
        mostrar_tabla("Mecánicos disponibles", ["id", "nombre"], mecanicos)
        if pedir_opcion("¿Asignar mecánico ahora?", ["si", "no"]) == "si":
            mecanico_id = pedir_entero("ID del mecánico", validador=lambda x: v.validar_entero_positivo(x, "ID"))
    else:
        mostrar_error("No hay mecánicos registrados; la orden quedará sin asignar.")

    descripcion = pedir_texto("Descripción del problema")
    costo_mano_obra = pedir_decimal("Costo de mano de obra", validador=lambda x: v.validar_decimal_no_negativo(x, "Costo"))
    try:
        orden = taller_controller.crear_orden(
            cliente_id, moto_marca, moto_modelo, moto_placa, mecanico_id, descripcion, costo_mano_obra
        )
        mostrar_exito(f"Orden de trabajo id {orden['id']} creada con estado '{orden['estado']}'.")
    except ValueError as e:
        mostrar_error(str(e))
    pausar()


def _ver_ordenes() -> None:
    titulo("Órdenes de Trabajo")
    estado = pedir_opcion("Filtrar por estado (o 'todas')", ["todas", *ESTADOS])
    filtro = None if estado == "todas" else estado
    mostrar_tabla("Órdenes", COLUMNAS_ORDENES, taller_controller.listar_ordenes(estado=filtro))
    pausar()


def _actualizar_estado() -> None:
    titulo("Actualizar Estado de Orden")
    mostrar_tabla("Órdenes", COLUMNAS_ORDENES, taller_controller.listar_ordenes())
    orden_id = pedir_entero("ID de la orden", validador=lambda x: v.validar_entero_positivo(x, "ID"))
    nuevo_estado = pedir_opcion("Nuevo estado", list(ESTADOS))
    try:
        orden = taller_controller.cambiar_estado_orden(orden_id, nuevo_estado)
        mostrar_exito(f"Orden id {orden['id']} ahora está '{orden['estado']}'.")
    except ValueError as e:
        mostrar_error(str(e))
    pausar()


def _agregar_repuesto() -> None:
    titulo("Agregar Repuesto Usado a una Orden")
    mostrar_tabla("Órdenes", COLUMNAS_ORDENES, taller_controller.listar_ordenes())
    orden_id = pedir_entero("ID de la orden", validador=lambda x: v.validar_entero_positivo(x, "ID"))
    mostrar_tabla(
        "Repuestos disponibles",
        ["id", "nombre", "precio", "stock"],
        repuesto_controller.listar_repuestos(),
    )
    repuesto_id = pedir_entero("ID del repuesto", validador=lambda x: v.validar_entero_positivo(x, "ID"))
    cantidad = pedir_entero("Cantidad usada", validador=lambda x: v.validar_entero_positivo(x, "Cantidad"))
    try:
        taller_controller.agregar_repuesto_a_orden(orden_id, repuesto_id, cantidad)
        mostrar_exito("Repuesto agregado a la orden y stock actualizado.")
    except ValueError as e:
        mostrar_error(str(e))
    pausar()


def _ver_detalle() -> None:
    titulo("Detalle de Orden de Trabajo")
    mostrar_tabla("Órdenes", COLUMNAS_ORDENES, taller_controller.listar_ordenes())
    orden_id = pedir_entero("ID de la orden", validador=lambda x: v.validar_entero_positivo(x, "ID"))
    try:
        detalle = taller_controller.obtener_detalle_orden(orden_id)
        mostrar_tabla(
            "Repuestos usados en la orden",
            ["repuesto_nombre", "cantidad", "precio_unitario"],
            detalle["repuestos"],
        )
        console.print(f"\n[bold]Costo total de la orden:[/bold] {detalle['costo_total']}")
    except ValueError as e:
        mostrar_error(str(e))
    pausar()
