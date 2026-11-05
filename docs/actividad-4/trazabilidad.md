# Actividad 4 — Trazabilidad entre diseño e implementación

Relaciona cada elemento diseñado en la Actividad 3 con el código que lo implementa y la prueba que lo verifica.

## Del diseño al código

| Diseño (Actividad 3) | Implementación | Verificación |
|---|---|---|
| Entidad `Entrega` y objeto de valor `EstadoEntrega` | `app/domain/entities.py` | `tests/unit/test_entrega.py` |
| Invariante: una entrega no puede tener dos repartidores activos | `Entrega.asignar_repartidor` | `test_no_se_puede_asignar_dos_veces_la_misma_entrega` (unitaria) y `test_no_permite_asignar_dos_repartidores_a_la_misma_entrega` (integración) |
| Transiciones de estado controladas por la entidad | `Entrega.asignar_repartidor` solo acepta entregas Pendientes | `test_no_se_puede_asignar_repartidor_a_entrega_ya_entregada` (unitaria) y `test_entrega_que_no_esta_pendiente_responde_409_y_no_500` (integración) |
| Caso de uso `AsignarRepartidorUseCase` | `app/application/use_cases/asignar_repartidor.py` | `test_flujo_completo_asigna_repartidor_y_queda_guardado` (integración) |
| Puerto `IEntregaRepository` y su adaptador de base de datos | Puerto en `app/application/ports.py`; adaptador `SqlEntregaRepository` en `app/infrastructure/db/repository.py` | El segundo intento de asignación es rechazado, lo que prueba que la primera quedó guardada |
| Puerto `IDisponibilidadRepartidor` y su adaptador hacia Ruteo | Puerto en `app/application/ports.py`; adaptador simulado en `app/infrastructure/disponibilidad_ruteo.py` | `test_repartidor_sin_capacidad_responde_409_y_no_toca_la_entrega` |
| Contextos separados: Entregas solo consume una respuesta de Ruteo a través de un puerto | El caso de uso no conoce cómo se calcula la capacidad | Mismo que la fila anterior |
| Dependencias hacia adentro: dominio y aplicación no conocen la infraestructura | Estructura de capas en `app/` | `tests/unit/test_arquitectura.py` |
| Resultado esperado: la decisión queda persistida y trazable | Repositorio y logs `repartidor_asignado` | Flujo completo de integración; logs reales en `observabilidad.md` |

## Escenarios de aceptación

| Escenario de la Actividad 3 | Prueba |
|---|---|
| Asignación exitosa | `test_flujo_completo_asigna_repartidor_y_queda_guardado` |
| Rechazo por entrega ya asignada | `test_no_permite_asignar_dos_repartidores_a_la_misma_entrega` |
| Rechazo por ruta saturada | `test_repartidor_sin_capacidad_responde_409_y_no_toca_la_entrega` (implementado como repartidor sin capacidad) |

## Lo que del diseño no se implementó

- **Entidades `Repartidor` y `Ruta`.** El repartidor es solo un identificador en la entrega, y la capacidad la responde el puerto de disponibilidad. No hay una entidad con sus propias reglas.
- **Integración real con el Contexto de Ruteo.** Se reemplazó por un adaptador simulado (riesgo R1).
- **Notificación al cliente.** En el diseño era un efecto indirecto del flujo; no se implementó.
- **Actor operador logístico.** No hay autenticación ni roles (riesgo R5).
- **Transiciones posteriores a Asignada** (EnCamino, Entregada, Fallida). Los estados existen en el dominio, pero ningún endpoint los cambia.

## Ajustes al diseño

Los cambios que se hicieron al implementar (endpoint de creación de entrega, modelo de base de datos separado del dominio, nombre del escenario de ruta saturada) están explicados en `decisiones-tecnologicas.md`.