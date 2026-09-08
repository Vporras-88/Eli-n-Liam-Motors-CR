"""Utilidades de moneda: Colones costarricenses (CRC) o Dólares (USD).

Los precios y precios unitarios del sistema se guardan junto con la
moneda en la que fueron ingresados, para mostrarse con su símbolo
correspondiente sin hacer ninguna conversión de tipo de cambio.
"""

MONEDAS = ("CRC", "USD")
MONEDA_POR_DEFECTO = "CRC"

ETIQUETAS = {"CRC": "₡ Colones (CRC)", "USD": "$ Dólares (USD)"}
SIMBOLOS = {"CRC": "₡", "USD": "$"}


def simbolo(moneda: str | None) -> str:
    return SIMBOLOS.get(moneda, SIMBOLOS[MONEDA_POR_DEFECTO])


def formatear(monto: float, moneda: str | None) -> str:
    return f"{simbolo(moneda)}{monto:,.2f}"
