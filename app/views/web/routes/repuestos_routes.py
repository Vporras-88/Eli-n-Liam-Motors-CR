"""Rutas del módulo de Repuestos y Accesorios."""

import sqlite3

from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.controllers import repuesto_controller
from app.models import repuesto as repuesto_model
from app.models.repuesto import CATEGORIAS
from app.utils import validators as v
from app.utils.moneda import MONEDA_POR_DEFECTO, MONEDAS
from app.views.web.auth import requiere_permiso

bp = Blueprint("repuestos", __name__, url_prefix="/repuestos")


@bp.route("/")
@requiere_permiso("repuestos")
def listar():
    solo_bajo = request.args.get("stock_bajo") == "1"
    filas = repuesto_controller.listar_stock_bajo() if solo_bajo else repuesto_controller.listar_repuestos()
    return render_template("repuestos/listar.html", repuestos=filas, solo_bajo=solo_bajo)


@bp.route("/nuevo", methods=["GET", "POST"])
@requiere_permiso("repuestos")
def nuevo():
    if request.method == "POST":
        datos = request.form
        errores = _validar(datos)
        if errores:
            for e in errores:
                flash(e, "error")
            return render_template("repuestos/form.html", repuesto=None, valores=datos, categorias=CATEGORIAS)
        try:
            repuesto = repuesto_controller.crear_repuesto(
                datos["nombre"], datos["categoria"], datos.get("marca_compatible", ""),
                float(datos["precio"]), int(datos["stock"]), datos.get("proveedor", ""), _moneda(datos),
            )
            flash(f"'{repuesto['nombre']}' registrado con id {repuesto['id']}.", "exito")
            return redirect(url_for("repuestos.listar"))
        except ValueError as e:
            flash(str(e), "error")
            return render_template("repuestos/form.html", repuesto=None, valores=datos, categorias=CATEGORIAS)
    return render_template("repuestos/form.html", repuesto=None, valores={}, categorias=CATEGORIAS)


@bp.route("/<int:repuesto_id>/editar", methods=["GET", "POST"])
@requiere_permiso("repuestos")
def editar(repuesto_id):
    fila = repuesto_model.obtener_por_id(repuesto_id)
    if fila is None:
        flash("El repuesto indicado no existe.", "error")
        return redirect(url_for("repuestos.listar"))

    if request.method == "POST":
        datos = request.form
        errores = _validar(datos, requerir_categoria_stock=False)
        if errores:
            for e in errores:
                flash(e, "error")
            return render_template("repuestos/form.html", repuesto=fila, valores=datos, categorias=CATEGORIAS)
        try:
            repuesto_controller.editar_repuesto(
                repuesto_id, datos["nombre"], datos.get("marca_compatible", ""), float(datos["precio"]),
                datos.get("proveedor", ""), _moneda(datos),
            )
            flash("Repuesto actualizado.", "exito")
            return redirect(url_for("repuestos.listar"))
        except ValueError as e:
            flash(str(e), "error")
            return render_template("repuestos/form.html", repuesto=fila, valores=datos, categorias=CATEGORIAS)

    return render_template("repuestos/form.html", repuesto=fila, valores=dict(fila), categorias=CATEGORIAS)


@bp.route("/<int:repuesto_id>/stock", methods=["POST"])
@requiere_permiso("repuestos")
def mover_stock(repuesto_id):
    tipo = request.form.get("tipo", "")
    ok, msg = v.validar_entero_positivo(request.form.get("cantidad", ""), "Cantidad")
    if not ok:
        flash(msg, "error")
        return redirect(url_for("repuestos.listar"))
    cantidad = int(request.form["cantidad"])
    try:
        if tipo == "entrada":
            repuesto = repuesto_controller.registrar_entrada_stock(repuesto_id, cantidad)
        else:
            repuesto = repuesto_controller.registrar_salida_stock(repuesto_id, cantidad)
        flash(f"Stock de '{repuesto['nombre']}' actualizado a {repuesto['stock']} unidades.", "exito")
    except ValueError as e:
        flash(str(e), "error")
    return redirect(url_for("repuestos.listar"))


@bp.route("/<int:repuesto_id>/eliminar", methods=["POST"])
@requiere_permiso("repuestos")
def eliminar(repuesto_id):
    try:
        repuesto_controller.eliminar_repuesto(repuesto_id)
        flash("Repuesto eliminado.", "exito")
    except ValueError as e:
        flash(str(e), "error")
    except sqlite3.IntegrityError:
        flash("No se puede eliminar: el repuesto tiene ventas u órdenes de taller asociadas.", "error")
    return redirect(url_for("repuestos.listar"))


def _moneda(datos) -> str:
    valor = datos.get("moneda", "").strip()
    return valor if valor in MONEDAS else MONEDA_POR_DEFECTO


def _validar(datos, requerir_categoria_stock: bool = True) -> list[str]:
    errores = []
    ok, msg = v.validar_no_vacio(datos.get("nombre", ""), "Nombre")
    if not ok:
        errores.append(msg)
    ok, msg = v.validar_decimal_positivo(datos.get("precio", ""), "Precio")
    if not ok:
        errores.append(msg)
    if requerir_categoria_stock:
        if datos.get("categoria") not in CATEGORIAS:
            errores.append(f"Categoría inválida. Debe ser una de: {', '.join(CATEGORIAS)}.")
        ok, msg = v.validar_entero_no_negativo(datos.get("stock", ""), "Stock")
        if not ok:
            errores.append(msg)
    return errores
