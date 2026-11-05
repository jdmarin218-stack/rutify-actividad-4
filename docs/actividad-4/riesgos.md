# Actividad 4 — Registro de riesgos

Riesgos del flujo "asignar repartidor a entrega" tal como quedó construido. Para cada uno se indica qué se hizo y qué queda pendiente, sin maquillar lo que no se resolvió.

## Riesgos

| # | Riesgo | Impacto | Qué se hizo | Estado |
|---|--------|---------|-------------|--------|
| R1 | La disponibilidad del repartidor es una simulación, no el servicio real de Ruteo | Medio | El caso de uso solo conoce el puerto `IDisponibilidadRepartidor`; el adaptador simulado se cambia sin tocar la lógica. Hay pruebas unitarias e de integración con un repartidor sin capacidad. | Aceptado |
| R2 | Dos peticiones simultáneas sobre la misma entrega podrían leerla como Pendiente y asignarla las dos | Alto | La regla de no reasignar vive en la entidad `Entrega`, pero no hay bloqueo ni control de versión en la base de datos. | Abierto |
| R3 | La lista de repartidores saturados vive en memoria | Bajo | Se documenta. Se pierde al reiniciar el servidor y no se comparte entre procesos. | Aceptado |
| R4 | La base se crea con `create_all` y SQLite, sin migraciones versionadas | Medio | Sirve para reproducir el proyecto en cualquier equipo. No guarda historial de cambios del esquema. | Aceptado |
| R5 | Los endpoints no tienen autenticación ni autorización | Alto | Fuera del alcance de esta actividad. | Abierto |
| R6 | Fuga de datos sensibles en los logs | Medio | Los logs registran solo identificadores y el motivo del rechazo, nunca direcciones. | Mitigado |
| R7 | `TestClient` de Starlette avisa que dejará de usar `httpx` | Bajo | Las pruebas funcionan hoy. Se deja el aviso visible en lugar de ocultarlo. | Aceptado |

## Riesgos residuales y siguientes pasos

- **R2 es el más importante.** Para cerrarlo haría falta un control de concurrencia optimista (una columna de versión en la entrega) o una actualización condicional que solo asigne si la entrega sigue sin repartidor. Con SQLite y un solo proceso el riesgo es bajo, pero en producción con varias instancias sería real.
- **R5** se resolvería con autenticación en la capa de entrada, sin tocar el dominio.
- **R1 y R4** se resuelven cuando exista el servicio de Ruteo y una base de datos de servidor con migraciones (por ejemplo, Alembic).