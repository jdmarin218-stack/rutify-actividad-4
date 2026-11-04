"""
Inyección de dependencias de FastAPI. Aquí es el único lugar del
proyecto donde se "cablean" los puertos con sus adaptadores concretos.
"""
from typing import Generator

from sqlalchemy.orm import Session

from app.application.use_cases.asignar_repartidor import AsignarRepartidorUseCase
from app.infrastructure.db.models import Base
from app.infrastructure.db.repository import SqlEntregaRepository
from app.infrastructure.db.session import SessionLocal, engine
from app.infrastructure.disponibilidad_ruteo import DisponibilidadRepartidorSimulada

# crea las tablas si no existen (nuestra "migración" simple, ver docs/actividad-4)
Base.metadata.create_all(bind=engine)

# una sola instancia compartida, para poder simular repartidores saturados
# desde las pruebas y que el endpoint vea el mismo estado
disponibilidad_repartidor = DisponibilidadRepartidorSimulada()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_asignar_repartidor_use_case(db: Session) -> AsignarRepartidorUseCase:
    repositorio = SqlEntregaRepository(db)
    return AsignarRepartidorUseCase(repositorio, disponibilidad_repartidor)