# Actividad 4 — Decisiones tecnológicas y de implementación

El enunciado aclara que no se espera aplicar todos los patrones, sino justificar cuáles aplican y cuáles no. Rutify se construyó como un monolito modular con un solo flujo (asignar repartidor a entrega), así que la mayoría de los patrones pensados para microservicios, mensajería o infraestructura grande no aportan hoy. Aquí queda el criterio de cada uno.

## Stack elegido

- **Python y FastAPI** para la capa de entrada, porque es el stack con el que trabajo y el enunciado no impone lenguaje.
- **SQLAlchemy con SQLite** para la persistencia: no necesita un servidor aparte y permite que cualquiera reproduzca el proyecto. El dominio no sabe que existe, porque el repositorio convierte entre el modelo de base de datos y la entidad.
- **pytest** con `TestClient` de FastAPI para las pruebas unitarias, de integración y de arquitectura.

## Patrones que aplican

| Patrón (video) | Cómo se aplicó |
|---|---|
| Durable State vs Event Sourcing (V24) | Se guarda el **estado actual** de la entrega en una tabla. Event Sourcing se descartó: para un flujo con una sola transición, reconstruir el estado desde eventos agregaría complejidad sin beneficio. |
| Máquinas de estado finito (V25) | La entidad `Entrega` controla sus propias transiciones con `EstadoEntrega`. Hoy solo está implementada la transición Pendiente a Asignada, y la entidad rechaza asignar si el estado no es Pendiente. Las demás transiciones (EnCamino, Entregada, Fallida) quedan declaradas pero fuera del alcance del flujo. |
| Fitness Functions (V27) y pruebas de arquitectura (V12) | `tests/unit/test_arquitectura.py` verifica por análisis de imports que el dominio y la aplicación no dependan de infraestructura, API ni frameworks. |
| Observabilidad (V28), en versión mínima | Logs con identificadores y motivo del rechazo (`entrega_creada`, `repartidor_asignado`, `asignacion_rechazada`), sin direcciones ni datos sensibles. No se usó OpenTelemetry. |
| Trunk Based Development (V4), parcial | Se trabaja sobre una sola rama con commits pequeños y mensajes descriptivos. No hay reglas de protección de rama ni pull requests, porque es un repositorio individual. |

## Patrones que no aplican (por ahora)

| Patrón (video) | Por qué no |
|---|---|
| Monorepos con Pants (V3) | Hay un solo servicio en un solo repositorio. |
| Strangler Fig (V14) | No hay un sistema legado que migrar. Sería útil si Rutify reemplazara poco a poco otro sistema. |
| Migraciones con Flyway (V15) | Se aplicó la idea con la herramienta del ecosistema Python: Alembic. La migración `0001` crea la tabla `entregas`, `alembic check` detecta si los modelos se desalinean de la migración y una prueba automática lo verifica. Se cierra así el riesgo R4. |
| Infraestructura como código (V18) | No hay despliegue ni varios servicios que aprovisionar. |
| API Gateway (V16) | Con un solo servicio, FastAPI es la entrada directa. Un gateway agregaría un salto sin resolver un problema real. |
| Mensajes vs eventos, productor-consumidor, Dead Letter Queue, Comparing Consumers, Process Manager (V19 a V23) | El flujo es síncrono: la disponibilidad del repartidor se consulta y se responde en la misma petición. Si el servicio real de Ruteo fuera asíncrono, aquí entrarían los eventos, los reintentos y las colas de mensajes fallidos. |
| SAST, DAST y pentesting (V26) | No se ejecutaron en esta entrega. La falta de autenticación está registrada como riesgo R5. |
| Agentes de IA que revisan código (V8) y métricas cuantitativas (V13) | No se usaron en esta entrega. |

## Ajustes respecto al diseño de la Actividad 3

Para que la trazabilidad quede clara, estos son los puntos donde la implementación se movió o completó el diseño:

- **Crear entrega.** El diseño partía de una entrega ya existente. Para poder demostrar el flujo se agregó el endpoint `POST /entregas`, que en el sistema real vendría de un pedido confirmado en el Contexto de Pedidos.
- **Ruta saturada y capacidad del repartidor.** El escenario de rechazo por ruta saturada se implementó como "repartidor sin capacidad", consultado por el puerto `IDisponibilidadRepartidor`. Como el servicio real de Ruteo no existe, el adaptador es una simulación (riesgo R1).
- **Modelo de base de datos separado del dominio.** Se agregó `EntregaModel` (SQLAlchemy) distinto de la entidad `Entrega`, con el repositorio como traductor, y DTOs de Pydantic distintos de ambos, para que el contrato HTTP, el dominio y la tabla puedan cambiar por separado.
- **Dónde se cablean los puertos.** Solo en `app/api/dependencies.py`.