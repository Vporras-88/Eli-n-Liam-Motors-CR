"""Punto de entrada de la aplicación: Elián-Liam Motors CR.

Ejecutar con:  uv run main.py
"""

from app.models.database import init_db
from app.views import vista_auth, vista_principal
from app.views.cli_helpers import console


def main() -> None:
    init_db()
    console.print("[bold cyan]═══ Elián-Liam Motors CR — Agencia Multimarca de Motocicletas ═══[/bold cyan]")

    while True:
        usuario_actual = vista_auth.iniciar_sesion()
        if usuario_actual is None:
            console.print("\n[bold]¡Hasta pronto![/bold]")
            break
        vista_principal.menu_principal(usuario_actual)


if __name__ == "__main__":
    main()
