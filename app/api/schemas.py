"""
DTOs de la API. Esto es lo que viaja por HTTP, no las entidades del
dominio directamente — así el contrato de la API puede cambiar sin
tocar el dominio, y viceversa.
"""
import uuid

from pydantic import BaseModel


class CrearEntregaRequest(BaseModel):
    direccion_destino: str


class EntregaResponse(BaseModel):
    id: uuid.UUID
    direccion_destino: str
    estado: str
    repartidor_id: uuid.UUID | None = None


class AsignarRepartidorRequest(BaseModel):
    repartidor_id: uuid.UUID


class ErrorResponse(BaseModel):
    detalle: str