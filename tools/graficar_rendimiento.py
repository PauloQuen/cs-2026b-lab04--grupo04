#!/usr/bin/env python3
"""
Genera el gráfico comparativo de simulación de rendimiento (fitness/simulacion_rendimiento.png).
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from fitness.rendimiento import simular, bd_sin_indice, bd_con_indice, con_cache_redis

OUT_PATH = Path("fitness/simulacion_rendimiento.png")
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), dpi=300)

# Gráfico 1: p95 vs Carga (req/s)
cargas = [20, 40, 60, 67, 80, 100, 120]
p95_sin = []
p95_ind = []
p95_cache = []

for c in cargas:
    p95_sin.append(simular(c, 4, bd_sin_indice)["p95"])
    p95_ind.append(simular(c, 4, bd_con_indice)["p95"])
    p95_cache.append(simular(c, 4, con_cache_redis(bd_con_indice, 0.75))["p95"])

ax1.plot(cargas, p95_sin, "r-o", label="Sin tácticas (scan secuencial)", linewidth=2.2)
ax1.plot(cargas, p95_ind, "b--s", label="Con índice B-Tree (6 ms)", linewidth=2.0)
ax1.plot(cargas, p95_cache, "g-^", label="Con índice + caché Redis 75% hit", linewidth=2.2)
ax1.axhline(500, color="orange", linestyle=":", label="Presupuesto QA-01 (500 ms)", linewidth=2.0)
ax1.axvline(67, color="purple", linestyle="--", alpha=0.6, label="Carga base 2000 parcelas (67 req/s)")
ax1.axvline(120, color="darkred", linestyle="--", alpha=0.6, label="Carga pico campaña (120 req/s)")

ax1.set_yscale("log")
ax1.set_title("Rendimiento API ante Escalamiento a 2000 Parcelas\n(p95 en escala logarítmica)", fontsize=11, fontweight="bold", color="#1A365D")
ax1.set_xlabel("Tasa de solicitudes (req/s)", fontsize=10)
ax1.set_ylabel("Latencia p95 (ms) [Log scale]", fontsize=10)
ax1.grid(True, which="both", ls="--", alpha=0.4)
ax1.legend(loc="upper left", fontsize=8.5)

# Gráfico 2: Punto de sensibilidad de la Caché ante Carga Pico (120 req/s)
tasas_acierto = [0.0, 0.10, 0.25, 0.50, 0.75, 0.90, 0.98]
p95_sensibilidad = []

for tasa in tasas_acierto:
    p95_sensibilidad.append(simular(120, 4, con_cache_redis(bd_con_indice, tasa))["p95"])

ax2.plot([t * 100 for t in tasas_acierto], p95_sensibilidad, "m-D", linewidth=2.2, label="Índice + Caché (120 req/s)")
ax2.axhline(500, color="orange", linestyle=":", label="Presupuesto QA-01 (500 ms)", linewidth=2.0)
ax2.set_title("Punto de Sensibilidad: Tasa de Aciertos Caché\n(Carga pico = 120 req/s)", fontsize=11, fontweight="bold", color="#1A365D")
ax2.set_xlabel("Tasa de aciertos de caché (%)", fontsize=10)
ax2.set_ylabel("Latencia p95 (ms)", fontsize=10)
ax2.grid(True, ls="--", alpha=0.4)
ax2.legend(loc="upper right", fontsize=8.5)

plt.tight_layout()
plt.savefig(OUT_PATH, dpi=300, bbox_inches="tight")
plt.close()
print(f"Gráfico de rendimiento generado en {OUT_PATH}")
