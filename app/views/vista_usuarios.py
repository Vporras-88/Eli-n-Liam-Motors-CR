"""Vista del módulo de Usuarios (solo accesible para el rol admin)."""

from app.controllers import usuario_controller
from app.models.usuario import ROLES
from app.utils import validators as v
from app.views.cli_helpers import (
    mostrar_error,
    mostrar_exito,
    mostrar_tabla,
    pausar,
    pedir_entero,
    pedir_menu,
    pedir_opcion,
    pedir_texto,
    titulo,
)

COLUMNAS = ["id", "nombre", "usuario", "rol", "activo"]


def _listar(filas) -> None:
    mostrar_tabla("Usuarios", COLUMNAS, filas)


def menu_usuarios() -> None:
    while True:
        opcion = pedir_menu(
            "— Gestión de Usuarios (Admin) —",
            {
                "1": "Listar usuarios",
                "2": "Crear usuario",
                "3": "Editar usuario (nombre/rol)",
                "4": "Cambiar contraseña de un usuario",
                "5": "Activar/Desactivar usuario",
                "0": "Volver al menú principal",
            },
        )
        if opcion == "1":
            titulo("Listado de Usuarios")
            _listar(usuario_controller.listar_usuarios())
            pausar()
        elif opcion == "2":
            _crear_usuario()
        elif opcion == "3":
            _editar_usuario()
        elif opcion == "4":
            _cambiar_password()
        elif opcion == "5":
            _activar_desactivar()
        elif opcion == "0":
            return


def _crear_usuario() -> None:
    titulo("Crear Usuario")
    nombre = pedir_texto("Nombre completo")
    usuario = pedir_texto("Nombre de usuario")
    password = pedir_texto("Contraseña")
    rol = pedir_opcion("Rol", list(ROLES))
    try:
        nuevo = usuario_controller.crear_usuario(nombre, usuario, password, rol)
        mostrar_exito(f"Usuario '{nuevo['usuario']}' creado con id {nuevo['id']} y rol '{nuevo['rol']}'.")
    except ValueError as e:
        mostrar_error(str(e))
    pausar()


def _editar_usuario() -> None:
    titulo("Editar Usuario")
    _listar(usuario_controller.listar_usuarios())
    usuario_id = pedir_entero("ID del usuario", validador=lambda x: v.validar_entero_positivo(x, "ID"))
    nombre = pedir_texto("Nuevo nombre")
    rol = pedir_opcion("Nuevo rol", list(ROLES))
    try:
        usuario = usuario_controller.editar_usuario(usuario_id, nombre, rol)
        mostrar_exito(f"Usuario id {usuario['id']} actualizado.")
    except ValueError as e:
        mostrar_error(str(e))
    pausar()


def _cambiar_password() -> None:
    titulo("Cambiar Contraseña")
    _listar(usuario_controller.listar_usuarios())
    usuario_id = pedir_entero("ID del usuario", validador=lambda x: v.validar_entero_positivo(x, "ID"))
    password_nueva = pedir_texto("Nueva contraseña")
    try:
        usuario_controller.cambiar_password(usuario_id, password_nueva)
        mostrar_exito("Contraseña actualizada.")
    except ValueError as e:
        mostrar_error(str(e))
    pausar()


def _activar_desactivar() -> None:
    titulo("Activar/Desactivar Usuario")
    _listar(usuario_controller.listar_usuarios())
    usuario_id = pedir_entero("ID del usuario", validador=lambda x: v.validar_entero_positivo(x, "ID"))
    activo = pedir_opcion("Nuevo estado", ["activo", "inactivo"]) == "activo"
    try:
        usuario = usuario_controller.activar_desactivar(usuario_id, activo)
        estado_txt = "activo" if usuario["activo"] else "inactivo"
        mostrar_exito(f"Usuario id {usuario['id']} ahora está {estado_txt}.")
    except ValueError as e:
        mostrar_error(str(e))
    pausar()
