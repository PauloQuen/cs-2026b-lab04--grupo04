"""
Versión 'antes' del flujo crítico de riego en ChacraSmart Majes (E1).
Código ingenuo y acoplado, desarrollado para cumplir rápidamente con el sprint.
Presenta múltiples olores de código (God Method, Shotgun Surgery, violación de OCP y DIP).
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

from src.valvulas_riego.externos import (
    RainBirdControllerSDK,
    HunterProC_SDK,
    TuyaZigbeeRelaySDK,
    ServicioSMSPeru,
    ClienteLLMSimulado,
)


@dataclass
class Valvula:
    id: str
    nombre: str
    parcela_id: str
    apertura_maxima_min: int = 60
    estado: str = "CERRADA"
    ack_operacion: Optional[str] = None


class ServicioRiego:
    """Servicio monolítico antes de refactorizar."""

    def __init__(
        self,
        rainbird: Optional[RainBirdControllerSDK] = None,
        hunter: Optional[HunterProC_SDK] = None,
        tuya: Optional[TuyaZigbeeRelaySDK] = None,
        sms: Optional[ServicioSMSPeru] = None,
        llm: Optional[ClienteLLMSimulado] = None,
    ):
        self.rainbird = rainbird or RainBirdControllerSDK()
        self.hunter = hunter or HunterProC_SDK()
        self.tuya = tuya or TuyaZigbeeRelaySDK()
        self.sms = sms or ServicioSMSPeru()
        self.llm = llm or ClienteLLMSimulado()
        self.eventos: List[str] = []

    def ejecutar_orden_riego(
        self,
        valvula: Valvula,
        hardware_tipo: str,
        duracion_min: int,
        politica_tipo: str = "GOTEO",
        celular: str = "959123456",
        humedad: float = 15.0,
    ) -> str:
        # Validación de estados con condicionales anidados
        if valvula.estado != "CERRADA":
            if valvula.estado == "FALLA":
                raise ValueError("La válvula está en falla segura; requiere técnico")
            elif valvula.estado == "ABIERTA":
                raise ValueError("La válvula ya se encuentra abierta")
            elif valvula.estado == "ABRIENDO":
                raise ValueError("La válvula ya tiene apertura en progreso")
            elif valvula.estado == "CERRANDO":
                raise ValueError("La válvula se encuentra en proceso de cierre")
            else:
                raise ValueError(f"Estado de válvula no válido: {valvula.estado}")

        # QA-01 / ADR-003: Límite máximo de seguridad física
        if duracion_min > valvula.apertura_maxima_min:
            raise ValueError("Duración mayor que el máximo seguro de apertura")

        # Cálculo de duración según política de riego con if/elif
        duracion_ajustada = duracion_min
        if politica_tipo == "GOTEO":
            if humedad < 12.0:
                duracion_ajustada = int(duracion_min * 1.25)
            elif humedad > 25.0:
                duracion_ajustada = int(duracion_min * 0.75)
        elif politica_tipo == "ASPERSION":
            duracion_ajustada = int(duracion_min * 0.8)
        elif politica_tipo == "DEFICITARIO":
            duracion_ajustada = int(duracion_min * 0.6)
        else:
            raise ValueError(f"Política de riego no soportada: {politica_tipo}")

        # Asegurar que el ajuste no sobrepase la seguridad del actuador
        duracion_final = min(duracion_ajustada, valvula.apertura_maxima_min)

        valvula.estado = "ABRIENDO"
        aprobado = False
        ack = None

        # Bloque de hardware con if/elif y reintentos duplicados
        if hardware_tipo == "RAINBIRD":
            for intento in range(3):
                try:
                    resp = self.rainbird.abrir_valvula(valvula.id, duracion_final)
                    aprobado = (resp.get("status") == 200)
                    ack = resp.get("job_id")
                    break
                except TimeoutError:
                    if intento == 2:
                        aprobado = False
        elif hardware_tipo == "HUNTER":
            for intento in range(3):
                try:
                    # Hunter opera en segundos
                    ok, code = self.hunter.execute_irrigation(int(valvula.id), duracion_final * 60)
                    aprobado = ok
                    ack = code
                    break
                except TimeoutError:
                    if intento == 2:
                        aprobado = False
        elif hardware_tipo == "TUYA":
            for intento in range(3):
                try:
                    code = self.tuya.set_switch(valvula.id, True, duracion_final * 60)
                    aprobado = (code in (200, 204))
                    ack = f"TUYA_{code}"
                    break
                except TimeoutError:
                    if intento == 2:
                        aprobado = False
        else:
            raise ValueError(f"Hardware de válvula no soportado: {hardware_tipo}")

        if aprobado:
            valvula.estado = "ABIERTA"
            valvula.ack_operacion = ack
            self.eventos.append(f"sms:{celular}:Riego iniciado en valvula {valvula.id}")
            self.eventos.append(f"auditoria:{valvula.id}:APERTURA_EXITOSA")
            self.eventos.append(f"telemetria:{valvula.id}:{duracion_final}min")
        else:
            # Falla segura: QA-01 / ADR-003
            valvula.estado = "FALLA"
            self.eventos.append(f"alerta:{celular}:Falla en valvula {valvula.id}")
            self.eventos.append(f"seguridad:{valvula.id}:CIERRE_SEGURO_AUTOMATICO")

        return valvula.estado

    def cerrar_valvula(self, valvula: Valvula, hardware_tipo: str, celular: str = "959123456") -> str:
        if valvula.estado not in ("ABIERTA", "ABRIENDO"):
            raise ValueError("Solo se puede cerrar una válvula abierta o abriendo")

        valvula.estado = "CERRANDO"
        cerrado = False

        if hardware_tipo == "RAINBIRD":
            for intento in range(3):
                try:
                    resp = self.rainbird.cerrar_valvula(valvula.id)
                    cerrado = (resp.get("status") == 200)
                    break
                except TimeoutError:
                    if intento == 2:
                        cerrado = False
        elif hardware_tipo == "HUNTER":
            for intento in range(3):
                try:
                    ok, _ = self.hunter.stop_irrigation(int(valvula.id))
                    cerrado = ok
                    break
                except TimeoutError:
                    if intento == 2:
                        cerrado = False
        elif hardware_tipo == "TUYA":
            for intento in range(3):
                try:
                    code = self.tuya.set_switch(valvula.id, False, 0)
                    cerrado = (code in (200, 204))
                    break
                except TimeoutError:
                    if intento == 2:
                        cerrado = False
        else:
            raise ValueError(f"Hardware de válvula no soportado: {hardware_tipo}")

        if cerrado:
            valvula.estado = "CERRADA"
            self.eventos.append(f"sms:{celular}:Valvula {valvula.id} cerrada")
            self.eventos.append(f"auditoria:{valvula.id}:CIERRE_CONFIRMADO")
        else:
            valvula.estado = "FALLA"
            self.eventos.append(f"alerta:{celular}:Alerta actuador trabado en {valvula.id}")

        return valvula.estado

    def explicar_recomendacion_ia(self, cultivo: str, humedad: float) -> str:
        """Llamada a IA sin aislamiento: sin caché, sin guardrails, acoplada al cliente."""
        prompt = f"Explica la recomendacion de riego para cultivo {cultivo} con humedad de suelo {humedad}%."
        return self.llm.generar(prompt)
