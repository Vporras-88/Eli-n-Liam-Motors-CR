"""Rutas del módulo de Ventas de Repuestos y Accesorios."""

from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.controllers import cliente_controller, repuesto_controller, venta_repuesto_controller
from app.utils import validators as v
from app.views.web.auth import requiere_permiso, usuario_actual

bp = Blueprint("ventas_repuestos", __name__, url_prefix="/ventas-repuestos")


@bp.route("/")
@requiere_permiso("ventas_repuestos")
def listar():
    return render_template("ventas_repuestos/listar.html", ventas=venta_repuesto_controller.listar_ventas())


@bp.route("/nueva", methods=["GET", "POST"])
@requiere_permiso("ventas_repuestos")
def nueva():
    disponibles = [r for r in repuesto_controller.listar_repuestos() if r["stock"] > 0]
    clientes = cliente_controller.listar_clientes()

    if request.method == "POST":
        datos = request.form
        errores = []
        ok, msg = v.validar_entero_positivo(datos.get("repuesto_id", ""), "Repuesto/Accesorio")
        if not ok:
            errores.append(msg)
        ok, msg = v.validar_entero_positivo(datos.get("cliente_id", ""), "Cliente")
        if not ok:
            errores.append(msg)
        ok, msg = v.validar_entero_positivo(datos.get("cantidad", ""), "Cantidad")
        if not ok:
            errores.append(msg)
        ok, msg = v.validar_decimal_positivo(datos.get("precio_unitario", ""), "Precio unitario")
        if not ok:
            errores.append(msg)
        if errores:
            for e in errores:
                flash(e, "error")
            return render_template(
                "ventas_repuestos/form.html",
                repuestos=disponibles, clientes=clientes, metodos=venta_repuesto_controller.METODOS_PAGO, valores=datos,
            )
        try:
            venta = venta_repuesto_controller.registrar_venta(
                int(datos["repuesto_id"]), int(datos["cliente_id"]), usuario_actual()["id"],
                int(datos["cantidad"]), float(datos["precio_unitario"]), datos.get("metodo_pago", ""),
            )
            flash(
                f"Venta registrada: {venta['cantidad']} x {venta['repuesto_nombre']} a {venta['cliente_nombre']}.",
                "exito",
            )
            return redirect(url_for("ventas_repuestos.listar"))
        except ValueError as e:
            flash(str(e), "error")
            return render_template(
                "ventas_repuestos/form.html",
                repuestos=disponibles, clientes=clientes, metodos=venta_repuesto_controller.METODOS_PAGO, valores=datos,
            )

    return render_template(
        "ventas_repuestos/form.html",
        repuestos=disponibles, clientes=clientes, metodos=venta_repuesto_controller.METODOS_PAGO, valores={},
    )
