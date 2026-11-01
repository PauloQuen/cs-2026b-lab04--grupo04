#!/usr/bin/env python3
"""
Simulación Monte Carlo de Disponibilidad y Safety — ChacraSmart Majes 2.0 (Lab 08, E4/E5)
Evalúa los escenarios:
- QA-02 (Safety Crítico): Cero válvulas abiertas más de 5 s tras corte de conexión.
- QA-03 (Resiliencia): Circuit Breaker evita saturar controladores caídos y outbox preserva comandos.
"""

import random
from typing import Dict, Any, List


def simular_jornada_riego(estrategia: str, num_operaciones: int = 1000, prob_corte_red: float = 0.15, semilla: int = 123) -> Dict[str, Any]:
    """
    Simula una jornada intensiva de riego en el Valle de Majes con 2000 parcelas.
    estrategia: 'centralizada' (servidor ordena cerrar), 'reintentos' (servidor reintenta), 'failsafe_local' (temporizador local + breaker)
    """
    rnd = random.Random(semilla)
    valvulas_inundadas = 0       # Válvulas que quedaron abiertas más del tiempo programado
    sobretiempo_maximo_s = 0.0   # Exceso de tiempo con válvula abierta
    comandos_perdidos = 0
    llamadas_a_controlador_caido = 0

    # Estado del circuit breaker (para estrategia failsafe_local)
    breaker_fallas = 0
    breaker_abierto = False
    umbral_breaker = 3

    for op in range(num_operaciones):
        duracion_programada_s = rnd.randint(600, 3600)  # Riego entre 10 y 60 min
        hay_corte_red = (rnd.random() < prob_corte_red)

        if hay_corte_red:
            duracion_corte_s = rnd.uniform(180, 1800)  # Corte dura entre 3 min y 30 min

            if estrategia == "centralizada":
                # El servidor debe mandar la orden de cierre. Al no haber red, la orden no llega.
                valvulas_inundadas += 1
                sobretiempo = duracion_corte_s
                sobretiempo_maximo_s = max(sobretiempo_maximo_s, sobretiempo)
                comandos_perdidos += 1
                llamadas_a_controlador_caido += 1

            elif estrategia == "reintentos":
                # Servidor reintenta 10 veces cada 5 s (50 s total)
                llamadas_a_controlador_caido += 10
                if duracion_corte_s > 50:
                    valvulas_inundadas += 1
                    sobretiempo = duracion_corte_s - 50
                    sobretiempo_maximo_s = max(sobretiempo_maximo_s, sobretiempo)
                    comandos_perdidos += 1

            elif estrategia == "failsafe_local":
                # El controlador tiene temporizador autónomo en hardware y válvula NC
                # Aunque se corte la red por 30 minutos, el temporizador local corta el relé
                # con un jitter de reloj RTC de a lo sumo 0.5 s.
                jitter_reloj = rnd.uniform(0.01, 0.45)
                # El sobretiempo jamás excede 5 segundos
                sobretiempo_maximo_s = max(sobretiempo_maximo_s, jitter_reloj)
                # Ninguna válvula queda inundada
                # Manejo de llamadas mediante Circuit Breaker + Outbox
                if breaker_abierto:
                    # No llama al controlador; guarda el comando en outbox PostgreSQL
                    pass
                else:
                    llamadas_a_controlador_caido += 1
                    breaker_fallas += 1
                    if breaker_fallas >= umbral_breaker:
                        breaker_abierto = True
        else:
            # Operación normal con red
            breaker_fallas = 0
            breaker_abierto = False

    return {
        "estrategia": estrategia,
        "operaciones": num_operaciones,
        "valvulas_inundadas": valvulas_inundadas,
        "sobretiempo_maximo_s": sobretiempo_maximo_s,
        "comandos_perdidos": comandos_perdidos,
        "llamadas_a_controlador_caido": llamadas_a_controlador_caido,
    }


if __name__ == "__main__":
    print("=== Simulación de Safety y Resiliencia ChacraSmart Majes 2.0 ===")
    estrategias = ["centralizada", "reintentos", "failsafe_local"]
    for est in estrategias:
        res = simular_jornada_riego(est)
        print(f"\nEstrategia: {est.upper()}")
        print(f"  Válvulas abiertas tras corte (> 5s): {res['valvulas_inundadas']}")
        print(f"  Sobretiempo máximo medido: {res['sobretiempo_maximo_s']:.1f} s")
        print(f"  Comandos de riego perdidos: {res['comandos_perdidos']}")
        print(f"  Llamadas desperdiciadas a red caída: {res['llamadas_a_controlador_caido']}")
