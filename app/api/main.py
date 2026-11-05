"""
Capa de entrada: expone el flujo por HTTP con FastAPI.
El controller solo recibe/valida y responde — la regla de negocio
vive en el caso de uso y el dominio, no aquí.
"""
import logging
import uuid

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_asignar_repartidor_use_case, get_db
from app.api.schemas import (
    AsignarRepartidorRequest,
    CrearEntregaRequest,
    EntregaResponse,
)
from app.application.use_cases.asignar_repartidor import (
    EntregaNoEncontradaError,
    RepartidorSinCapacidadError,
)
from app.domain.entities import Entrega, EntregaYaAsignadaError, TransicionInvalidaError
from app.infrastructure.db.repository import SqlEntregaRepository

logger = logging.getLogger("rutify.entregas")
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Rutify - Actividad 4")


@app.post("/entregas", response_model=EntregaResponse, status_code=201)
def crear_entrega(request: CrearEntregaRequest, db: Session = Depends(get_db)):
    """Crea una entrega pendiente. En el sistema real esto vendría de un pedido ya confirmado en el Contexto de Pedidos."""
    entrega = Entrega.nueva(direccion_destino=request.direccion_destino)
    repositorio = SqlEntregaRepository(db)
    repositorio.guardar(entrega)
    logger.info("entrega_creada entrega_id=%s", entrega.id)
    return entrega


@app.post("/entregas/{entrega_id}/asignar-repartidor", response_model=EntregaResponse)
def asignar_repartidor(
    entrega_id: uuid.UUID,
    request: AsignarRepartidorRequest,
    db: Session = Depends(get_db),
):
    caso_de_uso = get_asignar_repartidor_use_case(db)
    try:
        entrega = caso_de_uso.ejecutar(entrega_id, request.repartidor_id)
    except EntregaNoEncontradaError as error:
        logger.warning("asignacion_rechazada entrega_id=%s motivo=no_encontrada", entrega_id)
        raise HTTPException(status_code=404, detail=str(error))
    except RepartidorSinCapacidadError as error:
        logger.warning("asignacion_rechazada entrega_id=%s motivo=sin_capacidad", entrega_id)
        raise HTTPException(status_code=409, detail=str(error))
    except EntregaYaAsignadaError as error:
        logger.warning("asignacion_rechazada entrega_id=%s motivo=ya_asignada", entrega_id)
        raise HTTPException(status_code=409, detail=str(error))
    except TransicionInvalidaError as error:
        # la entrega existe pero su estado no permite asignarla (por ejemplo, ya fue entregada)
        logger.warning("asignacion_rechazada entrega_id=%s motivo=transicion_invalida", entrega_id)
        raise HTTPException(status_code=409, detail=str(error))

    logger.info("repartidor_asignado entrega_id=%s repartidor_id=%s", entrega_id, request.repartidor_id)
    return entrega