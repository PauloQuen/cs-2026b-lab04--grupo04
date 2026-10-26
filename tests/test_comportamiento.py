"""
Pruebas de caracterización para el flujo crítico de ChacraSmart Majes (E1).
Red de seguridad: las mismas pruebas se ejecutan sobre la versión 'antes' (monolítica)
y la versión 'después' (refactorizada con patrones GoF) usando un fixture parametrizado.
"""
import importlib
import pytest

from src.valvulas_riego.externos import (
    RainBirdControllerSDK,
    HunterProC_SDK,
    TuyaZigbeeRelaySDK,
    ServicioSMSPeru,
    ClienteLLMSimulado,
)


@pytest.fixture(params=["src.valvulas_riego.antes.servicio", "src.valvulas_riego.servicio"])
def m(request):
    """Fixture que carga dinámicamente el módulo antes o después."""
    return importlib.import_module(request.param)


def crear_valvula(m, id="101", nombre="Válvula Sector A", max_min=60, estado="CERRADA"):
    return m.Valvula(
        id=id,
        nombre=nombre,
        parcela_id="parcela-majes-01",
        apertura_maxima_min=max_min,
        estado=estado
    )


# 1. Éxito con actuador RainBird y eventos generados
def test_riego_rainbird_exitoso_publica_eventos(m):
    valvula = crear_valvula(m, id="V-01")
    servicio = m.ServicioRiego()
    estado_final = servicio.ejecutar_orden_riego(
        valvula=valvula,
        hardware_tipo="RAINBIRD",
        duracion_min=30,
        politica_tipo="GOTEO",
        celular="959123456",
        humedad=15.0
    )
    assert estado_final == "ABIERTA"
    assert valvula.estado == "ABIERTA"
    assert "sms:959123456:Riego iniciado en valvula V-01" in servicio.eventos
    assert "auditoria:V-01:APERTURA_EXITOSA" in servicio.eventos
    assert "telemetria:V-01:30min" in servicio.eventos


# 2. Éxito con actuador Hunter (verificando conversión y ack)
def test_riego_hunter_exitoso_con_conversion(m):
    hunter = HunterProC_SDK()
    valvula = crear_valvula(m, id="12")
    servicio = m.ServicioRiego(hunter=hunter)
    estado_final = servicio.ejecutar_orden_riego(
        valvula=valvula,
        hardware_tipo="HUNTER",
        duracion_min=20,
        politica_tipo="GOTEO",
        celular="959111222"
    )
    assert estado_final == "ABIERTA"
    assert hunter.llamadas == 1
    assert "sms:959111222:Riego iniciado en valvula 12" in servicio.eventos


# 3. Resiliencia: reintenta tras 2 timeouts y aprueba en el 3er intento
def test_reintenta_tras_dos_timeouts(m):
    rainbird = RainBirdControllerSDK(fallas=2)
    valvula = crear_valvula(m, id="V-RETRY")
    servicio = m.ServicioRiego(rainbird=rainbird)
    estado = servicio.ejecutar_orden_riego(valvula, "RAINBIRD", 25)
    assert estado == "ABIERTA"
    assert rainbird.llamadas == 3


# 4. Falla segura ante desconexión total (3 fallas consecutivas)
def test_falla_segura_tras_tres_timeouts(m):
    rainbird = RainBirdControllerSDK(fallas=3)
    valvula = crear_valvula(m, id="V-FAIL")
    servicio = m.ServicioRiego(rainbird=rainbird)
    estado = servicio.ejecutar_orden_riego(valvula, "RAINBIRD", 25)
    assert estado == "FALLA"
    assert valvula.estado == "FALLA"
    assert "alerta:959123456:Falla en valvula V-FAIL" in servicio.eventos
    assert "seguridad:V-FAIL:CIERRE_SEGURO_AUTOMATICO" in servicio.eventos


# 5. Ajuste agronómico por política de riego (Goteo aumenta duración con baja humedad)
def test_politica_goteo_ajuste_humedad_baja(m):
    valvula = crear_valvula(m, id="V-HUM", max_min=50)
    servicio = m.ServicioRiego()
    servicio.ejecutar_orden_riego(
        valvula=valvula,
        hardware_tipo="RAINBIRD",
        duracion_min=20,
        politica_tipo="GOTEO",
        humedad=10.0  # < 12% incrementa 25% -> 25 min
    )
    assert "telemetria:V-HUM:25min" in servicio.eventos


# 6. Regla de seguridad física QA-01: Duración solicitada excede límite seguro
def test_duracion_excesiva_rechazada_inmediatamente(m):
    valvula = crear_valvula(m, id="V-MAX", max_min=45)
    servicio = m.ServicioRiego()
    with pytest.raises(ValueError, match="máximo seguro"):
        servicio.ejecutar_orden_riego(valvula, "RAINBIRD", 90)


# 7. Transición inválida: No se puede abrir una válvula ya abierta o en falla
def test_intento_abrir_valvula_ya_abierta_rechazado(m):
    valvula = crear_valvula(m, id="V-OPEN", estado="ABIERTA")
    servicio = m.ServicioRiego()
    with pytest.raises(ValueError):
        servicio.ejecutar_orden_riego(valvula, "RAINBIRD", 30)


# 8. Cierre exitoso de válvula abierta
def test_cierre_valvula_exitoso(m):
    valvula = crear_valvula(m, id="V-CLOSE", estado="ABIERTA")
    servicio = m.ServicioRiego()
    estado = servicio.cerrar_valvula(valvula, "RAINBIRD", celular="959999888")
    assert estado == "CERRADA"
    assert valvula.estado == "CERRADA"
    assert "sms:959999888:Valvula V-CLOSE cerrada" in servicio.eventos
    assert "auditoria:V-CLOSE:CIERRE_CONFIRMADO" in servicio.eventos


# 9. Hardware no soportado lanza excepción
def test_hardware_desconocido_lanza_error(m):
    valvula = crear_valvula(m, id="V-UNK")
    servicio = m.ServicioRiego()
    with pytest.raises(ValueError, match="no soportado"):
        servicio.ejecutar_orden_riego(valvula, "MOTOROLA_IRRIGATION", 30)


# 10. Explicación de IA genera respuesta textual
def test_ia_recomendacion_basica(m):
    llm = ClienteLLMSimulado(respuesta_predefinida="Recomendación: Aplicar 20 min de riego en Majes.")
    servicio = m.ServicioRiego(llm=llm)
    texto = servicio.explicar_recomendacion_ia(cultivo="Palto", humedad=14.0)
    assert "Recomendación: Aplicar 20 min" in texto
