# Actividad 4 — Registro de riesgos

Riesgos del flujo "asignar repartidor a entrega" tal como quedó construido. Cada riesgo indica la mitigación aplicada y la evidencia con que se puede verificar. Donde no hay evidencia, se dice.

## Registro

| # | Riesgo | Impacto | Mitigación | Evidencia de verificación | Estado |
|---|--------|---------|------------|---------------------------|--------|
| R1 | La disponibilidad del repartidor es una simulación, no el servicio real de Ruteo | Medio | El caso de uso solo conoce el puerto `IDisponibilidadRepartidor`; el adaptador simulado se reemplaza sin tocar la lógica. | `test_repartidor_sin_capacidad_responde_409_y_no_toca_la_entrega` (integración) | Aceptado |
| R2 | Dos peticiones simultáneas sobre la misma entrega podrían leerla como Pendiente y asignarla las dos | Alto | La regla de no reasignar vive en la entidad `Entrega`. No hay bloqueo ni control de versión en la base de datos. | La invariante se prueba en secuencia (`test_no_se_puede_asignar_dos_veces_la_misma_entrega` y su prueba de integración). **No hay prueba de concurrencia.** | Abierto |
| R3 | La lista de repartidores saturados vive en memoria | Bajo | Se documenta en el adaptador simulado. Se pierde al reiniciar y no se comparte entre procesos. | Docstring de `disponibilidad_ruteo.py` | Aceptado |
| R4 | Sin migraciones versionadas, el esquema de la base no tendría historial ni podría evolucionar de forma controlada | Medio | Migraciones con Alembic: la migración `0001` crea la tabla `entregas` y el servidor ya no crea tablas por su cuenta (hay que correr `alembic upgrade head`). Una prueba aplica la migración sobre una base vacía y falla si los modelos tienen algo que la migración no cubre. | `migrations/versions/0001_crear_tabla_entregas.py`; `tests/integration/test_migraciones.py`; `alembic check` responde "No new upgrade operations detected". | Mitigado |
| R5 | Los endpoints no tienen autenticación ni autorización | Alto | Fuera del alcance de esta actividad. | Ninguna | Abierto |
| R6 | Fuga de datos sensibles en los logs | Medio | Los logs registran solo identificadores y el motivo del rechazo, nunca direcciones. | Revisión de las llamadas a `logger` en `app/api/main.py` y logs reales en `observabilidad.md`. **No hay prueba automática.** | Mitigado |
| R7 | `TestClient` de Starlette avisa que dejará de usar `httpx` | Bajo | Las pruebas funcionan hoy. El aviso se deja visible en lugar de ocultarlo. | Sección de avisos de la salida de `pytest` | Aceptado |
| R8 | Que el dominio termine dependiendo de la base de datos o de la web sin que nadie lo note | Medio | Chequeo automático de imports por capa. | `tests/unit/test_arquitectura.py`; se comprobó que falla al meter `import sqlalchemy` en `entities.py`. | Mitigado |
| R9 | Un error de dominio sin manejar termina en un 500 sin rastro propio | Medio | El endpoint traduce a 409 todos los errores de dominio del flujo y registra el motivo. | `test_entrega_que_no_esta_pendiente_responde_409_y_no_500` (integración) | Mitigado |

## Resultados de las verificaciones automáticas

- `pytest tests`: 11 pruebas pasando (3 de dominio, 6 de integración, 2 de arquitectura), con 1 aviso de deprecación (R7).
- Chequeo de arquitectura: el dominio y la aplicación no importan infraestructura, API ni frameworks.
- Prueba de que el chequeo detecta violaciones: al agregar a propósito `import sqlalchemy` en `app/domain/entities.py`, la prueba del dominio falló señalando `entities.py importa sqlalchemy`. El cambio se revirtió.
- Hallazgo corregido: al documentar la observabilidad se detectó que `TransicionInvalidaError` no se capturaba en el endpoint y habría respondido 500 (R9). Se corrigió y se agregó su prueba.

## Riesgos residuales y siguientes pasos

- **R2 es el más importante.** Para cerrarlo haría falta un control de concurrencia optimista (una columna de versión en la entrega) o una actualización condicional que solo asigne si la entrega sigue sin repartidor, más una prueba con dos asignaciones simultáneas. Con SQLite y un solo proceso el riesgo es bajo; en producción con varias instancias sería real.
- **R5** se resolvería con autenticación en la capa de entrada, sin tocar el dominio.
- **R6** quedaría cubierto con una prueba que capture los logs y verifique que no aparece la dirección.
- **R1** se resuelve cuando exista el servicio de Ruteo real. **R4** quedó mitigado con Alembic sobre SQLite; en un entorno real se repetiría el mismo mecanismo contra la base del servidor.