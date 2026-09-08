"""Rutas del módulo de Usuarios (solo accesible para el rol admin)."""

from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.controllers import usuario_controller
from app.models import usuario as usuario_model
from app.models.usuario import ROLES
from app.utils import validators as v
from app.views.web.auth import requiere_permiso

bp = Blueprint("usuarios", __name__, url_prefix="/usuarios")


@bp.route("/")
@requiere_permiso("usuarios")
def listar():
    return render_template("usuarios/listar.html", usuarios=usuario_controller.listar_usuarios())


@bp.route("/nuevo", methods=["GET", "POST"])
@requiere_permiso("usuarios")
def nuevo():
    if request.method == "POST":
        datos = request.form
        errores = []
        ok, msg = v.validar_no_vacio(datos.get("nombre", ""), "Nombre")
        if not ok:
            errores.append(msg)
        ok, msg = v.validar_no_vacio(datos.get("usuario", ""), "Nombre de usuario")
        if not ok:
            errores.append(msg)
        ok, msg = v.validar_no_vacio(datos.get("password", ""), "Contraseña")
        if not ok:
            errores.append(msg)
        if errores:
            for e in errores:
                flash(e, "error")
            return render_template("usuarios/form.html", usuario=None, valores=datos, roles=ROLES)
        try:
            nuevo_usuario = usuario_controller.crear_usuario(datos["nombre"], datos["usuario"], datos["password"], datos["rol"])
            flash(f"Usuario '{nuevo_usuario['usuario']}' creado con id {nuevo_usuario['id']}.", "exito")
            return redirect(url_for("usuarios.listar"))
        except ValueError as e:
            flash(str(e), "error")
            return render_template("usuarios/form.html", usuario=None, valores=datos, roles=ROLES)
    return render_template("usuarios/form.html", usuario=None, valores={}, roles=ROLES)


@bp.route("/<int:usuario_id>/editar", methods=["GET", "POST"])
@requiere_permiso("usuarios")
def editar(usuario_id):
    fila = usuario_model.obtener_por_id(usuario_id)
    if fila is None:
        flash("El usuario indicado no existe.", "error")
        return redirect(url_for("usuarios.listar"))

    if request.method == "POST":
        datos = request.form
        ok, msg = v.validar_no_vacio(datos.get("nombre", ""), "Nombre")
        if not ok:
            flash(msg, "error")
            return render_template("usuarios/form.html", usuario=fila, valores=datos, roles=ROLES)
        try:
            usuario_controller.editar_usuario(usuario_id, datos["nombre"], datos["rol"])
            flash("Usuario actualizado.", "exito")
            return redirect(url_for("usuarios.listar"))
        except ValueError as e:
            flash(str(e), "error")
            return render_template("usuarios/form.html", usuario=fila, valores=datos, roles=ROLES)

    return render_template("usuarios/form.html", usuario=fila, valores=dict(fila), roles=ROLES)


@bp.route("/<int:usuario_id>/password", methods=["POST"])
@requiere_permiso("usuarios")
def cambiar_password(usuario_id):
    password_nueva = request.form.get("password_nueva", "")
    ok, msg = v.validar_no_vacio(password_nueva, "Contraseña")
    if not ok:
        flash(msg, "error")
        return redirect(url_for("usuarios.listar"))
    try:
        usuario_controller.cambiar_password(usuario_id, password_nueva)
        flash("Contraseña actualizada.", "exito")
    except ValueError as e:
        flash(str(e), "error")
    return redirect(url_for("usuarios.listar"))


@bp.route("/<int:usuario_id>/estado", methods=["POST"])
@requiere_permiso("usuarios")
def cambiar_estado(usuario_id):
    activo = request.form.get("activo") == "1"
    try:
        usuario = usuario_controller.activar_desactivar(usuario_id, activo)
        estado_txt = "activo" if usuario["activo"] else "inactivo"
        flash(f"Usuario id {usuario['id']} ahora está {estado_txt}.", "exito")
    except ValueError as e:
        flash(str(e), "error")
    return redirect(url_for("usuarios.listar"))
