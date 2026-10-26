"""
ServicioRiego refactorizado con patrones GoF (Laboratorio 07).
Integra:
- Strategy (PoliticaRiego) + Factory (FabricaPoliticas)
- Adapter (Adaptadores RainBird/Hunter/Tuya) + Factory (FabricaControladores)
- State (Ciclo de vida de la entidad Valvula)
- Observer (PublicadorEventos con múltiples suscriptores)
- Decorator (ConReintentos y ConCache)
- Command (ComandoAbrirValvula, ComandoCerrarValvula e InvocadorRiego)
- Chain of Responsibility (Guardrails deterministas de seguridad hídrica para IA)
"""
from __future__ import annotations
from typing import Optional, List

from src.valvulas_riego.estados import Valvula
from src.valvulas_riego.actuadores import (
    FabricaControladores,
    crear_fabrica_por_defecto,
)
from src.valvulas_riego.politicas import (
    FabricaPoliticas,
)
from src.valvulas_riego.eventos import (
    PublicadorEventos,
    NotificadorAgricultorSMS,
    MonitorAuditoriaIoT,
    MonitorTelemetria,
)
from src.valvulas_riego.comandos import (
    ComandoAbrirValvula,
    ComandoCerrarValvula,
    InvocadorRiego,
)
from src.valvulas_riego.ia import (
    ProveedorLLM,
    AdaptadorLLMSimulado,
    ConCache,
    ServicioRecomendacionIA,
)
from src.valvulas_riego.externos import (
    RainBirdControllerSDK,
    HunterProC_SDK,
    TuyaZigbeeRelaySDK,
    ServicioSMSPeru,
    ClienteLLMSimulado,
)


class ServicioRiego:
    """Servicio orquestador desacoplado, limpio y extensible (Open-Closed Principle)."""

    def __init__(
        self,
        rainbird: Optional[RainBirdControllerSDK] = None,
        hunter: Optional[HunterProC_SDK] = None,
        tuya: Optional[TuyaZigbeeRelaySDK] = None,
        sms: Optional[ServicioSMSPeru] = None,
        llm: Optional[ClienteLLMSimulado] = None,
        fabrica_controladores: Optional[FabricaControladores] = None,
        fabrica_politicas: Optional[FabricaPoliticas] = None,
        publicador: Optional[PublicadorEventos] = None,
    ):
        # 1. Fábrica de controladores con adaptadores y reintentos (Strategy + Adapter + Factory)
        self.fabrica_controladores = fabrica_controladores or crear_fabrica_por_defecto(
            rainbird_sdk=rainbird,
            hunter_sdk=hunter,
            tuya_sdk=tuya,
        )

        # 2. Fábrica de políticas agronómicas (Strategy + Factory)
        self.fabrica_politicas = fabrica_politicas or FabricaPoliticas()

        # 3. Sistema de eventos (Observer)
        self.publicador = publicador or PublicadorEventos()
        self.eventos: List[str] = []

        # Suscripción de observadores estándar
        self.publicador.suscribir("riego_iniciado", NotificadorAgricultorSMS(self.eventos))
        self.publicador.suscribir("riego_iniciado", MonitorAuditoriaIoT(self.eventos))
        self.publicador.suscribir("riego_iniciado", MonitorTelemetria(self.eventos))

        self.publicador.suscribir("valvula_cerrada", NotificadorAgricultorSMS(self.eventos))
        self.publicador.suscribir("valvula_cerrada", MonitorAuditoriaIoT(self.eventos))

        self.publicador.suscribir("falla_valvula", NotificadorAgricultorSMS(self.eventos))
        self.publicador.suscribir("falla_valvula", MonitorAuditoriaIoT(self.eventos))

        self.publicador.suscribir("falla_cierre", NotificadorAgricultorSMS(self.eventos))

        # 4. Invocador de órdenes de campo (Command)
        self.invocador = InvocadorRiego()

        # 5. Componente de IA aislado (Strategy + Adapter + Decorator + Chain of Responsibility)
        proveedor_base = AdaptadorLLMSimulado(llm or ClienteLLMSimulado())
        self.proveedor_ia_cache = ConCache(proveedor_base)
        self.servicio_ia = ServicioRecomendacionIA(self.proveedor_ia_cache)

    def ejecutar_orden_riego(
        self,
        valvula: Valvula,
        hardware_tipo: str,
        duracion_min: int,
        politica_tipo: str = "GOTEO",
        celular: str = "959123456",
        humedad: float = 15.0,
    ) -> str:
        """Flujo crítico refactorizado: complejidad ciclomática reducida drásticamente."""
        # Validación de hardware previo a cualquier cambio de estado (resuelve bug del 'antes')
        controlador = self.fabrica_controladores.crear(hardware_tipo)
        politica = self.fabrica_politicas.crear(politica_tipo)

        # QA-01 / ADR-003: Límite físico de seguridad
        if duracion_min > valvula.apertura_maxima_min:
            raise ValueError("Duración mayor que el máximo seguro de apertura")

        # Cálculo de duración mediante la estrategia agronómica
        duracion_ajustada = politica.calcular_duracion(duracion_min, humedad)
        duracion_final = min(duracion_ajustada, valvula.apertura_maxima_min)

        # Creación y despacho del comando (Command + State)
        comando = ComandoAbrirValvula(valvula, controlador, duracion_final)
        resultado = self.invocador.ejecutar_comando(comando)

        # Publicación a observadores desacoplados (Observer)
        if resultado.aprobado:
            self.publicador.publicar("riego_iniciado", {
                "valvula_id": valvula.id,
                "celular": celular,
                "duracion_min": duracion_final,
                "ack": resultado.ack,
            })
        else:
            self.publicador.publicar("falla_valvula", {
                "valvula_id": valvula.id,
                "celular": celular,
                "motivo": resultado.mensaje,
            })

        return valvula.estado

    def cerrar_valvula(self, valvula: Valvula, hardware_tipo: str, celular: str = "959123456") -> str:
        """Cierre controlado o de emergencia sobre la válvula."""
        controlador = self.fabrica_controladores.crear(hardware_tipo)
        comando = ComandoCerrarValvula(valvula, controlador)
        resultado = self.invocador.ejecutar_comando(comando)

        if resultado.aprobado:
            self.publicador.publicar("valvula_cerrada", {"valvula_id": valvula.id, "celular": celular})
        else:
            self.publicador.publicar("falla_cierre", {"valvula_id": valvula.id, "celular": celular})

        return valvula.estado

    def explicar_recomendacion_ia(self, cultivo: str, humedad: float) -> str:
        """Explicación generativa protegida por caché y guardrails."""
        return self.servicio_ia.generar_explicacion(cultivo, humedad, 30)
