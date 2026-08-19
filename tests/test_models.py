"""Pruebas unitarias de la capa Modelo (CRUD contra una BD SQLite temporal)."""

import pytest

import app.models.cliente as cliente
import app.models.database as database
import app.models.motocicleta as motocicleta
import app.models.orden_trabajo as orden_trabajo
import app.models.repuesto as repuesto
import app.models.usuario as usuario
import app.models.venta as venta


@pytest.fixture(autouse=True)
def bd_temporal(tmp_path, monkeypatch):
    """Redirige DB_PATH a un archivo temporal antes de cada test.

    Todos los modelos llaman a `get_connection()` en tiempo de ejecución, la
    cual lee `database.DB_PATH` desde el namespace del módulo `database` —
    por eso basta con parchear ese atributo, sin recargar los módulos.
    """
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "test.db")
    database.init_db()

    yield {
        "cliente": cliente,
        "motocicleta": motocicleta,
        "orden_trabajo": orden_trabajo,
        "repuesto": repuesto,
        "usuario": usuario,
        "venta": venta,
    }


def test_seed_admin_creado(bd_temporal):
    usuario = bd_temporal["usuario"]
    admin = usuario.obtener_por_usuario("admin")
    assert admin is not None
    assert admin["rol"] == "admin"


def test_cliente_crud(bd_temporal):
    cliente = bd_temporal["cliente"]
    cliente_id = cliente.crear("Juan Pérez", "123456789", "8888-8888", "juan@test.com", "San José")
    fila = cliente.obtener_por_id(cliente_id)
    assert fila["nombre"] == "Juan Pérez"

    cliente.actualizar(cliente_id, "Juan P. Editado", "8888-9999", "juan2@test.com", "Heredia")
    editado = cliente.obtener_por_id(cliente_id)
    assert editado["nombre"] == "Juan P. Editado"

    assert cliente.obtener_por_cedula("123456789") is not None
    assert len(cliente.buscar("Juan")) == 1


def test_motocicleta_estado(bd_temporal):
    moto = bd_temporal["motocicleta"]
    moto_id = moto.crear("Honda", "CB190R", 2024, "Rojo", 190, "VIN123", 2500.0)
    fila = moto.obtener_por_id(moto_id)
    assert fila["estado"] == "disponible"

    moto.cambiar_estado(moto_id, "reservada")
    assert moto.obtener_por_id(moto_id)["estado"] == "reservada"


def test_venta_registrar_marca_moto_vendida(bd_temporal):
    moto = bd_temporal["motocicleta"]
    cliente = bd_temporal["cliente"]
    usuario = bd_temporal["usuario"]
    venta = bd_temporal["venta"]

    moto_id = moto.crear("Yamaha", "FZ", 2023, "Negro", 150, "VIN999", 2000.0)
    cliente_id = cliente.crear("Ana Soto", "987654321", "", "", "")
    admin = usuario.obtener_por_usuario("admin")

    venta_id = venta.registrar(moto_id, cliente_id, admin["id"], 1950.0, "contado")
    assert venta_id is not None
    assert moto.obtener_por_id(moto_id)["estado"] == "vendida"

    with pytest.raises(ValueError):
        venta.registrar(moto_id, cliente_id, admin["id"], 1950.0, "contado")


def test_repuesto_stock_no_negativo(bd_temporal):
    repuesto = bd_temporal["repuesto"]
    repuesto_id = repuesto.crear("Pastillas de freno", "repuesto", "Honda", 25.0, 3, "Proveedor X")

    repuesto.ajustar_stock(repuesto_id, 5)
    assert repuesto.obtener_por_id(repuesto_id)["stock"] == 8

    with pytest.raises(ValueError):
        repuesto.ajustar_stock(repuesto_id, -100)


def test_orden_trabajo_agregar_repuesto_descuenta_stock(bd_temporal):
    cliente = bd_temporal["cliente"]
    repuesto = bd_temporal["repuesto"]
    orden_trabajo = bd_temporal["orden_trabajo"]

    cliente_id = cliente.crear("Luis Vargas", "111222333", "", "", "")
    repuesto_id = repuesto.crear("Bujía", "repuesto", "Suzuki", 10.0, 10, "Proveedor Y")

    orden_id = orden_trabajo.crear(cliente_id, "Suzuki", "GN125", "ABC123", None, "Cambio de bujía", 15.0)
    orden_trabajo.agregar_repuesto(orden_id, repuesto_id, 2)

    assert repuesto.obtener_por_id(repuesto_id)["stock"] == 8
    assert orden_trabajo.costo_total(orden_id) == 15.0 + 2 * 10.0
