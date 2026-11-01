#!/usr/bin/env python3
"""
Renderizador visual del Árbol de Utilidad de ChacraSmart Majes 2.0 (Lab 08, E1).
Genera docs/architecture/utilidad/arbol.png con matplotlib.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pathlib import Path

OUT_PATH = Path("docs/architecture/utilidad/arbol.png")
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

fig, ax = plt.subplots(figsize=(15, 9), dpi=300)
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis("off")

# Título del Diagrama
ax.text(50, 97, "ÁRBOL DE UTILIDAD — CHACRASMART MAJES 2.0 (2000 PARCELAS)", 
        ha="center", va="center", fontsize=14, fontweight="bold", color="#1A365D")
ax.text(50, 94, "Priorización de Atributos de Calidad y Escenarios Medibles (Lab 08, E1)", 
        ha="center", va="center", fontsize=10, style="italic", color="#4A5568")

# Función para dibujar cajas redondeadas con sombra sutil
def draw_box(x, y, w, h, text, bg_color, text_color="white", fontsize=8.5, bold=True):
    rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.8,rounding_size=1.2",
                                  facecolor=bg_color, edgecolor="#2D3748", linewidth=1.2)
    ax.add_patch(rect)
    fw = "bold" if bold else "normal"
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", 
            fontsize=fontsize, color=text_color, fontweight=fw, linespacing=1.2)

def draw_arrow(x1, y1, x2, y2, color="#718096"):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="->", color=color, lw=1.5, shrinkA=3, shrinkB=3))

# 1. Nivel Raíz (Columna 1)
draw_box(2, 45, 15, 12, "UTILIDAD DEL\nSISTEMA\nChacraSmart 2.0\n(2000 parcelas)", "#1A365D", fontsize=9)

# 2. Nivel Atributos (Columna 2)
atributos = [
    (24, 78, 16, 8, "Protección (Safety)\ny Fiabilidad", "#2C5282"),
    (24, 60, 16, 8, "Rendimiento\n(Ingesta Masiva)", "#2C5282"),
    (24, 44, 16, 8, "Disponibilidad\n(Resiliencia de Red)", "#2C5282"),
    (24, 28, 16, 8, "Modificabilidad y\nMultitenencia", "#2C5282"),
    (24, 12, 16, 8, "Seguridad e\nIntegridad", "#2C5282"),
]
for x, y, w, h, txt, col in atributos:
    draw_box(x, y, w, h, txt, col)
    draw_arrow(17, 51, x, y + h / 2)

# 3. Nivel Refinamientos (Columna 3)
refinamientos = [
    (46, 83, 16, 6, "Falla segura ante\ncorte de red", "#EDF2F7", "#1A202C"),
    (46, 73, 16, 6, "Detección de fuga\npor falla de válvula", "#EDF2F7", "#1A202C"),
    (46, 61, 16, 6, "Procesamiento de\n67 req/s sostenidas", "#EDF2F7", "#1A202C"),
    (46, 45, 16, 6, "Tolerancia a cortes\ntransitorios de red", "#EDF2F7", "#1A202C"),
    (46, 33, 16, 6, "Escalamiento a 6\nsectores de riego", "#EDF2F7", "#1A202C"),
    (46, 23, 16, 6, "Nuevos protocolos\nde sensores (LoRa)", "#EDF2F7", "#1A202C"),
    (46, 13, 16, 6, "Aislamiento lógico\nentre agricultores", "#EDF2F7", "#1A202C"),
]
for x, y, w, h, txt, bg, tc in refinamientos:
    draw_box(x, y, w, h, txt, bg, tc, fontsize=8)

# Conexiones Atributos -> Refinamientos
draw_arrow(40, 82, 46, 86)
draw_arrow(40, 82, 46, 76)
draw_arrow(40, 64, 46, 64)
draw_arrow(40, 48, 46, 48)
draw_arrow(40, 32, 46, 36)
draw_arrow(40, 32, 46, 26)
draw_arrow(40, 16, 46, 16)

# 4. Nivel Escenarios Priorizados (Hojas - Columna 4)
escenarios = [
    (68, 81, 30, 9, "QA-02 (H, H) [CRÍTICO]\nCorte abrupto de red con válvula abierta:\nTemporizador local en controlador cierra válvula\ncon sobretiempo <= 5 s en 100% incidentes", "#C53030", "white"),
    (68, 71, 30, 8, "QA-06 (M, H)\nFuga de agua por falla mecánica de válvula:\nAlerta P0 a válvula matriz y PWA en <= 15 s", "#DD6B20", "white"),
    (68, 59, 30, 9, "QA-01 (H, M)\nCarga masiva (2000 parcelas, 67 req/s):\nLatencia de respuesta p95 <= 500 ms en\nconsultas y registro en el VPS único", "#DD6B20", "white"),
    (68, 44, 30, 8, "QA-03 (H, M)\nGateway de campo inestable:\nCircuit breaker + outbox diferido;\n0 comandos de riego perdidos en 24 h", "#DD6B20", "white"),
    (68, 31, 30, 9, "QA-04 (M, M)\nAlta de nuevo sector de regantes:\nConfiguración de cuotas y RLS en BD\nen <= 1 h-persona sin modificar código", "#38A169", "white"),
    (68, 20, 30, 8, "QA-07 (M, L)\nNuevo sensor LoRaWAN:\nIntegración mediante puerto/adaptador\nen <= 2 días-persona sin tocar dominio", "#319795", "white"),
    (68, 9, 30, 9, "QA-05 (H, M) [Corregido por Equipo]\nAislamiento multi-sector:\nPolíticas RLS en PostgreSQL + JWT evitan\naccesos no autorizados (0 fugas en 10k tests)", "#DD6B20", "white"),
]
for x, y, w, h, txt, bg, tc in escenarios:
    draw_box(x, y, w, h, txt, bg, tc, fontsize=8)

# Conexiones Refinamientos -> Escenarios
draw_arrow(62, 86, 68, 85.5)
draw_arrow(62, 76, 68, 75)
draw_arrow(62, 64, 68, 63.5)
draw_arrow(62, 48, 68, 48)
draw_arrow(62, 36, 68, 35.5)
draw_arrow(62, 26, 68, 24)
draw_arrow(62, 16, 68, 13.5)

# Leyenda en la parte inferior
draw_box(15, 2, 70, 4.5, "LEYENDA:   [Rojo] Prioridad (H, H) - Crítico Inmediato    |    [Naranja] Prioridad (H, M) / (M, H) - Alta Prioridad    |    [Verde] Prioridad (M, M) / (M, L)", "#EDF2F7", "#2D3748", fontsize=8.5, bold=True)

plt.tight_layout()
plt.savefig(OUT_PATH, dpi=300, bbox_inches="tight")
plt.close()
print(f"Árbol de utilidad renderizado en {OUT_PATH}")
