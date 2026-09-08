"""Autenticación y control de acceso para la Vista web (sesión de Flask)."""

from functools import wraps

from flask import flash, redirect, session, url_for

from app.controllers import auth_controller
from app.models import usuario as usuario_model


def usuario_actual():
    """Devuelve la fila del usuario en sesión, o None si no hay sesión activa."""
    usuario_id = session.get("usuario_id")
    if usuario_id is None:
        return None
    return usuario_model.obtener_por_id(usuario_id)


def login_requerido(vista):
    @wraps(vista)
    def envoltura(*args, **kwargs):
        if usuario_actual() is None:
            flash("Debe iniciar sesión para continuar.", "error")
            return redirect(url_for("auth.login"))
        return vista(*args, **kwargs)

    return envoltura


def requiere_permiso(clave: str):
    """Exige sesión activa y que el rol del usuario tenga acceso a `clave`."""

    def decorador(vista):
        @wraps(vista)
        @login_requerido
        def envoltura(*args, **kwargs):
            if not auth_controller.puede_acceder(usuario_actual(), clave):
                flash("No tiene permisos para acceder a esa sección.", "error")
                return redirect(url_for("principal.index"))
            return vista(*args, **kwargs)

        return envoltura

    return decorador
