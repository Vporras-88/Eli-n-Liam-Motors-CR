"""Rutas del módulo de Ventas."""

from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.controllers import cliente_controller, inventario_controller, venta_controller
from app.models import venta as venta_model
from app.utils import validators as v
from app.utils.moneda import MONEDA_POR_DEFECTO, MONEDAS
from app.views.web.auth import requiere_permiso, usuario_actual

bp = Blueprint("ventas", __name__, url_prefix="/ventas")


@bp.route("/")
@requiere_permiso("ventas")
def listar():
    return render_template("ventas/listar.html", ventas=venta_controller.listar_ventas())


@bp.route("/nueva", methods=["GET", "POST"])
@requiere_permiso("ventas")
def nueva():
    disponibles = inventario_controller.listar_disponibles()
    clientes = cliente_controller.listar_clientes()

    if request.method == "POST":
        datos = request.form
        errores = []
        ok, msg = v.validar_entero_positivo(datos.get("moto_id", ""), "Motocicleta")
        if not ok:
            errores.append(msg)
        ok, msg = v.validar_entero_positivo(datos.get("cliente_id", ""), "Cliente")
        if not ok:
            errores.append(msg)
        ok, msg = v.validar_decimal_positivo(datos.get("precio_final", ""), "Precio final")
        if not ok:
            errores.append(msg)
        if errores:
            for e in errores:
                flash(e, "error")
            return render_template("ventas/form.html", motos=disponibles, clientes=clientes, metodos=venta_controller.METODOS_PAGO, valores=datos)
        try:
            venta = venta_controller.registrar_venta(
                int(datos["moto_id"]), int(datos["cliente_id"]), usuario_actual()["id"],
                float(datos["precio_final"]), datos.get("metodo_pago", ""), _moneda(datos),
            )
            flash(f"Venta registrada: {venta['marca']} {venta['modelo']} a {venta['cliente_nombre']} por {venta['precio_final']}.", "exito")
            return redirect(url_for("ventas.listar"))
        except ValueError as e:
            flash(str(e), "error")
            return render_template("ventas/form.html", motos=disponibles, clientes=clientes, metodos=venta_controller.METODOS_PAGO, valores=datos)

    return render_template("ventas/form.html", motos=disponibles, clientes=clientes, metodos=venta_controller.METODOS_PAGO, valores={})


@bp.route("/<int:venta_id>/editar", methods=["GET", "POST"])
@requiere_permiso("ventas")
def editar(venta_id):
    fila = venta_model.obtener_por_id(venta_id)
    if fila is None:
        flash("La venta indicada no existe.", "error")
        return redirect(url_for("ventas.listar"))

    if request.method == "POST":
        datos = request.form
        errores = []
        ok, msg = v.validar_decimal_positivo(datos.get("precio_final", ""), "Precio final")
        if not ok:
            errores.append(msg)
        if errores:
            for e in errores:
                flash(e, "error")
            return render_template("ventas/editar.html", venta=fila, metodos=venta_controller.METODOS_PAGO, valores=datos)
        try:
            venta_controller.editar_venta(venta_id, float(datos["precio_final"]), datos.get("metodo_pago", ""), _moneda(datos))
            flash("Venta actualizada.", "exito")
            return redirect(url_for("ventas.listar"))
        except ValueError as e:
            flash(str(e), "error")
            return render_template("ventas/editar.html", venta=fila, metodos=venta_controller.METODOS_PAGO, valores=datos)

    return render_template("ventas/editar.html", venta=fila, metodos=venta_controller.METODOS_PAGO, valores=dict(fila))


@bp.route("/<int:venta_id>/eliminar", methods=["POST"])
@requiere_permiso("ventas")
def eliminar(venta_id):
    try:
        venta_controller.eliminar_venta(venta_id)
        flash("Venta eliminada. La motocicleta vuelve a estar disponible.", "exito")
    except ValueError as e:
        flash(str(e), "error")
    return redirect(url_for("ventas.listar"))


def _moneda(datos) -> str:
    valor = datos.get("moneda", "").strip()
    return valor if valor in MONEDAS else MONEDA_POR_DEFECTO
