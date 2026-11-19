"""Pruebas objetivas que reproducen los 3 issues de ChacraSmart Majes (Lab 10, E1)."""
import pytest

from src.valvulas_riego.operaciones_campo import (
    iniciar_riego_en_turno,
    procesar_latido_controlador,
    registrar_lectura_humedad,
)


def test_issue_01_valvula_cierra_al_perder_conexion():
    """QA-01 / ADR-003: al expirar el tiempo, cierra localmente aunque no haya señal."""
    res = procesar_latido_controlador(
        valvula_abierta=True,
        segundos_sin_conexion=45,
        tiempo_programado_s=600,
        segundos_transcurridos_s=602,
    )
    assert res["cerrada"] is True
    assert res["estado"] == "CERRADA"


def test_issue_02_bloquea_riego_en_turno_ajeno():
    """QA-05 / ADR-008: impide iniciar riego en turno o parcela de otro agricultor."""
    with pytest.raises(PermissionError, match="No autorizado"):
        iniciar_riego_en_turno(
            parcela_propietario_id="AGR-01",
            solicitante_id="AGR-99",
            turno_asignado_id="AGR-01",
            volumen_m3=12.0,
        )

    ok = iniciar_riego_en_turno("AGR-01", "AGR-01", "AGR-01", 12.0)
    assert ok["autorizado"] is True


def test_issue_03_rechaza_humedad_negativa_o_imposible():
    """RF-01: rechaza porcentajes de humedad < 0 % o > 100 %."""
    with pytest.raises(ValueError, match="rango"):
        registrar_lectura_humedad("PARC-01", -12.5)

    with pytest.raises(ValueError, match="rango"):
        registrar_lectura_humedad("PARC-01", 135.0)

    ok = registrar_lectura_humedad("PARC-01", 24.5)
    assert ok["humedad_pct"] == 24.5
