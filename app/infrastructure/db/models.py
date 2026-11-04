"""
Modelo de base de datos (SQLAlchemy). Esto NO es la entidad del dominio,
es solo cómo se guarda en la tabla. El repositorio se encarga de
convertir entre una cosa y la otra.
"""
import uuid

from sqlalchemy import Column, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class EntregaModel(Base):
    __tablename__ = "entregas"

    id = Column(String(36), primary_key=True)
    direccion_destino = Column(String, nullable=False)
    estado = Column(String(20), nullable=False)
    repartidor_id = Column(String(36), nullable=True)