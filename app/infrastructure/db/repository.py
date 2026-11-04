"""
Adaptador de persistencia: implementa el puerto IEntregaRepository
usando SQLAlchemy. Convierte entre el modelo de base de datos y
la entidad del dominio, para que el dominio nunca tenga que saber
que existe SQLAlchemy.
"""
import uuid

from sqlalchemy.orm import Session

from app.domain.entities import Entrega, EstadoEntrega
from app.infrastructure.db.models import EntregaModel


class SqlEntregaRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def obtener(self, entrega_id: uuid.UUID) -> Entrega | None:
        fila = self._session.get(EntregaModel, str(entrega_id))
        if fila is None:
            return None
        return self._a_entidad(fila)

    def guardar(self, entrega: Entrega) -> None:
        fila = self._session.get(EntregaModel, str(entrega.id))
        if fila is None:
            fila = EntregaModel(id=str(entrega.id))
            self._session.add(fila)

        fila.direccion_destino = entrega.direccion_destino
        fila.estado = entrega.estado.value
        fila.repartidor_id = str(entrega.repartidor_id) if entrega.repartidor_id else None

        self._session.commit()

    @staticmethod
    def _a_entidad(fila: EntregaModel) -> Entrega:
        return Entrega(
            id=uuid.UUID(fila.id),
            direccion_destino=fila.direccion_destino,
            estado=EstadoEntrega(fila.estado),
            repartidor_id=uuid.UUID(fila.repartidor_id) if fila.repartidor_id else None,
        )