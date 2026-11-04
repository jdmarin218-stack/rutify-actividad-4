"""
Adaptador de disponibilidad de repartidor.

En un sistema real esto llamaría al Contexto de Ruteo (otra API o
servicio interno). Como no tenemos ese servicio disponible para esta
actividad, lo simulamos aquí con una regla simple y lo dejamos
documentado como una limitación conocida (ver docs/actividad-4/riesgos.md).

El punto importante es que el caso de uso NO sabe que esto es una
simulación: solo conoce el puerto IDisponibilidadRepartidor. El día
que exista el servicio real, se cambia este archivo y nada más.
"""
import uuid


class DisponibilidadRepartidorSimulada:
    """
    Simula la consulta de capacidad. Por defecto todos los repartidores
    tienen capacidad, excepto los que se marquen explícitamente como
    saturados (útil para probar el caso de error).
    """

    def __init__(self) -> None:
        self._repartidores_saturados: set[uuid.UUID] = set()

    def marcar_como_saturado(self, repartidor_id: uuid.UUID) -> None:
        self._repartidores_saturados.add(repartidor_id)

    def tiene_capacidad(self, repartidor_id: uuid.UUID) -> bool:
        return repartidor_id not in self._repartidores_saturados