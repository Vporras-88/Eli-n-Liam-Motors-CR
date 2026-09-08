"""Rutas del módulo de Taller Mecánico."""

from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.controllers import cliente_controller, repuesto_controller, taller_controller, usuario_controller
from app.models import cliente as cliente_model
from app.models import orden_trabajo as orden_model
from app.models.orden_trabajo import ESTADOS
from app.utils import validators as v
from app.utils.moneda import MONEDA_POR_DEFECTO, MONEDAS
from app.views.web.auth import requiere_permiso

bp = Blueprint("taller", __name__, url_prefix="/taller")


@bp.route("/")
@requiere_permiso("taller")
def listar():
    estado = request.args.get("estado", "").strip()
    filas = taller_controller.listar_ordenes(estado=estado or None)
    return render_template("taller/listar.html", ordenes=filas, estado=estado, estados=ESTADOS)


@bp.route("/nueva", methods=["GET", "POST"])
@requiere_permiso("taller")
def nueva():
    clientes = cliente_controller.listar_clientes()
    mecanicos = usuario_controller.listar_mecanicos()

    if request.method == "POST":
        datos = request.form
        errores = []
        ok, msg = v.validar_entero_positivo(datos.get("cliente_id", ""), "Cliente")
        if not ok:
            errores.append(msg)
        ok, msg = v.validar_no_vacio(datos.get("moto_marca", ""), "Marca de la moto")
        if not ok:
            errores.append(msg)
        ok, msg = v.validar_no_vacio(datos.get("moto_modelo", ""), "Modelo de la moto")
        if not ok:
            errores.append(msg)
        ok, msg = v.validar_no_vacio(datos.get("descripcion_problema", ""), "Descripción del problema")
        if not ok:
            errores.append(msg)
        ok, msg = v.validar_decimal_no_negativo(datos.get("costo_mano_obra", ""), "Costo de mano de obra")
        if not ok:
            errores.append(msg)
        if errores:
            for e in errores:
                flash(e, "error")
            return render_template("taller/form.html", clientes=clientes, mecanicos=mecanicos, valores=datos)
        try:
            mecanico_id = int(datos["mecanico_id"]) if datos.get("mecanico_id") else None
            orden = taller_controller.crear_orden(
                int(datos["cliente_id"]), datos["moto_marca"], datos["moto_modelo"], datos.get("moto_placa", ""),
                mecanico_id, datos["descripcion_problema"], float(datos["costo_mano_obra"]), _moneda(datos),
            )
            flash(f"Orden de trabajo id {orden['id']} creada con estado '{orden['estado']}'.", "exito")
            return redirect(url_for("taller.detalle", orden_id=orden["id"]))
        except ValueError as e:
            flash(str(e), "error")
            return render_template("taller/form.html", clientes=clientes, mecanicos=mecanicos, valores=datos)

    return render_template("taller/form.html", clientes=clientes, mecanicos=mecanicos, valores={})


@bp.route("/<int:orden_id>")
@requiere_permiso("taller")
def detalle(orden_id):
    try:
        info = taller_controller.obtener_detalle_orden(orden_id)
    except ValueError as e:
        flash(str(e), "error")
        return redirect(url_for("taller.listar"))
    return render_template(
        "taller/detalle.html", orden=info["orden"], repuestos=info["repuestos"], costo_total=info["costo_total"],
        estados=ESTADOS, repuestos_disponibles=repuesto_controller.listar_repuestos(),
    )


@bp.route("/<int:orden_id>/editar", methods=["GET", "POST"])
@requiere_permiso("taller")
def editar(orden_id):
    fila = orden_model.obtener_por_id(orden_id)
    if fila is None:
        flash("La orden indicada no existe.", "error")
        return redirect(url_for("taller.listar"))
    mecanicos = usuario_controller.listar_mecanicos()
    cliente = cliente_model.obtener_por_id(fila["cliente_id"])

    if request.method == "POST":
        datos = request.form
        errores = []
        ok, msg = v.validar_no_vacio(datos.get("moto_marca", ""), "Marca de la moto")
        if not ok:
            errores.append(msg)
        ok, msg = v.validar_no_vacio(datos.get("moto_modelo", ""), "Modelo de la moto")
        if not ok:
            errores.append(msg)
        ok, msg = v.validar_no_vacio(datos.get("descripcion_problema", ""), "Descripción del problema")
        if not ok:
            errores.append(msg)
        ok, msg = v.validar_decimal_no_negativo(datos.get("costo_mano_obra", ""), "Costo de mano de obra")
        if not ok:
            errores.append(msg)
        if errores:
            for e in errores:
                flash(e, "error")
            return render_template("taller/editar.html", orden=fila, cliente=cliente, mecanicos=mecanicos, valores=datos)
        try:
            mecanico_id = int(datos["mecanico_id"]) if datos.get("mecanico_id") else None
            taller_controller.editar_orden(
                orden_id, datos["moto_marca"], datos["moto_modelo"], datos.get("moto_placa", ""),
                mecanico_id, datos["descripcion_problema"], float(datos["costo_mano_obra"]), _moneda(datos),
            )
            flash("Orden actualizada.", "exito")
            return redirect(url_for("taller.detalle", orden_id=orden_id))
        except ValueError as e:
            flash(str(e), "error")
            return render_template("taller/editar.html", orden=fila, cliente=cliente, mecanicos=mecanicos, valores=datos)

    return render_template("taller/editar.html", orden=fila, cliente=cliente, mecanicos=mecanicos, valores=dict(fila))


@bp.route("/<int:orden_id>/eliminar", methods=["POST"])
@requiere_permiso("taller")
def eliminar(orden_id):
    try:
        taller_controller.eliminar_orden(orden_id)
        flash("Orden eliminada. El stock de los repuestos usados fue restituido.", "exito")
    except ValueError as e:
        flash(str(e), "error")
    return redirect(url_for("taller.listar"))


@bp.route("/<int:orden_id>/estado", methods=["POST"])
@requiere_permiso("taller")
def cambiar_estado(orden_id):
    estado = request.form.get("estado", "")
    try:
        taller_controller.cambiar_estado_orden(orden_id, estado)
        flash(f"Orden id {orden_id} ahora está '{estado}'.", "exito")
    except ValueError as e:
        flash(str(e), "error")
    return redirect(url_for("taller.detalle", orden_id=orden_id))


@bp.route("/<int:orden_id>/repuestos", methods=["POST"])
@requiere_permiso("taller")
def agregar_repuesto(orden_id):
    ok, msg = v.validar_entero_positivo(request.form.get("repuesto_id", ""), "Repuesto")
    if ok:
        ok, msg = v.validar_entero_positivo(request.form.get("cantidad", ""), "Cantidad")
    if not ok:
        flash(msg, "error")
        return redirect(url_for("taller.detalle", orden_id=orden_id))
    try:
        taller_controller.agregar_repuesto_a_orden(orden_id, int(request.form["repuesto_id"]), int(request.form["cantidad"]))
        flash("Repuesto agregado a la orden y stock actualizado.", "exito")
    except ValueError as e:
        flash(str(e), "error")
    return redirect(url_for("taller.detalle", orden_id=orden_id))


def _moneda(datos) -> str:
    valor = datos.get("moneda_mano_obra", "").strip()
    return valor if valor in MONEDAS else MONEDA_POR_DEFECTO
