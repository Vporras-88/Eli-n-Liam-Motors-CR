"""Validaciones reutilizables de campos de entrada.

Cada función devuelve ``(valido, mensaje_error)``; ``mensaje_error`` es
``""`` cuando el valor es válido. Las vistas usan estas funciones antes de
pasar los datos a los controladores.
"""

import re
from datetime import datetime

CEDULA_RE = re.compile(r"^\d{9,12}$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
TELEFONO_RE = re.compile(r"^\d{4}-?\d{4}$")


def validar_no_vacio(valor: str, campo: str) -> tuple[bool, str]:
    if not valor or not valor.strip():
        return False, f"{campo} no puede estar vacío."
    return True, ""


def validar_cedula(valor: str) -> tuple[bool, str]:
    if not CEDULA_RE.match(valor.strip()):
        return False, "La cédula debe tener entre 9 y 12 dígitos numéricos."
    return True, ""


def validar_email(valor: str) -> tuple[bool, str]:
    if valor and not EMAIL_RE.match(valor.strip()):
        return False, "El formato de email no es válido."
    return True, ""


def validar_telefono(valor: str) -> tuple[bool, str]:
    if valor and not TELEFONO_RE.match(valor.strip()):
        return False, "El teléfono debe tener formato 0000-0000."
    return True, ""


def validar_entero_positivo(valor: str, campo: str) -> tuple[bool, str]:
    try:
        if int(valor) <= 0:
            raise ValueError
    except ValueError:
        return False, f"{campo} debe ser un número entero positivo."
    return True, ""


def validar_entero_no_negativo(valor: str, campo: str) -> tuple[bool, str]:
    try:
        if int(valor) < 0:
            raise ValueError
    except ValueError:
        return False, f"{campo} debe ser un número entero mayor o igual a 0."
    return True, ""


def validar_decimal_positivo(valor: str, campo: str) -> tuple[bool, str]:
    try:
        if float(valor) <= 0:
            raise ValueError
    except ValueError:
        return False, f"{campo} debe ser un número mayor a 0."
    return True, ""


def validar_decimal_no_negativo(valor: str, campo: str) -> tuple[bool, str]:
    try:
        if float(valor) < 0:
            raise ValueError
    except ValueError:
        return False, f"{campo} debe ser un número mayor o igual a 0."
    return True, ""


def validar_anio(valor: str) -> tuple[bool, str]:
    try:
        anio = int(valor)
        actual = datetime.now().year
        if anio < 1980 or anio > actual + 1:
            raise ValueError
    except ValueError:
        return False, f"El año debe estar entre 1980 y {datetime.now().year + 1}."
    return True, ""
