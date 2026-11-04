"""
Caso de uso: asignar un repartidor a una entrega.

Esta es la pieza que coordina todo: busca la entrega, verifica que el
repartidor tenga espacio, protege la regla de negocio (eso lo hace la
propia entidad) y guarda el resultado. No sabe nada de bases de datos
ni de cómo se calcula la disponibilidad, solo usa los puertos.
"""
from __future__ import annotations

import uuid

from app.application.ports import IDisponibilidadRepartidor, IEntregaRepository
from app.domain.entities import Entrega


class EntregaNoEncontradaError(Exception):
    pass


class RepartidorSinCapacidadError(Exception):
    pass


class AsignarRepartidorUseCase:
    def __init__(
        self,
        repositorio: IEntregaRepository,
        disponibilidad: IDisponibilidadRepartidor,
    ) -> None:
        self._repositorio = repositorio
        self._disponibilidad = disponibilidad

    def ejecutar(self, entrega_id: uuid.UUID, repartidor_id: uuid.UUID) -> Entrega:
        entrega = self._repositorio.obtener(entrega_id)
        if entrega is None:
            raise EntregaNoEncontradaError(f"No existe la entrega {entrega_id}")

        if not self._disponibilidad.tiene_capacidad(repartidor_id):
            raise RepartidorSinCapacidadError(
                f"El repartidor {repartidor_id} no tiene capacidad disponible"
            )

        # la regla de "no se puede reasignar" vive dentro de la entidad,
        # no aquí, así nadie se la puede saltar
        entrega.asignar_repartidor(repartidor_id)
        self._repositorio.guardar(entrega)

        return entrega