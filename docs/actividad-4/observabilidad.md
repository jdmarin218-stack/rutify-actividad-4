# Actividad 4 — Señales de observabilidad

Qué señales deja el flujo "asignar repartidor a entrega" y cómo se usan para diagnosticarlo sin exponer datos sensibles.

## Señales definidas

Cada evento del flujo deja una línea de log con el logger `rutify.entregas`. Solo se registran identificadores (UUID) y el motivo del resultado. Nunca se registra la dirección de destino.

| Evento | Nivel | Qué indica |
|---|---|---|
| `entrega_creada entrega_id=...` | INFO | Se creó una entrega pendiente. |
| `repartidor_asignado entrega_id=... repartidor_id=...` | INFO | La asignación se hizo y quedó guardada. |
| `asignacion_rechazada entrega_id=... motivo=no_encontrada` | WARNING | La entrega no existe (respuesta 404). |
| `asignacion_rechazada entrega_id=... motivo=sin_capacidad` | WARNING | El repartidor no tiene capacidad (respuesta 409). |
| `asignacion_rechazada entrega_id=... motivo=ya_asignada` | WARNING | La entrega ya tenía repartidor (respuesta 409). |
| `asignacion_rechazada entrega_id=... motivo=transicion_invalida` | WARNING | La entrega existe pero su estado no permite asignarla (respuesta 409). |

Además, el servidor (`uvicorn`) registra una línea por petición con el método, la ruta y el código HTTP.

## Evidencia real

Salida del servidor al ejecutar el flujo completo (crear, asignar, reintentar, entrega inexistente):

    INFO:     127.0.0.1:52155 - "POST /entregas HTTP/1.1" 201 Created
    INFO:rutify.entregas:repartidor_asignado entrega_id=723c239d-59e9-41af-b49f-352b493e5951 repartidor_id=11111111-1111-1111-1111-111111111111
    INFO:     127.0.0.1:52155 - "POST /entregas/723c239d-59e9-41af-b49f-352b493e5951/asignar-repartidor HTTP/1.1" 200 OK
    WARNING:rutify.entregas:asignacion_rechazada entrega_id=723c239d-59e9-41af-b49f-352b493e5951 motivo=ya_asignada
    INFO:     127.0.0.1:52155 - "POST /entregas/723c239d-59e9-41af-b49f-352b493e5951/asignar-repartidor HTTP/1.1" 409 Conflict
    WARNING:rutify.entregas:asignacion_rechazada entrega_id=99999999-9999-9999-9999-999999999999 motivo=no_encontrada
    INFO:     127.0.0.1:52155 - "POST /entregas/99999999-9999-9999-9999-999999999999/asignar-repartidor HTTP/1.1" 404 Not Found

Se puede seguir la historia de una entrega buscando su `entrega_id` en el log: se ve que se asignó y que luego un segundo intento fue rechazado.

Los motivos `sin_capacidad` y `transicion_invalida` no se capturaron en el servidor real, porque no se pueden provocar desde la API; se verifican con pruebas de integración (códigos de respuesta, no el texto del log).

## Cómo diagnosticar con estas señales

| Síntoma | Qué buscar en el log | Causa probable |
|---|---|---|
| Un cliente recibe 404 | `motivo=no_encontrada` con el `entrega_id` | El identificador es incorrecto o la entrega nunca se creó. |
| Un cliente recibe 409 | `motivo=ya_asignada` | Reintento o doble clic sobre una entrega que ya tenía repartidor. |
| Un cliente recibe 409 | `motivo=sin_capacidad` | El repartidor está saturado; hay que elegir otro. |
| Un cliente recibe 409 | `motivo=transicion_invalida` | La entrega ya no está pendiente (por ejemplo, ya fue entregada). |
| Una entrega aparece asignada sin que nadie la pidió | `repartidor_asignado` con ese `entrega_id` | Muestra cuándo y con qué repartidor se asignó. |

## Qué no se registra

Las direcciones de destino no aparecen en ningún log. Hoy esto se verifica revisando las llamadas a `logger` en `app/api/main.py`; no hay una prueba automática (riesgo R6).

## Hallazgo corregido durante la actividad

Al documentar las señales se detectó que `TransicionInvalidaError` no se capturaba en el endpoint: si la entrega no estaba Pendiente, la API respondía 500 sin una línea propia de `rutify.entregas`. Se corrigió para que responda 409 y registre `motivo=transicion_invalida`, y se agregó la prueba `test_entrega_que_no_esta_pendiente_responde_409_y_no_500`.

## Limitaciones conocidas

- No hay identificador de correlación por petición; se cruzan las líneas por `entrega_id`.
- Los logs son texto plano, no JSON, y no hay métricas ni trazas distribuidas (no se usó OpenTelemetry).
- No hay prueba automática de que los logs omitan datos sensibles.
- Las pruebas verifican los códigos de respuesta, no el contenido exacto de las líneas de log.