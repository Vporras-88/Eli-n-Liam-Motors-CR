"""Rutas del módulo de Inventario de Motocicletas."""

import sqlite3

from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.controllers import inventario_controller
from app.models import motocicleta as moto_model
from app.models.motocicleta import ESTADOS
from app.utils import validators as v
from app.views.web.auth import requiere_permiso

bp = Blueprint("inventario", __name__, url_prefix="/inventario")


@bp.route("/")
@requiere_permiso("inventario")
def listar():
    texto = request.args.get("q", "").strip()
    estado = request.args.get("estado", "").strip()
    if texto:
        filas = inventario_controller.buscar_motos(texto)
    else:
        filas = inventario_controller.listar_motos(estado=estado or None)
    return render_template("inventario/listar.html", motos=filas, q=texto, estado=estado, estados=ESTADOS)


@bp.route("/nuevo", methods=["GET", "POST"])
@requiere_permiso("inventario")
def nuevo():
    if request.method == "POST":
        datos = request.form
        errores = _validar(datos)
        if errores:
            for e in errores:
                flash(e, "error")
            return render_template("inventario/form.html", moto=None, valores=datos)
        try:
            moto = inventario_controller.crear_moto(
                datos["marca"], datos["modelo"], int(datos["anio"]), datos.get("color", ""),
                int(datos["cilindraje"]), datos["vin"], float(datos["precio"]),
            )
            flash(f"Motocicleta {moto['marca']} {moto['modelo']} registrada con id {moto['id']}.", "exito")
            return redirect(url_for("inventario.listar"))
        except ValueError as e:
            flash(str(e), "error")
            return render_template("inventario/form.html", moto=None, valores=datos)
    return render_template("inventario/form.html", moto=None, valores={})


@bp.route("/<int:moto_id>/editar", methods=["GET", "POST"])
@requiere_permiso("inventario")
def editar(moto_id):
    fila = moto_model.obtener_por_id(moto_id)
    if fila is None:
        flash("La motocicleta indicada no existe.", "error")
        return redirect(url_for("inventario.listar"))

    if request.method == "POST":
        datos = request.form
        errores = _validar(datos, requerir_vin=False)
        if errores:
            for e in errores:
                flash(e, "error")
            return render_template("inventario/form.html", moto=fila, valores=datos)
        try:
            inventario_controller.editar_moto(
                moto_id, datos["marca"], datos["modelo"], int(datos["anio"]), datos.get("color", ""),
                int(datos["cilindraje"]), float(datos["precio"]),
            )
            flash("Motocicleta actualizada.", "exito")
            return redirect(url_for("inventario.listar"))
        except ValueError as e:
            flash(str(e), "error")
            return render_template("inventario/form.html", moto=fila, valores=datos)

    return render_template("inventario/form.html", moto=fila, valores=dict(fila))


@bp.route("/<int:moto_id>/estado", methods=["POST"])
@requiere_permiso("inventario")
def cambiar_estado(moto_id):
    estado = request.form.get("estado", "")
    try:
        moto = inventario_controller.cambiar_estado_moto(moto_id, estado)
        flash(f"Motocicleta id {moto['id']} ahora está '{moto['estado']}'.", "exito")
    except ValueError as e:
        flash(str(e), "error")
    return redirect(url_for("inventario.listar"))


@bp.route("/<int:moto_id>/eliminar", methods=["POST"])
@requiere_permiso("inventario")
def eliminar(moto_id):
    try:
        inventario_controller.eliminar_moto(moto_id)
        flash("Motocicleta eliminada.", "exito")
    except ValueError as e:
        flash(str(e), "error")
    except sqlite3.IntegrityError:
        flash("No se puede eliminar: la motocicleta tiene ventas asociadas.", "error")
    return redirect(url_for("inventario.listar"))


def _validar(datos, requerir_vin: bool = True) -> list[str]:
    errores = []
    for campo, etiqueta in (("marca", "Marca"), ("modelo", "Modelo")):
        ok, msg = v.validar_no_vacio(datos.get(campo, ""), etiqueta)
        if not ok:
            errores.append(msg)
    ok, msg = v.validar_anio(datos.get("anio", ""))
    if not ok:
        errores.append(msg)
    ok, msg = v.validar_entero_positivo(datos.get("cilindraje", ""), "Cilindraje")
    if not ok:
        errores.append(msg)
    ok, msg = v.validar_decimal_positivo(datos.get("precio", ""), "Precio")
    if not ok:
        errores.append(msg)
    if requerir_vin:
        ok, msg = v.validar_no_vacio(datos.get("vin", ""), "VIN")
        if not ok:
            errores.append(msg)
    return errores
