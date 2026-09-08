"""Utilidades para guardar/eliminar las imágenes subidas de repuestos y accesorios."""

import uuid
from pathlib import Path

from werkzeug.utils import secure_filename

EXTENSIONES_PERMITIDAS = {"png", "jpg", "jpeg", "gif", "webp"}
CARPETA_REPUESTOS = "uploads/repuestos"
TAMANO_MAXIMO_MB = 5


def extension_valida(nombre_archivo: str) -> bool:
    nombre = secure_filename(nombre_archivo or "")
    return "." in nombre and nombre.rsplit(".", 1)[1].lower() in EXTENSIONES_PERMITIDAS


def guardar_imagen_repuesto(archivo, carpeta_static: Path) -> str:
    """Guarda el archivo subido con un nombre único y devuelve la ruta relativa
    (dentro de static/) a guardar en la base de datos."""
    ext = secure_filename(archivo.filename).rsplit(".", 1)[1].lower()
    nombre = f"{uuid.uuid4().hex}.{ext}"
    destino_dir = carpeta_static / CARPETA_REPUESTOS
    destino_dir.mkdir(parents=True, exist_ok=True)
    archivo.save(destino_dir / nombre)
    return f"{CARPETA_REPUESTOS}/{nombre}"


def eliminar_imagen_repuesto(ruta_relativa: str | None, carpeta_static: Path) -> None:
    if not ruta_relativa:
        return
    ruta = carpeta_static / ruta_relativa
    if ruta.exists():
        ruta.unlink()
