#!/usr/bin/env python3
"""
Genera el gráfico comparativo de simulación de disponibilidad y safety (fitness/simulacion_disponibilidad.png).
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from fitness.disponibilidad import simular_jornada_riego

OUT_PATH = Path("fitness/simulacion_disponibilidad.png")
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), dpi=300)

estrategias = ["Centralizada", "Reintentos", "Fail-Safe Local + Breaker"]
claves = ["centralizada", "reintentos", "failsafe_local"]
resultados = [simular_jornada_riego(k) for k in claves]

valvulas = [r["valvulas_inundadas"] for r in resultados]
sobretiempos = [r["sobretiempo_maximo_s"] for r in resultados]
llamadas = [r["llamadas_a_controlador_caido"] for r in resultados]

colores = ["#E53E3E", "#DD6B20", "#38A169"]

# Gráfico 1: Válvulas abiertas tras corte de red (Safety QA-02)
bars1 = ax1.bar(estrategias, valvulas, color=colores, width=0.55, edgecolor="#2D3748", linewidth=1.2)
ax1.set_title("Válvulas Abiertas más de 5s tras Corte de Red\n(1000 operaciones de riego simuladas - QA-02)", 
              fontsize=11, fontweight="bold", color="#1A365D")
ax1.set_ylabel("Cantidad de válvulas que inundaron la parcela", fontsize=10)
ax1.grid(axis="y", linestyle="--", alpha=0.5)

for bar in bars1:
    yval = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2.0, yval + 2, f"{int(yval)}", ha="center", va="bottom", fontweight="bold", fontsize=10)

# Gráfico 2: Sobrecarga de red caída vs Protección de Hardware
ax2.plot(estrategias, sobretiempos, "o-", color="#C53030", linewidth=2.2, label="Sobretiempo Máximo (s) [Escala log]")
ax2.set_yscale("log")
ax2.set_title("Sobretiempo de Riego no Deseado (s) y Resiliencia\n(Log scale - Temporizador Local vs Servidor)", 
              fontsize=11, fontweight="bold", color="#1A365D")
ax2.set_ylabel("Sobretiempo máximo (segundos)", fontsize=10)
ax2.grid(True, linestyle="--", alpha=0.5)

for i, txt in enumerate(sobretiempos):
    ax2.annotate(f"{txt:.1f} s", (estrategias[i], sobretiempos[i]), textcoords="offset points", 
                 xytext=(0, 10), ha="center", fontweight="bold")

plt.tight_layout()
plt.savefig(OUT_PATH, dpi=300, bbox_inches="tight")
plt.close()
print(f"Gráfico de disponibilidad y safety generado en {OUT_PATH}")
