"""Definición del menú de navegación web, filtrado por rol."""

from app.controllers import auth_controller

# (clave de permiso, etiqueta de menú, endpoint del blueprint)
OPCIONES_MENU = [
    ("inventario", "Inventario", "inventario.listar"),
    ("clientes", "Clientes", "clientes.listar"),
    ("ventas", "Venta de Motocicletas", "ventas.listar"),
    ("repuestos", "Repuestos y Accesorios", "repuestos.listar"),
    ("ventas_repuestos", "Venta de Repuestos y Accesorios", "ventas_repuestos.listar"),
    ("taller", "Taller Mecánico", "taller.listar"),
    ("reportes", "Reportes", "reportes.ver"),
    ("usuarios", "Usuarios", "usuarios.listar"),
]


def opciones_visibles(usuario):
    if usuario is None:
        return []
    return [(clave, etiqueta, endpoint) for clave, etiqueta, endpoint in OPCIONES_MENU if auth_controller.puede_acceder(usuario, clave)]
