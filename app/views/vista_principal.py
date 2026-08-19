"""Vista del menú principal: enruta a cada módulo según el rol del usuario."""

import sqlite3

from app.controllers import auth_controller, repuesto_controller, taller_controller, venta_controller
from app.views import (
    vista_clientes,
    vista_inventario,
    vista_repuestos,
    vista_taller,
    vista_usuarios,
    vista_ventas,
)
from app.views.cli_helpers import console, mostrar_tabla, pausar, pedir_texto, titulo

# (clave de permiso, etiqueta de menú)
OPCIONES_MENU = [
    ("inventario", "Inventario de Motocicletas"),
    ("clientes", "Clientes"),
    ("ventas", "Ventas"),
    ("repuestos", "Repuestos y Accesorios"),
    ("taller", "Taller Mecánico"),
    ("reportes", "Reportes"),
    ("usuarios", "Usuarios (Admin)"),
]


def menu_principal(usuario_actual: sqlite3.Row) -> None:
    """Bucle del menú principal para la sesión actual. Retorna al cerrar sesión."""
    while True:
        disponibles = [(clave, etiqueta) for clave, etiqueta in OPCIONES_MENU if auth_controller.puede_acceder(usuario_actual, clave)]

        titulo(f"Menú Principal — {usuario_actual['nombre']} ({usuario_actual['rol']})")
        for i, (_, etiqueta) in enumerate(disponibles, start=1):
            console.print(f"  [cyan]{i}[/cyan]. {etiqueta}")
        console.print("  [cyan]0[/cyan]. Cerrar sesión")

        eleccion = pedir_texto("Seleccione una opción")
        if eleccion == "0":
            return
        if not eleccion.isdigit() or not (1 <= int(eleccion) <= len(disponibles)):
            continue

        clave, _ = disponibles[int(eleccion) - 1]
        _despachar(clave, usuario_actual)


def _despachar(clave: str, usuario_actual: sqlite3.Row) -> None:
    if clave == "inventario":
        vista_inventario.menu_inventario()
    elif clave == "clientes":
        vista_clientes.menu_clientes()
    elif clave == "ventas":
        vista_ventas.menu_ventas(usuario_actual)
    elif clave == "repuestos":
        vista_repuestos.menu_repuestos()
    elif clave == "taller":
        vista_taller.menu_taller()
    elif clave == "reportes":
        _ver_reportes()
    elif clave == "usuarios":
        vista_usuarios.menu_usuarios()


def _ver_reportes() -> None:
    titulo("Reportes")
    total = venta_controller.total_ventas()
    console.print(f"[bold]Total vendido (histórico):[/bold] {total}")

    ordenes_abiertas = [o for o in taller_controller.listar_ordenes() if o["estado"] != "entregada"]
    ordenes_cerradas = [o for o in taller_controller.listar_ordenes() if o["estado"] == "entregada"]
    console.print(f"[bold]Órdenes de taller abiertas:[/bold] {len(ordenes_abiertas)}")
    console.print(f"[bold]Órdenes de taller entregadas:[/bold] {len(ordenes_cerradas)}")

    mostrar_tabla(
        "Repuestos con stock bajo",
        ["id", "nombre", "stock"],
        repuesto_controller.listar_stock_bajo(),
    )
    pausar()
