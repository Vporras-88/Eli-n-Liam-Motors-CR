"""Punto de entrada de la versión web: Elián-Liam Motors CR.

Ejecutar con:  uv run webapp.py
"""

import secrets

from flask import Flask

from app.models.database import init_db
from app.views.web.auth import usuario_actual
from app.views.web.nav import opciones_visibles


def crear_app() -> Flask:
    app = Flask(__name__, template_folder="app/views/web/templates", static_folder="app/views/web/static")
    app.secret_key = secrets.token_hex(32)

    init_db()

    from app.views.web.routes.auth_routes import bp as auth_bp
    from app.views.web.routes.clientes_routes import bp as clientes_bp
    from app.views.web.routes.inventario_routes import bp as inventario_bp
    from app.views.web.routes.principal_routes import bp as principal_bp
    from app.views.web.routes.repuestos_routes import bp as repuestos_bp
    from app.views.web.routes.reportes_routes import bp as reportes_bp
    from app.views.web.routes.taller_routes import bp as taller_bp
    from app.views.web.routes.usuarios_routes import bp as usuarios_bp
    from app.views.web.routes.ventas_routes import bp as ventas_bp
    from app.views.web.routes.ventas_repuestos_routes import bp as ventas_repuestos_bp

    for bp in (
        auth_bp, principal_bp, clientes_bp, inventario_bp, ventas_bp, ventas_repuestos_bp,
        repuestos_bp, taller_bp, usuarios_bp, reportes_bp,
    ):
        app.register_blueprint(bp)

    @app.context_processor
    def inyectar_contexto():
        usuario = usuario_actual()
        return {"usuario": usuario, "opciones_menu": opciones_visibles(usuario)}

    return app


app = crear_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
