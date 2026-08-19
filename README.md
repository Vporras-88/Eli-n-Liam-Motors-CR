# Elián-Liam Motors CR

Agencia Multimarca de Motocicletas — sistema de gestión en Python (CLI) para
inventario de motocicletas, clientes, ventas, repuestos/accesorios y taller
mecánico.

## Arquitectura

Aplicación de consola construida con el patrón **MVC**, en carpetas separadas:

```
app/
├── models/       # Modelo: acceso a datos (SQLite) y reglas de esquema
├── views/        # Vista: menús y formularios de consola (rich)
├── controllers/  # Controlador: lógica de negocio y validaciones
└── utils/        # Validadores y utilidades (hash de contraseñas, etc.)
main.py           # Punto de entrada
tests/            # Pruebas unitarias (pytest)
```

## Módulos funcionales

- **Autenticación y Usuarios** (roles: `admin`, `vendedor`, `mecanico`)
- **Clientes**
- **Inventario de Motocicletas**
- **Ventas**
- **Repuestos y Accesorios** (con control de stock)
- **Taller Mecánico** (órdenes de trabajo, repuestos usados, costos)
- **Reportes** básicos (ventas, órdenes de taller, stock bajo)

## Requisitos

- Python 3.12+
- [`uv`](https://docs.astral.sh/uv/) como gestor de entorno y dependencias

## Instalación

```bash
uv sync
```

## Ejecución

```bash
uv run main.py
```

Al primer arranque se crea automáticamente un usuario administrador:

- **Usuario:** `admin`
- **Contraseña:** `admin123`

> Se recomienda cambiar esta contraseña desde el menú *Usuarios → Cambiar
> contraseña* apenas se inicia el sistema por primera vez.

La base de datos SQLite se guarda en `data/motos.db` (se crea automáticamente
y no se versiona en git).

## Pruebas

```bash
uv run pytest
```
