"""
Implementación del patrón Observer para eventos de campo y notificaciones (E4).
Desacopla la lógica de riego de los canales de comunicación y auditoría IoT.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, List, Any


class Suscriptor(ABC):
    """OBSERVER: Interfaz que deben implementar todos los observadores de eventos."""

    @abstractmethod
    def actualizar(self, evento: str, datos: Dict[str, Any]) -> None:
        """Método de callback invocado cuando ocurre un evento de interés."""
        ...


class PublicadorEventos:
    """SUBJECT / OBSERVABLE: Gestiona suscripciones y difunde eventos a los interesados."""

    def __init__(self):
        self._suscriptores: Dict[str, List[Suscriptor]] = {}

    def suscribir(self, evento: str, suscriptor: Suscriptor) -> None:
        self._suscriptores.setdefault(evento, []).append(suscriptor)

    def desuscribir(self, evento: str, suscriptor: Suscriptor) -> None:
        if evento in self._suscriptores and suscriptor in self._suscriptores[evento]:
            self._suscriptores[evento].remove(suscriptor)

    def publicar(self, evento: str, datos: Dict[str, Any]) -> None:
        for s in self._suscriptores.get(evento, []):
            s.actualizar(evento, datos)


# ---------------------------------------------------------------------------
# SUSCRIPTORES CONCRETOS (E4)
# ---------------------------------------------------------------------------
class NotificadorAgricultorSMS(Suscriptor):
    """Envía SMS informativos o de alerta al celular del agricultor en Majes (RF-05)."""

    def __init__(self, bandeja_salida: List[str]):
        self.bandeja = bandeja_salida

    def actualizar(self, evento: str, datos: Dict[str, Any]) -> None:
        celular = datos.get("celular", "")
        valvula_id = datos.get("valvula_id", "")
        if evento == "riego_iniciado":
            self.bandeja.append(f"sms:{celular}:Riego iniciado en valvula {valvula_id}")
        elif evento == "valvula_cerrada":
            self.bandeja.append(f"sms:{celular}:Valvula {valvula_id} cerrada")
        elif evento == "falla_valvula":
            self.bandeja.append(f"alerta:{celular}:Falla en valvula {valvula_id}")
        elif evento == "falla_cierre":
            self.bandeja.append(f"alerta:{celular}:Alerta actuador trabado en {valvula_id}")


class MonitorAuditoriaIoT(Suscriptor):
    """Registra eventos de auditoría inmutable para trazabilidad de uso del agua."""

    def __init__(self, bandeja_salida: List[str]):
        self.bandeja = bandeja_salida

    def actualizar(self, evento: str, datos: Dict[str, Any]) -> None:
        valvula_id = datos.get("valvula_id", "")
        if evento == "riego_iniciado":
            self.bandeja.append(f"auditoria:{valvula_id}:APERTURA_EXITOSA")
        elif evento == "valvula_cerrada":
            self.bandeja.append(f"auditoria:{valvula_id}:CIERRE_CONFIRMADO")
        elif evento == "falla_valvula":
            self.bandeja.append(f"seguridad:{valvula_id}:CIERRE_SEGURO_AUTOMATICO")


class MonitorTelemetria(Suscriptor):
    """Monitorea métricas operativas de duración y caudal."""

    def __init__(self, bandeja_salida: List[str]):
        self.bandeja = bandeja_salida

    def actualizar(self, evento: str, datos: Dict[str, Any]) -> None:
        valvula_id = datos.get("valvula_id", "")
        if evento == "riego_iniciado":
            duracion = datos.get("duracion_min", 0)
            self.bandeja.append(f"telemetria:{valvula_id}:{duracion}min")
