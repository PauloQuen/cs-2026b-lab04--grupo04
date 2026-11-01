#!/usr/bin/env python3
"""
Genera la Matriz de Probabilidad e Impacto de Riesgos ATAM-lite (Lab 08, E7).
Salida: docs/architecture/diagramas/matriz_riesgos.png
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pathlib import Path

OUT_PATH = Path("docs/architecture/diagramas/matriz_riesgos.png")
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

fig, ax = plt.subplots(figsize=(10, 8), dpi=300)

# Cuadrícula 5x5
ax.set_xlim(0.5, 5.5)
ax.set_ylim(0.5, 5.5)
ax.set_xticks(range(1, 6))
ax.set_yticks(range(1, 6))
ax.set_xticklabels(["1: Muy Baja", "2: Baja", "3: Media", "4: Alta", "5: Muy Alta"], fontsize=9)
ax.set_yticklabels(["1: Insignificante", "2: Menor", "3: Moderado", "4: Mayor", "5: Catastrófico"], fontsize=9)

ax.set_xlabel("Probabilidad de Ocurrencia", fontsize=11, fontweight="bold", color="#1A365D")
ax.set_ylabel("Impacto Técnico / Negocio", fontsize=11, fontweight="bold", color="#1A365D")
ax.set_title("MATRIZ DE RIESGOS ARQUITECTÓNICOS (ATAM-LITE)\nChacraSmart Majes 2.0 — Grupo 04", 
             fontsize=12, fontweight="bold", color="#1A365D", pad=15)

# Zonas de riesgo coloreadas
# Verde (Bajo)
ax.fill_between([0.5, 3.5], 0.5, 2.5, color="#C6F6D5", alpha=0.6)
# Amarillo (Medio)
ax.fill_between([0.5, 5.5], 2.5, 3.5, color="#FEFCBF", alpha=0.5)
ax.fill_between([2.5, 3.5], 0.5, 5.5, color="#FEFCBF", alpha=0.3)
# Naranja / Rojo (Alto / Crítico)
ax.fill_between([3.5, 5.5], 3.5, 5.5, color="#FED7D7", alpha=0.7)
ax.fill_between([1.5, 3.5], 3.5, 5.5, color="#FEEBC8", alpha=0.6)
ax.fill_between([3.5, 5.5], 1.5, 3.5, color="#FEEBC8", alpha=0.6)

# Riesgos identificados en ATAM-lite
# (ID, Nombre, Prob, Imp, Color, Texto Offset)
riesgos = [
    ("R1", "Fallo total de VPS único\n(P=2, I=4)", 2.0, 4.0, "#C53030", (-20, 15)),
    ("R2", "Desincronización reloj RTC\nen controlador (P=3, I=4)", 3.0, 4.0, "#DD6B20", (15, 12)),
    ("R3", "Fuga mecánica silenciosa\nde electroválvula (P=2, I=5)", 2.0, 5.0, "#9B2C2C", (15, -15)),
    ("R4", "Lectura desactualizada por\ncaché 60s (P=2, I=2)", 2.0, 2.0, "#2F855A", (15, 10)),
]

for rid, label, prob, imp, col, offset in riesgos:
    ax.scatter(prob, imp, color=col, s=280, edgecolors="#1A202C", linewidth=1.5, zorder=5)
    ax.text(prob, imp, rid, color="white", ha="center", va="center", fontweight="bold", fontsize=9, zorder=6)
    ax.annotate(label, xy=(prob, imp), xytext=offset, textcoords="offset points",
                fontsize=8.5, fontweight="bold", color="#1A202C",
                bbox=dict(boxstyle="round,pad=0.3", fc="#FFFFFF", ec=col, lw=1.2, alpha=0.9),
                arrowprops=dict(arrowstyle="->", color=col, lw=1))

ax.grid(True, linestyle="--", alpha=0.5)

# Leyenda
ax.text(5.3, 0.7, "Zonas de Riesgo:\nVerde: Aceptable\nAmarillo: Monitoreo\nNaranja: Alto\nRojo: Crítico Inmediato",
        ha="right", va="bottom", fontsize=8, bbox=dict(boxstyle="square,pad=0.5", fc="white", ec="#CBD5E0"))

plt.tight_layout()
plt.savefig(OUT_PATH, dpi=300, bbox_inches="tight")
plt.close()
print(f"Matriz de riesgos generada en {OUT_PATH}")
