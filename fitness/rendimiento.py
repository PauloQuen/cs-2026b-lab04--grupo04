#!/usr/bin/env python3
"""
Simulación de Rendimiento M/G/c — ChacraSmart Majes 2.0 (Lab 08, E2)
Evalúa el escenario QA-01: Ingesta y consulta de telemetría de 2000 parcelas
(67 req/s sostenidas, picos de hasta 120 req/s).
Modelo de colas M/G/c: llegadas de Poisson, c workers (gunicorn), tiempos de servicio lognormales.
"""

import math
import random
import statistics
import heapq
from typing import Callable, Dict, Any, List

# Parámetros del caso ChacraSmart Majes 2.0
PRESUPUESTO_P95_MS = 500.0  # QA-01: p95 <= 500 ms


def bd_sin_indice(rnd: random.Random) -> float:
    """Tiempo de servicio sin índices: scan secuencial en PostgreSQL. Media ~45 ms, cola larga."""
    # Lognormal con media aproximada 0.045 s y desviación estándar 0.020 s
    mu = math.log((0.045**2) / math.sqrt(0.020**2 + 0.045**2))
    sigma = math.sqrt(math.log(1 + (0.020**2) / (0.045**2)))
    return rnd.lognormvariate(mu, sigma)


def bd_con_indice(rnd: random.Random) -> float:
    """Tiempo de servicio con índice B-Tree (parcela_id, fecha DESC). Media ~6 ms."""
    mu = math.log((0.006**2) / math.sqrt(0.002**2 + 0.006**2))
    sigma = math.sqrt(math.log(1 + (0.002**2) / (0.006**2)))
    return rnd.lognormvariate(mu, sigma)


def con_cache_redis(servicio_bd: Callable[[random.Random], float], tasa_acierto: float = 0.75) -> Callable[[random.Random], float]:
    """Táctica de Caché en Redis para la última lectura de cada parcela."""
    def _servicio(rnd: random.Random) -> float:
        if rnd.random() < tasa_acierto:
            # Acierto en caché Redis: tiempo de lectura sub-milisegundo (~0.8 ms)
            return rnd.uniform(0.0005, 0.0012)
        # Fallo en caché: consulta a la base de datos + escritura en Redis
        return servicio_bd(rnd) + 0.0015
    return _servicio


def simular(lam: float, workers: int, servicio: Callable[[random.Random], float], segundos: int = 120, semilla: int = 42) -> Dict[str, Any]:
    """
    Simulación de cola M/G/c para medir tiempos de respuesta de la API.
    lam: tasa de llegadas (req/s)
    workers: número de workers de gunicorn
    servicio: generador de tiempos de servicio
    segundos: duración de la ventana simulada
    """
    rnd = random.Random(semilla)
    t = 0.0
    llegadas: List[float] = []
    while t < segundos:
        t += rnd.expovariate(lam)
        llegadas.append(t)

    libres = [0.0] * workers
    heapq.heapify(libres)
    respuestas: List[float] = []

    for a in llegadas:
        libre = heapq.heappop(libres)
        inicio = max(a, libre)
        duracion = servicio(rnd)
        fin = inicio + duracion
        heapq.heappush(libres, fin)
        respuestas.append((fin - a) * 1000.0)  # Convertir a milisegundos

    respuestas.sort()
    n = len(respuestas)
    if n == 0:
        return {"n": 0, "p50": 0.0, "p95": 0.0, "p99": 0.0, "media": 0.0, "max": 0.0}

    p = lambda q: respuestas[min(int(q * (n - 1)), n - 1)]
    return {
        "n": n,
        "p50": p(0.50),
        "p95": p(0.95),
        "p99": p(0.99),
        "media": statistics.mean(respuestas),
        "max": max(respuestas),
    }


if __name__ == "__main__":
    print("=== Simulación de Rendimiento ChacraSmart Majes 2.0 ===")
    cargas = [30, 67, 100, 120]  # req/s
    print(f"{'Carga (req/s)':<15} | {'Sin Tácticas (ms)':<18} | {'Índice (ms)':<15} | {'Índice + Caché (ms)':<20} | {'Cumple QA-01'}")
    print("-" * 85)
    for lam in cargas:
        r_base = simular(lam, workers=4, servicio=bd_sin_indice)
        r_ind = simular(lam, workers=4, servicio=bd_con_indice)
        r_cache = simular(lam, workers=4, servicio=con_cache_redis(bd_con_indice, tasa_acierto=0.75))
        cumple = "SÍ (<= 500 ms)" if r_cache["p95"] <= PRESUPUESTO_P95_MS else "NO"
        print(f"{lam:<15} | {r_base['p95']:<18.1f} | {r_ind['p95']:<15.1f} | {r_cache['p95']:<20.1f} | {cumple}")
