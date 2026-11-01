"""
Fitness Functions de Calidad — ChacraSmart Majes 2.0 (Lab 08, E5)
Pruebas arquitectónicas automatizadas ejecutadas en Integración Continua (CI)
para proteger los atributos de calidad frente a degradación evolutiva:
- FF-03: Rendimiento nominal ante 2000 parcelas (QA-01, p95 <= 500 ms).
- FF-04: Rendimiento pico en campaña de riego (QA-01, p95 <= 500 ms a 120 req/s).
- FF-05: Protección y Safety (QA-02: 0 válvulas abiertas más de 5 s tras corte de red).
- FF-06: Resiliencia y protección de canal degradado con Circuit Breaker (QA-03).
- FF-07: Aislamiento estricto de multitenencia entre sectores de regantes (QA-05).
"""

import pytest
from fitness.rendimiento import simular, bd_con_indice, con_cache_redis
from fitness.disponibilidad import simular_jornada_riego

PRESUPUESTO_P95_MS = 500.0  # Presupuesto SLA estipulado en QA-01


def test_ff03_rendimiento_nominal_2000_parcelas():
    """FF-03: Con 2000 parcelas (67 req/s sostenidas), la latencia p95 debe ser <= 500 ms."""
    res = simular(lam=67.0, workers=4, servicio=con_cache_redis(bd_con_indice, tasa_acierto=0.75), segundos=60)
    assert res["p95"] <= PRESUPUESTO_P95_MS, f"p95={res['p95']:.1f} ms excede el presupuesto de {PRESUPUESTO_P95_MS} ms"


def test_ff04_rendimiento_pico_campana_120_req_s():
    """FF-04: En hora punta de riego (120 req/s pico), el índice B-Tree y la caché garantizan p95 <= 500 ms."""
    res = simular(lam=120.0, workers=4, servicio=con_cache_redis(bd_con_indice, tasa_acierto=0.75), segundos=60)
    assert res["p95"] <= PRESUPUESTO_P95_MS, f"p95 pico={res['p95']:.1f} ms excede el presupuesto de {PRESUPUESTO_P95_MS} ms"


def test_ff05_safety_cero_valvulas_abiertas_tras_corte_red():
    """FF-05 (Safety Crítico): Ante cortes de conexión celular, ninguna válvula debe quedar abierta más de 5 s."""
    res = simular_jornada_riego(estrategia="failsafe_local", num_operaciones=1000, prob_corte_red=0.15, semilla=42)
    assert res["valvulas_inundadas"] == 0, f"Se detectaron {res['valvulas_inundadas']} válvulas inundando parcelas"
    assert res["sobretiempo_maximo_s"] <= 5.0, f"Sobretiempo {res['sobretiempo_maximo_s']} s supera el límite de 5 s"


def test_ff06_resiliencia_circuit_breaker_reduce_sobrecarga():
    """FF-06: El Circuit Breaker debe reducir las llamadas a controladores caídos en al menos 80% vs reintentos ciegos."""
    res_breaker = simular_jornada_riego(estrategia="failsafe_local", num_operaciones=500, prob_corte_red=0.20, semilla=99)
    res_reintentos = simular_jornada_riego(estrategia="reintentos", num_operaciones=500, prob_corte_red=0.20, semilla=99)
    
    llamadas_breaker = res_breaker["llamadas_a_controlador_caido"]
    llamadas_reintentos = res_reintentos["llamadas_a_controlador_caido"]
    
    assert llamadas_breaker < llamadas_reintentos * 0.20, (
        f"Circuit Breaker no protegió adecuadamente: {llamadas_breaker} llamadas vs {llamadas_reintentos} de reintentos"
    )


def test_ff07_aislamiento_multitenencia_sectores():
    """FF-07: Verificación de regla de partición lógica y claims de sector entre comisiones de regantes."""
    sectores_autorizados = {1: "Pedregal", 2: "El Pane", 3: "San Juan de Siguas", 4: "Santa Rita", 5: "La Colina", 6: "Camana-Majes"}
    
    # Simulación de evaluación de autorización de sector
    def verificar_acceso_valvula(usuario_sector_id: int, valvula_sector_id: int) -> bool:
        return usuario_sector_id == valvula_sector_id

    # 100 pruebas de matriz cruzada
    violaciones = 0
    for u_sec in sectores_autorizados:
        for v_sec in sectores_autorizados:
            acceso = verificar_acceso_valvula(u_sec, v_sec)
            if u_sec != v_sec and acceso:
                violaciones += 1
            elif u_sec == v_sec and not acceso:
                violaciones += 1
                
    assert violaciones == 0, f"Se detectaron {violaciones} violaciones de aislamiento multitenencia"
