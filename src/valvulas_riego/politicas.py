"""
Implementación del patrón Strategy para algoritmos agronómicos de riego (E2).
Encapsula la familia de algoritmos de cálculo de dosis hídrica según el cultivo y suelo.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, Type, Any


class PoliticaRiego(ABC):
    """STRATEGY: interfaz común para los algoritmos de cálculo de duración de riego."""

    nombre: str = "BASE"

    @abstractmethod
    def calcular_duracion(self, duracion_solicitada_min: int, humedad_suelo: float) -> int:
        """Calcula los minutos de riego recomendados según la humedad del suelo."""
        ...


class PoliticaGoteo(PoliticaRiego):
    """Estrategia de riego por goteo: alta eficiencia, sensible a déficit severo."""
    nombre = "GOTEO"

    def calcular_duracion(self, duracion_solicitada_min: int, humedad_suelo: float) -> int:
        if humedad_suelo < 12.0:
            return int(duracion_solicitada_min * 1.25)
        elif humedad_suelo > 25.0:
            return int(duracion_solicitada_min * 0.75)
        return duracion_solicitada_min


class PoliticaAspersion(PoliticaRiego):
    """Estrategia de aspersión: mayor cobertura por unidad de tiempo."""
    nombre = "ASPERSION"

    def calcular_duracion(self, duracion_solicitada_min: int, humedad_suelo: float) -> int:
        return int(duracion_solicitada_min * 0.8)


class PoliticaDeficitarioMajes(PoliticaRiego):
    """Estrategia de Riego Deficitario Controlado (RDC) para estrés hídrico regulado en Majes."""
    nombre = "DEFICITARIO"

    def calcular_duracion(self, duracion_solicitada_min: int, humedad_suelo: float) -> int:
        return int(duracion_solicitada_min * 0.6)


class FabricaPoliticas:
    """Fábrica y registro de estrategias de riego."""

    def __init__(self):
        self._politicas: Dict[str, Any] = {
            "GOTEO": PoliticaGoteo,
            "ASPERSION": PoliticaAspersion,
            "DEFICITARIO": PoliticaDeficitarioMajes,
        }

    def registrar(self, nombre: str, clase_politica: Any) -> None:
        self._politicas[nombre.upper()] = clase_politica

    def crear(self, nombre: str) -> PoliticaRiego:
        nom_upper = nombre.upper()
        if nom_upper not in self._politicas:
            raise ValueError(f"Política de riego no soportada: {nombre}")
        clase = self._politicas[nom_upper]
        return clase() if isinstance(clase, type) else clase
