"""Rutas del módulo de Clientes."""

import sqlite3

from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.controllers import cliente_controller, financiera_controller
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
    financieras = financiera_controller.listar_financieras()
    if request.method == "POST":
        datos = request.form
        errores = _validar(datos, requerir_cedula=True)
        if errores:
            for e in errores:
                flash(e, "error")
            return render_template("clientes/form.html", cliente=None, valores=datos, financieras=financieras)
        try:
            cliente = cliente_controller.crear_cliente(
                datos["nombre"], datos["cedula"], datos.get("telefono", ""), datos.get("email", ""), datos.get("direccion", ""),
                _financiera_id(datos), _estado_financiamiento(datos),
            )
            flash(f"Cliente '{cliente['nombre']}' registrado con id {cliente['id']}.", "exito")
            return redirect(url_for("clientes.listar"))
        except ValueError as e:
            flash(str(e), "error")
            return render_template("clientes/form.html", cliente=None, valores=datos, financieras=financieras)
    return render_template("clientes/form.html", cliente=None, valores={}, financieras=financieras)


@bp.route("/<int:cliente_id>/editar", methods=["GET", "POST"])
@requiere_permiso("clientes")
def editar(cliente_id):
    fila = cliente_model.obtener_por_id(cliente_id)
    if fila is None:
        flash("El cliente indicado no existe.", "error")
        return redirect(url_for("clientes.listar"))
    financieras = financiera_controller.listar_financieras()

    if request.method == "POST":
        datos = request.form
        errores = _validar(datos, requerir_cedula=False)
        if errores:
            for e in errores:
                flash(e, "error")
            return render_template("clientes/form.html", cliente=fila, valores=datos, financieras=financieras)
        try:
            cliente_controller.editar_cliente(
                cliente_id, datos["nombre"], datos.get("telefono", ""), datos.get("email", ""), datos.get("direccion", ""),
                _financiera_id(datos), _estado_financiamiento(datos),
            )
            flash("Cliente actualizado.", "exito")
            return redirect(url_for("clientes.listar"))
        except ValueError as e:
            flash(str(e), "error")
            return render_template("clientes/form.html", cliente=fila, valores=datos, financieras=financieras)

    return render_template("clientes/form.html", cliente=fila, valores=dict(fila), financieras=financieras)


@bp.route("/<int:cliente_id>/eliminar", methods=["POST"])
@requiere_permiso("clientes")
def eliminar(cliente_id):
    try:
        cliente_controller.eliminar_cliente(cliente_id)
        flash("Cliente eliminado.", "exito")
    except ValueError as e:
        flash(str(e), "error")
    except sqlite3.IntegrityError:
        flash("No se puede eliminar: el cliente tiene ventas u órdenes de taller asociadas.", "error")
    return redirect(url_for("clientes.listar"))


@bp.route("/financieras")
@requiere_permiso("clientes")
def financieras():
    return render_template("clientes/financieras.html", financieras=financiera_controller.listar_financieras())


@bp.route("/financieras/nueva", methods=["POST"])
@requiere_permiso("clientes")
def nueva_financiera():
    try:
        financiera = financiera_controller.crear_financiera(request.form.get("nombre", ""))
        flash(f"Financiera '{financiera['nombre']}' agregada.", "exito")
    except ValueError as e:
        flash(str(e), "error")
    return redirect(url_for("clientes.financieras"))


@bp.route("/financieras/<int:financiera_id>/eliminar", methods=["POST"])
@requiere_permiso("clientes")
def eliminar_financiera(financiera_id):
    try:
        financiera_controller.eliminar_financiera(financiera_id)
        flash("Financiera eliminada.", "exito")
    except ValueError as e:
        flash(str(e), "error")
    except sqlite3.IntegrityError:
        flash("No se puede eliminar: hay clientes asociados a esta financiera.", "error")
    return redirect(url_for("clientes.financieras"))


def _financiera_id(datos) -> int | None:
    valor = datos.get("financiera_id", "").strip()
    return int(valor) if valor else None


def _estado_financiamiento(datos) -> str | None:
    valor = datos.get("estado_financiamiento", "").strip()
    return valor or None


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
    estado = datos.get("estado_financiamiento", "").strip()
    if estado and estado not in cliente_controller.ESTADOS_FINANCIAMIENTO:
        errores.append("El estado de financiamiento indicado no es válido.")
    return errores
