"""
Preparación común para las pruebas de integración.

Cada prueba recibe un cliente HTTP nuevo conectado a una base de datos
SQLite en memoria, así las pruebas no se estorban entre sí y tampoco
tocan el archivo rutify.db que usas cuando corres el servidor a mano.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.dependencies import get_db
from app.api.main import app
from app.infrastructure.db.models import Base


@pytest.fixture
def client():
    # StaticPool hace que todas las conexiones compartan la misma base en
    # memoria; sin esto, cada conexión vería una base vacía distinta
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    SesionDePrueba = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def get_db_de_prueba():
        db = SesionDePrueba()
        try:
            yield db
        finally:
            db.close()

    # le decimos a FastAPI: "donde pedías get_db, usa esta versión de prueba"
    app.dependency_overrides[get_db] = get_db_de_prueba

    with TestClient(app) as cliente:
        yield cliente

    app.dependency_overrides.clear()
    engine.dispose()