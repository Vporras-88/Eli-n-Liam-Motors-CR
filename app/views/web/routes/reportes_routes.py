"""Ruta del módulo de Reportes básicos."""

from flask import Blueprint, render_template

from app.controllers import repuesto_controller, taller_controller, venta_controller
from app.views.web.auth import requiere_permiso

bp = Blueprint("reportes", __name__, url_prefix="/reportes")


@bp.route("/")
@requiere_permiso("reportes")
def ver():
    ordenes = taller_controller.listar_ordenes()
    abiertas = [o for o in ordenes if o["estado"] != "entregada"]
    entregadas = [o for o in ordenes if o["estado"] == "entregada"]
    return render_template(
        "reportes.html",
        total_ventas=venta_controller.total_ventas(),
        ordenes_abiertas=len(abiertas),
        ordenes_entregadas=len(entregadas),
        stock_bajo=repuesto_controller.listar_stock_bajo(),
    )
