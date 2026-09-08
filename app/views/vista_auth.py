"""Vista de autenticación (login)."""

import sqlite3

from app.controllers import auth_controller
from app.views.cli_helpers import console, mostrar_error, mostrar_exito, titulo


def iniciar_sesion() -> sqlite3.Row | None:
    """Pide usuario/contraseña hasta lograr un login válido, o None si el usuario escribe 'salir'."""
    titulo("Elián-Liam Motors CR — Inicio de sesión")
    while True:
        usuario = console.input("[cyan]Usuario (o 'salir' para terminar): [/cyan]").strip()
        if usuario.lower() == "salir":
            return None
        password = console.input("[cyan]Contraseña: [/cyan]", password=True).strip()
        fila = auth_controller.login(usuario, password)
        if fila is None:
            mostrar_error("Usuario o contraseña incorrectos, o el usuario está inactivo.")
            continue
        mostrar_exito(f"Bienvenido/a, {fila['nombre']} ({fila['rol']}).")
        return fila
