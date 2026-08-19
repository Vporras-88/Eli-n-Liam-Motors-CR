"""Rutas de autenticación: login/logout."""

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from app.controllers import auth_controller
from app.views.web.auth import usuario_actual

bp = Blueprint("auth", __name__)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if usuario_actual() is not None:
        return redirect(url_for("principal.index"))

    if request.method == "POST":
        usuario = request.form.get("usuario", "")
        password = request.form.get("password", "")
        fila = auth_controller.login(usuario, password)
        if fila is None:
            flash("Usuario o contraseña incorrectos, o el usuario está inactivo.", "error")
            return render_template("login.html")
        session["usuario_id"] = fila["id"]
        flash(f"Bienvenido/a, {fila['nombre']} ({fila['rol']}).", "exito")
        return redirect(url_for("principal.index"))

    return render_template("login.html")


@bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("Sesión cerrada.", "exito")
    return redirect(url_for("auth.login"))
