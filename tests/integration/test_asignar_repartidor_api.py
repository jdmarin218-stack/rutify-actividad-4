"""
Pruebas de integración del flujo "asignar repartidor a entrega".

Aquí se recorre todo el camino real: la petición HTTP entra por el
endpoint, pasa por el caso de uso y el dominio, y termina guardada en
la base de datos (en memoria). No hay dobles falsos como en las pruebas
unitarias.
"""
import uuid

from app.api.dependencies import disponibilidad_repartidor


def _crear_entrega(client, direccion="Calle 50 #30-20, Medellín") -> dict:
    respuesta = client.post("/entregas", json={"direccion_destino": direccion})
    assert respuesta.status_code == 201
    return respuesta.json()


def test_flujo_completo_asigna_repartidor_y_queda_guardado(client):
    entrega = _crear_entrega(client)
    repartidor_id = str(uuid.uuid4())

    respuesta = client.post(
        f"/entregas/{entrega['id']}/asignar-repartidor",
        json={"repartidor_id": repartidor_id},
    )

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["estado"] == "Asignada"
    assert cuerpo["repartidor_id"] == repartidor_id

    # prueba de que quedó guardado de verdad: un segundo intento ya
    # encuentra la entrega asignada y la rechaza
    segundo_intento = client.post(
        f"/entregas/{entrega['id']}/asignar-repartidor",
        json={"repartidor_id": str(uuid.uuid4())},
    )
    assert segundo_intento.status_code == 409


def test_no_permite_asignar_dos_repartidores_a_la_misma_entrega(client):
    entrega = _crear_entrega(client)
    url = f"/entregas/{entrega['id']}/asignar-repartidor"

    primera = client.post(url, json={"repartidor_id": str(uuid.uuid4())})
    segunda = client.post(url, json={"repartidor_id": str(uuid.uuid4())})

    assert primera.status_code == 200
    assert segunda.status_code == 409
    assert "ya tiene un repartidor asignado" in segunda.json()["detail"]


def test_entrega_inexistente_responde_404(client):
    respuesta = client.post(
        f"/entregas/{uuid.uuid4()}/asignar-repartidor",
        json={"repartidor_id": str(uuid.uuid4())},
    )

    assert respuesta.status_code == 404
    assert "No existe la entrega" in respuesta.json()["detail"]


def test_repartidor_sin_capacidad_responde_409_y_no_toca_la_entrega(client):
    entrega = _crear_entrega(client)
    url = f"/entregas/{entrega['id']}/asignar-repartidor"

    repartidor_saturado = uuid.uuid4()
    disponibilidad_repartidor.marcar_como_saturado(repartidor_saturado)

    rechazada = client.post(url, json={"repartidor_id": str(repartidor_saturado)})
    assert rechazada.status_code == 409
    assert "no tiene capacidad" in rechazada.json()["detail"]

    # la entrega debió quedar intacta: otro repartidor sí puede tomarla
    aceptada = client.post(url, json={"repartidor_id": str(uuid.uuid4())})
    assert aceptada.status_code == 200
    assert aceptada.json()["estado"] == "Asignada"