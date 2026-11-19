#!/usr/bin/env python3
"""
Genera el gráfico de métricas de trazas agénticas (Lab 10 · E7)
a partir de los archivos reales .jsonl en agentes/trazas/.
"""
from pathlib import Path
import sys
import matplotlib.pyplot as plt
import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agentes.agente.traza import resumen_metricas

TRAZAS = REPO_ROOT / "agentes" / "trazas"


def main():
    m1 = resumen_metricas(TRAZAS / "issue1_ejecutor.jsonl")
    m3 = resumen_metricas(TRAZAS / "issue3_ejecutor.jsonl")
    m2u = resumen_metricas(TRAZAS / "issue2_unico.jsonl")
    m2_list = [
        resumen_metricas(TRAZAS / f)
        for f in (
            "issue2_planificador.jsonl",
            "issue2_ejecutor_r1.jsonl",
            "issue2_revisor_r1.jsonl",
            "issue2_ejecutor_r2.jsonl",
            "issue2_revisor_r2.jsonl",
        )
    ]

    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.6), dpi=200)

    # Panel 1: Acciones permitidas vs bloqueadas / rechazadas por ejecución
    etiquetas = [
        "ISSUE-01\n(ReAct E2)",
        "ISSUE-03\n(AST+Notas E4)",
        "ISSUE-02\n(Agente Único)",
        "ISSUE-02\n(Actor-Crítico 2R)",
    ]
    permitidas = [
        m1["pasos"] - m1["decisiones_rechazadas_contrato"] - m1["acciones_bloqueadas_politica"],
        m3["pasos"] - m3["decisiones_rechazadas_contrato"] - m3["acciones_bloqueadas_politica"],
        m2u["pasos"] - m2u["decisiones_rechazadas_contrato"] - m2u["acciones_bloqueadas_politica"],
        sum(x["pasos"] - x["decisiones_rechazadas_contrato"] - x["acciones_bloqueadas_politica"] for x in m2_list),
    ]
    bloqueadas = [
        m1["decisiones_rechazadas_contrato"] + m1["acciones_bloqueadas_politica"],
        m3["decisiones_rechazadas_contrato"] + m3["acciones_bloqueadas_politica"],
        m2u["decisiones_rechazadas_contrato"] + m2u["acciones_bloqueadas_politica"],
        sum(x["decisiones_rechazadas_contrato"] + x["acciones_bloqueadas_politica"] for x in m2_list),
    ]

    x = np.arange(len(etiquetas))
    w = 0.48
    b1 = ax1.bar(x, permitidas, w, label="Acciones permitidas", color="#2B6CB0", edgecolor="#1A365D")
    b2 = ax1.bar(x, bloqueadas, w, bottom=permitidas, label="Rechazadas (contrato/política)", color="#E53E3E", edgecolor="#9B2C2C")

    ax1.set_xticks(x)
    ax1.set_xticklabels(etiquetas, fontsize=8.5, fontweight="bold")
    ax1.set_ylabel("Número de pasos / acciones", fontsize=10, fontweight="bold", color="#1A365D")
    ax1.set_title("Pasos Permitidos vs. Bloqueados por Issue", fontsize=11.5, fontweight="bold", color="#1A365D", pad=10)
    ax1.set_ylim(0, 16)
    ax1.legend(loc="upper left", fontsize=8.5, frameon=True)

    for i, (p_val, bl_val) in enumerate(zip(permitidas, bloqueadas)):
        tot = p_val + bl_val
        ax1.text(i, tot + 0.35, f"{tot} ({bl_val} bloq.)", ha="center", va="bottom", fontsize=8.5, fontweight="bold", color="#1A202C")

    # Panel 2: Contexto máximo y acumulado (caracteres)
    ctx_max = [
        m1["contexto_final_chars"],
        m3["contexto_final_chars"],
        m2u["contexto_final_chars"],
        max(x["contexto_final_chars"] for x in m2_list),
    ]
    ctx_total = [
        m1["contexto_final_chars"],
        m3["contexto_final_chars"],
        m2u["contexto_final_chars"],
        sum(x["contexto_final_chars"] for x in m2_list),
    ]

    x2 = np.arange(len(etiquetas))
    w2 = 0.34
    bars_max = ax2.bar(x2 - w2 / 2, ctx_max, w2, label="Contexto máx. por agente", color="#319795", edgecolor="#234E52")
    bars_tot = ax2.bar(x2 + w2 / 2, ctx_total, w2, label="Contexto total acumulado", color="#805AD5", edgecolor="#44337A")

    ax2.set_xticks(x2)
    ax2.set_xticklabels(etiquetas, fontsize=8.5, fontweight="bold")
    ax2.set_ylabel("Caracteres de historial", fontsize=10, fontweight="bold", color="#1A365D")
    ax2.set_title("Consumo de Contexto (Máximo vs. Acumulado)", fontsize=11.5, fontweight="bold", color="#1A365D", pad=10)
    ax2.set_ylim(0, 23000)
    ax2.legend(loc="upper left", fontsize=8.5, frameon=True)

    for bar in bars_max:
        v = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width() / 2.0, v + 350, f"{v:,}", ha="center", va="bottom", fontsize=7.5, fontweight="bold", color="#234E52")
    for bar in bars_tot:
        v = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width() / 2.0, v + 350, f"{v:,}", ha="center", va="bottom", fontsize=7.5, fontweight="bold", color="#44337A")

    plt.tight_layout()
    out = TRAZAS / "metricas_agentes.png"
    plt.savefig(out, bbox_inches="tight")
    print(f"Gráfico guardado en {out}")


if __name__ == "__main__":
    main()
