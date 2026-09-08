"""Pruebas unitarias de la capa Controlador (reglas de negocio)."""

import pytest

import app.models.database as database
from app.controllers import (
    cliente_controller,
    inventario_controller,
    repuesto_controller,
    taller_controller,
    usuario_controller,
    venta_controller,
    venta_repuesto_controller,
)


@pytest.fixture(autouse=True)
def bd_temporal(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "test.db")
    database.init_db()


def _admin_id():
    from app.models import usuario as usuario_model

    return usuario_model.obtener_por_usuario("admin")["id"]


def test_no_se_puede_vender_moto_ya_vendida():
    moto = inventario_controller.crear_moto("Honda", "CB190R", 2024, "Rojo", 190, "VIN-A1", 2500.0)
    cliente = cliente_controller.crear_cliente("Marta Rojas", "101010101", "", "", "")

    venta_controller.registrar_venta(moto["id"], cliente["id"], _admin_id(), 2400.0, "contado")

    with pytest.raises(ValueError):
        venta_controller.registrar_venta(moto["id"], cliente["id"], _admin_id(), 2400.0, "contado")


def test_no_se_puede_vender_repuesto_sin_stock_suficiente():
    repuesto = repuesto_controller.crear_repuesto("Cadena", "repuesto", "Universal", 30.0, 1, "Proveedor W")
    cliente = cliente_controller.crear_cliente("Beto Jiménez", "404040404", "", "", "")

    with pytest.raises(ValueError):
        venta_repuesto_controller.registrar_venta(repuesto["id"], cliente["id"], _admin_id(), 5, 30.0, "contado")


def test_no_se_permite_vin_duplicado():
    inventario_controller.crear_moto("Honda", "CB190R", 2024, "Rojo", 190, "VIN-DUP", 2500.0)
    with pytest.raises(ValueError):
        inventario_controller.crear_moto("Suzuki", "GN125", 2023, "Negro", 125, "VIN-DUP", 1800.0)


def test_no_se_permite_cedula_duplicada():
    cliente_controller.crear_cliente("Carlos Mora", "202020202", "", "", "")
    with pytest.raises(ValueError):
        cliente_controller.crear_cliente("Otro Nombre", "202020202", "", "", "")


def test_usuario_rol_invalido_rechazado():
    with pytest.raises(ValueError):
        usuario_controller.crear_usuario("Pedro", "pedro1", "clave123", "rol_invalido")


def test_taller_transicion_estado_invalida():
    cliente = cliente_controller.crear_cliente("Sofía Lee", "303030303", "", "", "")
    orden = taller_controller.crear_orden(
        cliente["id"], "Bera", "SBR", "XYZ789", None, "Ruido en motor", 20.0
    )
    assert orden["estado"] == "pendiente"

    # No se puede saltar directo de 'pendiente' a 'entregada'.
    with pytest.raises(ValueError):
        taller_controller.cambiar_estado_orden(orden["id"], "entregada")

    orden = taller_controller.cambiar_estado_orden(orden["id"], "en_proceso")
    assert orden["estado"] == "en_proceso"
