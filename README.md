# Elián-Liam Motors CR

Agencia Multimarca de Motocicletas — sistema de gestión en Python para
inventario de motocicletas, clientes, ventas, repuestos/accesorios y taller
mecánico. Tiene dos interfaces (CLI y web) que comparten el mismo Modelo y
Controlador.

## Arquitectura

Construida con el patrón **MVC**, en carpetas separadas:

```
app/
├── models/         # Modelo: acceso a datos (SQLite) y reglas de esquema
├── controllers/     # Controlador: lógica de negocio y validaciones
├── utils/           # Validadores y utilidades (hash de contraseñas, etc.)
└── views/
    ├── *.py          # Vista CLI: menús y formularios de consola (rich)
    └── web/           # Vista web: Flask + Jinja2 (rutas, plantillas, CSS)
main.py             # Punto de entrada de la versión CLI
webapp.py           # Punto de entrada de la versión web
tests/              # Pruebas unitarias (pytest)
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

**Versión CLI (consola):**

```bash
uv run main.py
```

**Versión web (navegador):**

```bash
uv run webapp.py
```

Levanta un servidor Flask en `http://0.0.0.0:5000`. En GitHub Codespaces, el
puerto 5000 se reenvía automáticamente y queda accesible desde una URL
pública del tipo `https://<codespace>-5000.app.github.dev` (ver la pestaña
*Ports* del editor, o `gh codespace ports visibility 5000:public` para que no
pida autenticación de GitHub).

Al primer arranque (de cualquiera de las dos versiones) se crea
automáticamente un usuario administrador:

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
