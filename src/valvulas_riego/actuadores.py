"""
Patrones Adapter, Factory y Decorator para actuadores y controladores de válvulas físicas (E2, E4).
Aísla las diferencias de protocolo (segundos vs minutos, JSON vs tuplas vs HTTP status)
detrás de una interfaz común ControladorValvula.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Type, Optional, Any

from src.valvulas_riego.externos import (
    RainBirdControllerSDK,
    HunterProC_SDK,
    TuyaZigbeeRelaySDK,
)


@dataclass
class ResultadoOperacion:
    """Objeto de transferencia de resultado unificado entre cualquier hardware de campo."""
    aprobado: bool
    ack: Optional[str] = None
    mensaje: str = ""


class ControladorValvula(ABC):
    """Target Interface (Puerto) según Clean Architecture / Hexagonal (ADR-001/002)."""

    @abstractmethod
    def abrir(self, valvula_id: str, duracion_min: int) -> ResultadoOperacion:
        """Envía el comando de apertura al actuador físico."""
        ...

    @abstractmethod
    def cerrar(self, valvula_id: str) -> ResultadoOperacion:
        """Envía el comando de cierre al actuador físico."""
        ...


# ---------------------------------------------------------------------------
# ADAPTERS (E2)
# ---------------------------------------------------------------------------
class AdaptadorRainBird(ControladorValvula):
    """ADAPTER: traduce entre la interfaz del dominio y el SDK RainBird (HTTP/JSON en minutos)."""

    def __init__(self, sdk: Optional[RainBirdControllerSDK] = None):
        self.sdk = sdk or RainBirdControllerSDK()

    def abrir(self, valvula_id: str, duracion_min: int) -> ResultadoOperacion:
        resp = self.sdk.abrir_valvula(valvula_id, duracion_min)
        aprobado = resp.get("status") == 200
        ack = resp.get("job_id")
        return ResultadoOperacion(aprobado=aprobado, ack=ack, mensaje="RainBird OK" if aprobado else "Falla RainBird")

    def cerrar(self, valvula_id: str) -> ResultadoOperacion:
        resp = self.sdk.cerrar_valvula(valvula_id)
        aprobado = resp.get("status") == 200
        return ResultadoOperacion(aprobado=aprobado, ack="RB_CLOSED", mensaje="Cierre RainBird OK" if aprobado else "Falla cierre")


class AdaptadorHunter(ControladorValvula):
    """ADAPTER: traduce a Hunter Pro-C (interfaz serial que opera en SEGUNDOS con tuplas)."""

    def __init__(self, sdk: Optional[HunterProC_SDK] = None):
        self.sdk = sdk or HunterProC_SDK()

    def abrir(self, valvula_id: str, duracion_min: int) -> ResultadoOperacion:
        # Hunter requiere segundos: conversión encapsulada en el adaptador
        duracion_segundos = duracion_min * 60
        aprobado, ack = self.sdk.execute_irrigation(int(valvula_id), duracion_segundos)
        return ResultadoOperacion(aprobado=aprobado, ack=ack, mensaje="Hunter Pro-C OK" if aprobado else "Falla serial Hunter")

    def cerrar(self, valvula_id: str) -> ResultadoOperacion:
        aprobado, ack = self.sdk.stop_irrigation(int(valvula_id))
        return ResultadoOperacion(aprobado=aprobado, ack=ack, mensaje="Cierre Hunter OK" if aprobado else "Falla cierre serial")


class AdaptadorTuya(ControladorValvula):
    """ADAPTER: traduce a relés solenoide Zigbee Tuya (HTTP status 200/204)."""

    def __init__(self, sdk: Optional[TuyaZigbeeRelaySDK] = None):
        self.sdk = sdk or TuyaZigbeeRelaySDK()

    def abrir(self, valvula_id: str, duracion_min: int) -> ResultadoOperacion:
        code = self.sdk.set_switch(valvula_id, True, duracion_min * 60)
        aprobado = code in (200, 204)
        return ResultadoOperacion(aprobado=aprobado, ack=f"TUYA_{code}", mensaje="Tuya Zigbee OK" if aprobado else "Falla Tuya")

    def cerrar(self, valvula_id: str) -> ResultadoOperacion:
        code = self.sdk.set_switch(valvula_id, False, 0)
        aprobado = code in (200, 204)
        return ResultadoOperacion(aprobado=aprobado, ack=f"TUYA_OFF_{code}", mensaje="Tuya apagado OK" if aprobado else "Falla apagado Tuya")


# ---------------------------------------------------------------------------
# DECORATOR: Reintentos transversales (E4)
# ---------------------------------------------------------------------------
class ConReintentos(ControladorValvula):
    """DECORATOR: añade política de reintentos automática ante TimeoutError
    sin modificar el adaptador de hardware ni el servicio de aplicación."""

    def __init__(self, interno: ControladorValvula, max_intentos: int = 3):
        self._interno = interno
        self.max_intentos = max_intentos
        self.intentos_realizados = 0

    def abrir(self, valvula_id: str, duracion_min: int) -> ResultadoOperacion:
        for intento in range(self.max_intentos):
            self.intentos_realizados += 1
            try:
                return self._interno.abrir(valvula_id, duracion_min)
            except TimeoutError:
                if intento == self.max_intentos - 1:
                    return ResultadoOperacion(
                        aprobado=False,
                        ack=None,
                        mensaje=f"Timeout tras {self.max_intentos} intentos en actuador"
                    )
        return ResultadoOperacion(aprobado=False, mensaje="Falla de reintentos")

    def cerrar(self, valvula_id: str) -> ResultadoOperacion:
        for intento in range(self.max_intentos):
            self.intentos_realizados += 1
            try:
                return self._interno.cerrar(valvula_id)
            except TimeoutError:
                if intento == self.max_intentos - 1:
                    return ResultadoOperacion(
                        aprobado=False,
                        ack=None,
                        mensaje=f"Timeout cierre tras {self.max_intentos} intentos"
                    )
        return ResultadoOperacion(aprobado=False, mensaje="Falla de reintentos cierre")


# ---------------------------------------------------------------------------
# FACTORY: Registro y creación desacoplada (E2 - OCP)
# ---------------------------------------------------------------------------
class FabricaControladores:
    """FACTORY con registro dinámico: materializa el Principio Abierto/Cerrado (OCP).
    Nuevos adaptadores de hardware se agregan con registrar() sin tocar el código existente."""

    def __init__(self):
        self._creadores: Dict[str, Any] = {}

    def registrar(self, tipo: str, creador: Any) -> None:
        self._creadores[tipo.upper()] = creador

    def crear(self, tipo: str, **kwargs) -> ControladorValvula:
        tipo_upper = tipo.upper()
        if tipo_upper not in self._creadores:
            raise ValueError(f"Hardware de válvula no soportado: {tipo}")
        instancia = self._creadores[tipo_upper](**kwargs)
        # Por política de resiliencia de campo (QA-01), todos los actuadores se envuelven con ConReintentos
        return ConReintentos(instancia)


def crear_fabrica_por_defecto(
    rainbird_sdk: Optional[RainBirdControllerSDK] = None,
    hunter_sdk: Optional[HunterProC_SDK] = None,
    tuya_sdk: Optional[TuyaZigbeeRelaySDK] = None,
) -> FabricaControladores:
    """Función de conveniencia que inicializa la fábrica con los 3 adaptadores estándar."""
    fabrica = FabricaControladores()
    fabrica.registrar("RAINBIRD", lambda: AdaptadorRainBird(rainbird_sdk))
    fabrica.registrar("HUNTER", lambda: AdaptadorHunter(hunter_sdk))
    fabrica.registrar("TUYA", lambda: AdaptadorTuya(tuya_sdk))
    return fabrica
