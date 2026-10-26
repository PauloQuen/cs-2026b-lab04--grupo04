"""
Pruebas unitarias que demuestran y verifican cada uno de los patrones GoF aplicados (E2-E5).
Demuestra la adhesión al Principio Abierto/Cerrado (OCP), robustez de estados,
desacoplamiento de eventos y protección mediante guardrails de IA.
"""
import pytest

from src.valvulas_riego.estados import (
    Valvula,
    EstadoCerrada,
    EstadoAbriendo,
    EstadoAbierta,
    EstadoCerrando,
    EstadoFalla,
    TransicionEstadoInvalida,
)
from src.valvulas_riego.actuadores import (
    ControladorValvula,
    ResultadoOperacion,
    FabricaControladores,
    ConReintentos,
    AdaptadorRainBird,
)
from src.valvulas_riego.politicas import (
    PoliticaRiego,
    FabricaPoliticas,
    PoliticaGoteo,
)
from src.valvulas_riego.eventos import (
    PublicadorEventos,
    Suscriptor,
)
from src.valvulas_riego.comandos import (
    ComandoAbrirValvula,
    ComandoCerrarValvula,
    InvocadorRiego,
)
from src.valvulas_riego.ia import (
    ProveedorLLM,
    ConCache,
    GuardrailMaximoRiego,
    GuardrailConsistenciaHumedad,
    GuardrailLenguajeCampesino,
    ServicioRecomendacionIA,
)
from src.valvulas_riego.externos import (
    RainBirdControllerSDK,
    ClienteLLMSimulado,
)
from src.valvulas_riego.servicio import ServicioRiego


# ===========================================================================
# E2: PATRONES STRATEGY + ADAPTER + FACTORY (Principio Abierto/Cerrado)
# ===========================================================================
def test_open_closed_nuevo_hardware_sin_modificar_servicio():
    """Demuestra OCP: se registra un nuevo controlador IoT ESP32 sin tocar ServicioRiego."""
    class AdaptadorESP32Majes(ControladorValvula):
        def __init__(self):
            self.ordenes_recibidas = []

        def abrir(self, valvula_id: str, duracion_min: int) -> ResultadoOperacion:
            self.ordenes_recibidas.append(f"OPEN:{valvula_id}:{duracion_min}")
            return ResultadoOperacion(aprobado=True, ack="ACK_ESP32_OK", mensaje="ESP32 Majes OK")

        def cerrar(self, valvula_id: str) -> ResultadoOperacion:
            self.ordenes_recibidas.append(f"CLOSE:{valvula_id}")
            return ResultadoOperacion(aprobado=True, ack="ACK_ESP32_OFF", mensaje="ESP32 Cierre")

    # Registro dinámico en la fábrica
    fabrica = FabricaControladores()
    fabrica.registrar("ESP32_MAJES", AdaptadorESP32Majes)

    servicio = ServicioRiego(fabrica_controladores=fabrica)
    valvula = Valvula(id="V-ESP", nombre="Válvula Experimental", parcela_id="Lote 9")

    estado = servicio.ejecutar_orden_riego(valvula, "ESP32_MAJES", 15)
    assert estado == "ABIERTA"
    assert valvula.ack_operacion == "ACK_ESP32_OK"


def test_open_closed_nueva_politica_riego_sin_modificar_servicio():
    """Demuestra OCP en Strategy: se añade 'MICROASPERSION' sin alterar el servicio."""
    class PoliticaMicroaspersion(PoliticaRiego):
        nombre = "MICROASPERSION"
        def calcular_duracion(self, duracion_solicitada_min: int, humedad_suelo: float) -> int:
            return int(duracion_solicitada_min * 0.7)

    fabrica_pol = FabricaPoliticas()
    fabrica_pol.registrar("MICROASPERSION", PoliticaMicroaspersion)

    servicio = ServicioRiego(fabrica_politicas=fabrica_pol)
    valvula = Valvula(id="V-MICRO", nombre="Microaspersor", parcela_id="Lote 4")
    servicio.ejecutar_orden_riego(valvula, "RAINBIRD", 30, politica_tipo="MICROASPERSION")
    assert "telemetria:V-MICRO:21min" in servicio.eventos  # 30 * 0.7 = 21


# ===========================================================================
# E3: PATRÓN STATE (Ciclo de Vida de Valvula y Falla Segura QA-01)
# ===========================================================================
def test_state_transiciones_validas_completas():
    """Verifica el ciclo completo: CERRADA -> ABRIENDO -> ABIERTA -> CERRANDO -> CERRADA."""
    v = Valvula(id="V-1", nombre="V-1", parcela_id="P-1")
    assert v.estado == "CERRADA"
    assert isinstance(v.estado_objeto, EstadoCerrada)

    v.abrir(30)
    assert v.estado == "ABRIENDO"
    assert isinstance(v.estado_objeto, EstadoAbriendo)

    v.confirmar_apertura()
    assert v.estado == "ABIERTA"
    assert isinstance(v.estado_objeto, EstadoAbierta)

    v.cerrar()
    assert v.estado == "CERRANDO"
    assert isinstance(v.estado_objeto, EstadoCerrando)

    v.confirmar_cierre()
    assert v.estado == "CERRADA"
    assert isinstance(v.estado_objeto, EstadoCerrada)


def test_state_impide_transiciones_invalidas():
    """Verifica que transiciones prohibidas por el modelo formal lancen TransicionEstadoInvalida."""
    v = Valvula(id="V-2", nombre="V-2", parcela_id="P-1")
    # En estado CERRADA, no se puede confirmar apertura
    with pytest.raises(TransicionEstadoInvalida):
        v.confirmar_apertura()

    # En estado CERRADA, no se puede cerrar
    with pytest.raises(TransicionEstadoInvalida):
        v.cerrar()

    # Abrir a ABRIENDO
    v.abrir(20)
    # En ABRIENDO, no se puede volver a llamar abrir
    with pytest.raises(TransicionEstadoInvalida):
        v.abrir(10)


def test_state_falla_segura_es_terminal():
    """QA-01 / ADR-003: una válvula en FALLA queda bloqueada ante cualquier comando."""
    v = Valvula(id="V-FAIL", nombre="V-Falla", parcela_id="P-1", estado_inicial=EstadoFalla())
    assert v.estado == "FALLA"

    with pytest.raises(TransicionEstadoInvalida):
        v.abrir(15)

    with pytest.raises(TransicionEstadoInvalida):
        v.cerrar()

    with pytest.raises(TransicionEstadoInvalida):
        v.confirmar_apertura()


# ===========================================================================
# E4: OBSERVER, DECORATOR Y COMMAND
# ===========================================================================
def test_observer_nuevo_suscriptor_sin_tocar_servicio():
    """Demuestra Observer: suscriptor de panel web recibe eventos sin modificar el servicio."""
    class PanelSupervisorWeb(Suscriptor):
        def __init__(self):
            self.notificaciones_dashboard = []

        def actualizar(self, evento: str, datos: dict) -> None:
            self.notificaciones_dashboard.append(f"DASHBOARD:{evento}:{datos.get('valvula_id')}")

    panel = PanelSupervisorWeb()
    publicador = PublicadorEventos()
    publicador.suscribir("riego_iniciado", panel)

    servicio = ServicioRiego(publicador=publicador)
    valvula = Valvula(id="V-OBS", nombre="Válvula Test", parcela_id="P-1")
    servicio.ejecutar_orden_riego(valvula, "RAINBIRD", 10)

    assert "DASHBOARD:riego_iniciado:V-OBS" in panel.notificaciones_dashboard


def test_decorator_reintentos_controlador_valvula():
    """Demuestra Decorator en actuadores: ConReintentos reintenta llamadas ante fallo transitorio."""
    rainbird = RainBirdControllerSDK(fallas=2)
    adaptador_base = AdaptadorRainBird(rainbird)
    actuador_decorado = ConReintentos(adaptador_base, max_intentos=3)

    res = actuador_decorado.abrir("V-DEC", 15)
    assert res.aprobado is True
    assert actuador_decorado.intentos_realizados == 3


def test_command_invocador_mantiene_historial():
    """Demuestra Command: InvocadorRiego registra auditoría cronológica de órdenes."""
    invocador = InvocadorRiego()
    valvula = Valvula(id="V-CMD", nombre="Válvula Command", parcela_id="P-1")
    controlador = AdaptadorRainBird(RainBirdControllerSDK())

    cmd_abrir = ComandoAbrirValvula(valvula, controlador, 20)
    res_abrir = invocador.ejecutar_comando(cmd_abrir)
    assert res_abrir.aprobado is True
    assert valvula.estado == "ABIERTA"

    cmd_cerrar = ComandoCerrarValvula(valvula, controlador)
    res_cerrar = invocador.ejecutar_comando(cmd_cerrar)
    assert res_cerrar.aprobado is True
    assert valvula.estado == "CERRADA"

    assert len(invocador.historial) == 2
    assert invocador.historial[0] == cmd_abrir
    assert invocador.historial[1] == cmd_cerrar


# ===========================================================================
# E5: AISLAMIENTO DE IA (Strategy, Decorator Caché y Guardrails Chain)
# ===========================================================================
def test_decorator_cache_evita_llamadas_repetidas_al_llm():
    """Verifica que el decorador ConCache almacene la respuesta y evite re-ejecutar el LLM."""
    llm = ClienteLLMSimulado(respuesta_predefinida="Recomendación agrícola para Majes.")
    adaptador = ConCache(AdaptadorRainBird() if False else None)  # tipo check
    from src.valvulas_riego.ia import AdaptadorLLMSimulado
    prov = ConCache(AdaptadorLLMSimulado(llm))

    r1 = prov.completar("prompt-1")
    r2 = prov.completar("prompt-1")

    assert r1 == "Recomendación agrícola para Majes."
    assert r2 == r1
    assert llm.llamadas == 1  # Solo 1 llamada física al modelo!
    assert prov.cache_hits == 1
    assert prov.cache_misses == 1


def test_chain_guardrails_bloquea_sobre_riego():
    """QA-01: Guardrail bloquea recomendación que sugiera regar más tiempo del seguro."""
    llm = ClienteLLMSimulado(
        respuesta_predefinida="Se aconseja encarecidamente regar por 95 minutos en esta época."
    )
    from src.valvulas_riego.ia import AdaptadorLLMSimulado
    servicio_ia = ServicioRecomendacionIA(AdaptadorLLMSimulado(llm))

    # El límite seguro es 60 min; 95 min debe ser bloqueado por la cadena de guardrails
    with pytest.raises(ValueError, match="Guardrail Seguridad Hídrica"):
        servicio_ia.generar_explicacion(cultivo="Alfalfa", humedad=10.0, duracion_min=20, apertura_maxima_min=60)


def test_chain_guardrails_bloquea_humedad_imposible():
    """Guardrail bloquea alucinaciones de porcentajes de humedad inválidos."""
    llm = ClienteLLMSimulado(
        respuesta_predefinida="La humedad relativa del suelo es de -15.4%, peligro inminente."
    )
    from src.valvulas_riego.ia import AdaptadorLLMSimulado
    servicio_ia = ServicioRecomendacionIA(AdaptadorLLMSimulado(llm))

    with pytest.raises(ValueError, match="Guardrail Consistencia"):
        servicio_ia.generar_explicacion(cultivo="Quinua", humedad=12.0, duracion_min=15)


def test_chain_guardrails_bloquea_lenguaje_prohibido():
    """Guardrail ético bloquea promesas falsas o publicidad no verificada."""
    llm = ClienteLLMSimulado(
        respuesta_predefinida="Con este riego tendrá cero riesgo hídrico garantizado para siempre."
    )
    from src.valvulas_riego.ia import AdaptadorLLMSimulado
    servicio_ia = ServicioRecomendacionIA(AdaptadorLLMSimulado(llm))

    with pytest.raises(ValueError, match="Guardrail Ética"):
        servicio_ia.generar_explicacion(cultivo="Cebolla", humedad=18.0, duracion_min=20)


def test_chain_guardrails_permite_respuesta_valida():
    """Verifica que una recomendación sensata pase todos los eslabones de la cadena."""
    llm = ClienteLLMSimulado(
        respuesta_predefinida="Recomendación técnica: Regar durante 25 min para alcanzar 22% de humedad."
    )
    from src.valvulas_riego.ia import AdaptadorLLMSimulado
    servicio_ia = ServicioRecomendacionIA(AdaptadorLLMSimulado(llm))

    resultado = servicio_ia.generar_explicacion(
        cultivo="Ajo", humedad=14.0, duracion_min=25, apertura_maxima_min=60
    )
    assert "25 min" in resultado
    assert "Recomendación técnica" in resultado
