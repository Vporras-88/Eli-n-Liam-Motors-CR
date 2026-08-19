"""Ruta del dashboard principal."""

from flask import Blueprint, render_template

from app.views.web.auth import login_requerido, usuario_actual
from app.views.web.nav import opciones_visibles

bp = Blueprint("principal", __name__)


@bp.route("/")
@login_requerido
def index():
    usuario = usuario_actual()
    return render_template("principal.html", opciones=opciones_visibles(usuario))
