"""
Capa de dominio — Entidades y objetos de valor del flujo de asignación de repartidor.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum


class EstadoEntrega(str, Enum):
    PENDIENTE = "Pendiente"
    ASIGNADA = "Asignada"
    EN_CAMINO = "EnCamino"
    ENTREGADA = "Entregada"
    FALLIDA = "Fallida"


class EntregaYaAsignadaError(Exception):
    """Se lanza cuando se intenta asignar un repartidor a una entrega que ya tiene uno activo."""


class TransicionInvalidaError(Exception):
    """Se lanza cuando se intenta una transición de estado no permitida."""


@dataclass
class Entrega:
    """
    Entidad del dominio. Protege la invariante central del flujo:
    una entrega nunca puede tener dos repartidores activos al mismo tiempo.
    """
    id: uuid.UUID
    direccion_destino: str
    estado: EstadoEntrega = EstadoEntrega.PENDIENTE
    repartidor_id: uuid.UUID | None = None

    def asignar_repartidor(self, repartidor_id: uuid.UUID) -> None:
        if self.repartidor_id is not None:
            raise EntregaYaAsignadaError(
                f"La entrega {self.id} ya tiene un repartidor asignado"
            )
        if self.estado != EstadoEntrega.PENDIENTE:
            raise TransicionInvalidaError(
                f"No se puede asignar repartidor a una entrega en estado {self.estado}"
            )
        self.repartidor_id = repartidor_id
        self.estado = EstadoEntrega.ASIGNADA

    @staticmethod
    def nueva(direccion_destino: str) -> "Entrega":
        return Entrega(id=uuid.uuid4(), direccion_destino=direccion_destino)