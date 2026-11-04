"""
Puertos — contratos que la capa de aplicación necesita.
La implementación concreta vive en infraestructura (adaptadores).
"""
from __future__ import annotations

import uuid
from typing import Protocol

from app.domain.entities import Entrega


class IEntregaRepository(Protocol):
    """Puerto de persistencia: guardar y recuperar entregas."""

    def obtener(self, entrega_id: uuid.UUID) -> Entrega | None: ...

    def guardar(self, entrega: Entrega) -> None: ...


class IDisponibilidadRepartidor(Protocol):
    """
    Puerto de consulta de disponibilidad.
    Entregas no conoce cómo Ruteo calcula la capacidad, solo recibe sí/no.
    """

    def tiene_capacidad(self, repartidor_id: uuid.UUID) -> bool: ...