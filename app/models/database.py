"""Conexión a SQLite, creación del esquema y datos iniciales (seed).

Cada operación de los modelos abre y cierra su propia conexión mediante
``get_connection()``; para una aplicación CLI de un solo proceso esto es
suficiente y evita compartir estado de conexión entre módulos.
"""

import sqlite3
from pathlib import Path

from app.utils.security import hash_password

DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "motos.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS usuarios (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre          TEXT NOT NULL,
    usuario         TEXT NOT NULL UNIQUE,
    password_hash   TEXT NOT NULL,
    rol             TEXT NOT NULL CHECK (rol IN ('admin', 'vendedor', 'mecanico')),
    activo          INTEGER NOT NULL DEFAULT 1,
    fecha_creacion  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS financieras (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre  TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS vendedores (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre  TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS clientes (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre                  TEXT NOT NULL,
    cedula                  TEXT NOT NULL UNIQUE,
    telefono                TEXT,
    email                   TEXT,
    direccion               TEXT,
    financiera_id           INTEGER REFERENCES financieras(id),
    estado_financiamiento   TEXT CHECK (estado_financiamiento IN ('aprobado', 'rechazado', 'pendiente')),
    vendedor_id             INTEGER REFERENCES vendedores(id),
    fecha_registro          TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS motocicletas (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    marca           TEXT NOT NULL,
    modelo          TEXT NOT NULL,
    anio            INTEGER NOT NULL,
    color           TEXT,
    cilindraje      INTEGER,
    vin             TEXT NOT NULL UNIQUE,
    precio          REAL NOT NULL,
    moneda          TEXT NOT NULL CHECK (moneda IN ('CRC', 'USD')) DEFAULT 'CRC',
    estado          TEXT NOT NULL CHECK (estado IN ('disponible', 'reservada', 'vendida'))
                        DEFAULT 'disponible',
    fecha_ingreso   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS ventas (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    moto_id         INTEGER NOT NULL REFERENCES motocicletas(id),
    cliente_id      INTEGER NOT NULL REFERENCES clientes(id),
    vendedor_id     INTEGER NOT NULL REFERENCES usuarios(id),
    fecha           TEXT NOT NULL,
    precio_final    REAL NOT NULL,
    moneda          TEXT NOT NULL CHECK (moneda IN ('CRC', 'USD')) DEFAULT 'CRC',
    metodo_pago     TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS repuestos (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre              TEXT NOT NULL,
    categoria           TEXT NOT NULL CHECK (categoria IN ('repuesto', 'accesorio')),
    marca_compatible    TEXT,
    precio              REAL NOT NULL,
    moneda              TEXT NOT NULL CHECK (moneda IN ('CRC', 'USD')) DEFAULT 'CRC',
    stock               INTEGER NOT NULL DEFAULT 0,
    proveedor           TEXT
);

CREATE TABLE IF NOT EXISTS ventas_repuestos (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    repuesto_id     INTEGER NOT NULL REFERENCES repuestos(id),
    cliente_id      INTEGER NOT NULL REFERENCES clientes(id),
    vendedor_id     INTEGER NOT NULL REFERENCES usuarios(id),
    fecha           TEXT NOT NULL,
    cantidad        INTEGER NOT NULL,
    precio_unitario REAL NOT NULL,
    moneda          TEXT NOT NULL CHECK (moneda IN ('CRC', 'USD')) DEFAULT 'CRC',
    metodo_pago     TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS ordenes_trabajo (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id              INTEGER NOT NULL REFERENCES clientes(id),
    moto_marca              TEXT,
    moto_modelo             TEXT,
    moto_placa              TEXT,
    mecanico_id             INTEGER REFERENCES usuarios(id),
    descripcion_problema    TEXT NOT NULL,
    estado                  TEXT NOT NULL
                                CHECK (estado IN ('pendiente', 'en_proceso', 'completada', 'entregada'))
                                DEFAULT 'pendiente',
    costo_mano_obra         REAL NOT NULL DEFAULT 0,
    fecha_ingreso           TEXT NOT NULL,
    fecha_salida            TEXT
);

CREATE TABLE IF NOT EXISTS orden_repuestos (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    orden_id            INTEGER NOT NULL REFERENCES ordenes_trabajo(id),
    repuesto_id         INTEGER NOT NULL REFERENCES repuestos(id),
    cantidad            INTEGER NOT NULL,
    precio_unitario     REAL NOT NULL,
    moneda              TEXT NOT NULL CHECK (moneda IN ('CRC', 'USD')) DEFAULT 'CRC'
);
"""


def get_connection() -> sqlite3.Connection:
    """Abre una conexión nueva con claves foráneas activas y filas tipo dict."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    """Crea el esquema si no existe y siembra el usuario admin por defecto."""
    with get_connection() as conn:
        conn.executescript(SCHEMA)
        _migrar_clientes(conn)
        _migrar_monedas(conn)
        _seed_admin(conn)


def _migrar_clientes(conn: sqlite3.Connection) -> None:
    """Agrega a `clientes` las columnas de financiamiento en bases de datos creadas
    antes de que existieran (SQLite no soporta `ADD COLUMN IF NOT EXISTS`)."""
    columnas = {fila["name"] for fila in conn.execute("PRAGMA table_info(clientes)")}
    if "financiera_id" not in columnas:
        conn.execute("ALTER TABLE clientes ADD COLUMN financiera_id INTEGER REFERENCES financieras(id)")
    if "estado_financiamiento" not in columnas:
        conn.execute(
            "ALTER TABLE clientes ADD COLUMN estado_financiamiento TEXT "
            "CHECK (estado_financiamiento IN ('aprobado', 'rechazado', 'pendiente'))"
        )
    if "vendedor_id" not in columnas:
        conn.execute("ALTER TABLE clientes ADD COLUMN vendedor_id INTEGER REFERENCES vendedores(id)")
    conn.commit()


def _migrar_monedas(conn: sqlite3.Connection) -> None:
    """Agrega la columna `moneda` (CRC/USD) a las tablas con precio, en bases de
    datos creadas antes de que existiera."""
    tablas = ("motocicletas", "ventas", "repuestos", "ventas_repuestos", "orden_repuestos")
    for tabla in tablas:
        columnas = {fila["name"] for fila in conn.execute(f"PRAGMA table_info({tabla})")}
        if "moneda" not in columnas:
            conn.execute(
                f"ALTER TABLE {tabla} ADD COLUMN moneda TEXT NOT NULL "
                "CHECK (moneda IN ('CRC', 'USD')) DEFAULT 'CRC'"
            )
    conn.commit()


def _seed_admin(conn: sqlite3.Connection) -> None:
    """Crea un usuario admin/admin123 si todavía no existe ningún usuario."""
    total = conn.execute("SELECT COUNT(*) AS n FROM usuarios").fetchone()["n"]
    if total == 0:
        conn.execute(
            """INSERT INTO usuarios (nombre, usuario, password_hash, rol, activo, fecha_creacion)
               VALUES (?, ?, ?, ?, 1, datetime('now', 'localtime'))""",
            ("Administrador", "admin", hash_password("admin123"), "admin"),
        )
        conn.commit()
