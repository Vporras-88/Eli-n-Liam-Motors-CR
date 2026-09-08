"""Utilidades de entrada/salida por consola compartidas por todas las vistas.

Esta capa NO contiene lógica de negocio: solo pide datos, valida su formato
básico (mediante funciones de `app.utils.validators`) y muestra resultados.
"""

from rich.console import Console
from rich.table import Table

console = Console()


def titulo(texto: str) -> None:
    console.print()
    console.rule(f"[bold cyan]{texto}[/bold cyan]")


def mostrar_error(mensaje: str) -> None:
    console.print(f"[bold red]✗ {mensaje}[/bold red]")


def mostrar_exito(mensaje: str) -> None:
    console.print(f"[bold green]✓ {mensaje}[/bold green]")


def mostrar_info(mensaje: str) -> None:
    console.print(f"[bold yellow]ℹ {mensaje}[/bold yellow]")


def pausar() -> None:
    console.input("\n[dim]Presione Enter para continuar...[/dim]")


def confirmar(mensaje: str) -> bool:
    respuesta = console.input(f"[yellow]{mensaje} (s/n): [/yellow]").strip().lower()
    return respuesta in ("s", "si", "sí")


def pedir_texto(mensaje: str, validador=None, opcional: bool = False) -> str:
    """Pide texto por consola. `validador` es una función (valor) -> (bool, error)."""
    while True:
        valor = console.input(f"[cyan]{mensaje}: [/cyan]").strip()
        if opcional and valor == "":
            return valor
        if not opcional and valor == "":
            mostrar_error("Este campo es obligatorio.")
            continue
        if validador:
            valido, error = validador(valor)
            if not valido:
                mostrar_error(error)
                continue
        return valor


def pedir_entero(mensaje: str, validador=None) -> int:
    while True:
        valor = console.input(f"[cyan]{mensaje}: [/cyan]").strip()
        if validador:
            valido, error = validador(valor)
            if not valido:
                mostrar_error(error)
                continue
        try:
            return int(valor)
        except ValueError:
            mostrar_error("Debe ingresar un número entero.")


def pedir_decimal(mensaje: str, validador=None) -> float:
    while True:
        valor = console.input(f"[cyan]{mensaje}: [/cyan]").strip()
        if validador:
            valido, error = validador(valor)
            if not valido:
                mostrar_error(error)
                continue
        try:
            return float(valor)
        except ValueError:
            mostrar_error("Debe ingresar un número.")


def pedir_opcion(mensaje: str, opciones: list[str]) -> str:
    """Pide una opción de texto libre validada contra una lista permitida."""
    opciones_norm = [o.lower() for o in opciones]
    while True:
        valor = console.input(f"[cyan]{mensaje} ({'/'.join(opciones)}): [/cyan]").strip().lower()
        if valor in opciones_norm:
            return valor
        mostrar_error(f"Opción inválida. Debe ser una de: {', '.join(opciones)}.")


def pedir_menu(titulo_menu: str, opciones: dict[str, str]) -> str:
    """Muestra un menú {clave: etiqueta} y devuelve la clave elegida."""
    console.print(f"\n[bold]{titulo_menu}[/bold]")
    for clave, etiqueta in opciones.items():
        console.print(f"  [cyan]{clave}[/cyan]. {etiqueta}")
    while True:
        eleccion = console.input("[cyan]Seleccione una opción: [/cyan]").strip()
        if eleccion in opciones:
            return eleccion
        mostrar_error("Opción inválida.")


def mostrar_tabla(titulo_tabla: str, columnas: list[str], filas: list[dict]) -> None:
    tabla = Table(title=titulo_tabla, show_lines=False, header_style="bold magenta")
    for col in columnas:
        tabla.add_column(col)
    if not filas:
        console.print(f"[dim]({titulo_tabla}: no hay registros para mostrar)[/dim]")
        return
    for fila in filas:
        fila_dict = dict(fila)  # normaliza sqlite3.Row o dict a dict
        tabla.add_row(*["" if fila_dict.get(col) is None else str(fila_dict.get(col)) for col in columnas])
    console.print(tabla)
