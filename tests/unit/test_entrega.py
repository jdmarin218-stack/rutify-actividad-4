"""
Pruebas unitarias del dominio: la entidad Entrega debe proteger
su propia invariante sin ayuda de nadie más.
"""
import uuid

import pytest

from app.domain.entities import (
    Entrega,
    EntregaYaAsignadaError,
    EstadoEntrega,
    TransicionInvalidaError,
)


def test_asignar_repartidor_a_entrega_pendiente_funciona():
    entrega = Entrega.nueva(direccion_destino="Calle 10 #20-30")
    repartidor_id = uuid.uuid4()

    entrega.asignar_repartidor(repartidor_id)

    assert entrega.repartidor_id == repartidor_id
    assert entrega.estado == EstadoEntrega.ASIGNADA


def test_no_se_puede_asignar_dos_veces_la_misma_entrega():
    entrega = Entrega.nueva(direccion_destino="Calle 10 #20-30")
    entrega.asignar_repartidor(uuid.uuid4())

    with pytest.raises(EntregaYaAsignadaError):
        entrega.asignar_repartidor(uuid.uuid4())


def test_no_se_puede_asignar_repartidor_a_entrega_ya_entregada():
    entrega = Entrega.nueva(direccion_destino="Calle 10 #20-30")
    entrega.estado = EstadoEntrega.ENTREGADA

    with pytest.raises(TransicionInvalidaError):
        entrega.asignar_repartidor(uuid.uuid4())