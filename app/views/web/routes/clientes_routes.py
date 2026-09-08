"""Rutas del módulo de Clientes."""

from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.controllers import cliente_controller
from app.models import cliente as cliente_model
from app.utils import validators as v
from app.views.web.auth import requiere_permiso

bp = Blueprint("clientes", __name__, url_prefix="/clientes")


@bp.route("/")
@requiere_permiso("clientes")
def listar():
    texto = request.args.get("q", "").strip()
    filas = cliente_controller.buscar_clientes(texto) if texto else cliente_controller.listar_clientes()
    return render_template("clientes/listar.html", clientes=filas, q=texto)


@bp.route("/nuevo", methods=["GET", "POST"])
@requiere_permiso("clientes")
def nuevo():
    if request.method == "POST":
        datos = request.form
        errores = _validar(datos, requerir_cedula=True)
        if errores:
            for e in errores:
                flash(e, "error")
            return render_template("clientes/form.html", cliente=None, valores=datos)
        try:
            cliente = cliente_controller.crear_cliente(
                datos["nombre"], datos["cedula"], datos.get("telefono", ""), datos.get("email", ""), datos.get("direccion", "")
            )
            flash(f"Cliente '{cliente['nombre']}' registrado con id {cliente['id']}.", "exito")
            return redirect(url_for("clientes.listar"))
        except ValueError as e:
            flash(str(e), "error")
            return render_template("clientes/form.html", cliente=None, valores=datos)
    return render_template("clientes/form.html", cliente=None, valores={})


@bp.route("/<int:cliente_id>/editar", methods=["GET", "POST"])
@requiere_permiso("clientes")
def editar(cliente_id):
    fila = cliente_model.obtener_por_id(cliente_id)
    if fila is None:
        flash("El cliente indicado no existe.", "error")
        return redirect(url_for("clientes.listar"))

    if request.method == "POST":
        datos = request.form
        errores = _validar(datos, requerir_cedula=False)
        if errores:
            for e in errores:
                flash(e, "error")
            return render_template("clientes/form.html", cliente=fila, valores=datos)
        try:
            cliente_controller.editar_cliente(
                cliente_id, datos["nombre"], datos.get("telefono", ""), datos.get("email", ""), datos.get("direccion", "")
            )
            flash("Cliente actualizado.", "exito")
            return redirect(url_for("clientes.listar"))
        except ValueError as e:
            flash(str(e), "error")
            return render_template("clientes/form.html", cliente=fila, valores=datos)

    return render_template("clientes/form.html", cliente=fila, valores=fila)


def _validar(datos, requerir_cedula: bool) -> list[str]:
    errores = []
    ok, msg = v.validar_no_vacio(datos.get("nombre", ""), "Nombre")
    if not ok:
        errores.append(msg)
    if requerir_cedula:
        ok, msg = v.validar_cedula(datos.get("cedula", ""))
        if not ok:
            errores.append(msg)
    ok, msg = v.validar_telefono(datos.get("telefono", ""))
    if not ok:
        errores.append(msg)
    ok, msg = v.validar_email(datos.get("email", ""))
    if not ok:
        errores.append(msg)
    return errores
