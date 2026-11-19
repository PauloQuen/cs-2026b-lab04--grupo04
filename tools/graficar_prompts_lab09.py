#!/usr/bin/env python3
"""
Genera el gráfico de resultados de promptfoo para el Laboratorio 09 (E8)
a partir de los archivos reales resultados.json de Tarea A y Tarea B.
"""
import json
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent


def calcular_tasas(json_path: Path):
    data = json.loads(json_path.read_text(encoding="utf-8"))
    prompts_meta = data["results"]["prompts"]
    res_list = data["results"]["results"]

    orden = []
    stats = {}
    for p in prompts_meta:
        lbl = p["label"].splitlines()[0].split(":")[0].strip()
        if lbl not in stats:
            orden.append(lbl)
            stats[lbl] = {"pass": 0, "total": 0, "cases": {}}

    for r in res_list:
        lbl = prompts_meta[r["promptIdx"]]["label"].splitlines()[0].split(":")[0].strip()
        cid = r["vars"]["id"]
        stats[lbl]["total"] += 1
        if r["success"]:
            stats[lbl]["pass"] += 1
        stats[lbl]["cases"][cid] = 1 if r["success"] else 0

    tasas = [(lbl, 100.0 * stats[lbl]["pass"] / stats[lbl]["total"], stats[lbl]["pass"], stats[lbl]["total"]) for lbl in orden]
    return tasas, stats, orden


def main():
    tasas_a, stats_a, orden_a = calcular_tasas(REPO_ROOT / "prompts" / "criterios" / "resultados.json")
    tasas_b, stats_b, orden_b = calcular_tasas(REPO_ROOT / "prompts" / "adr-borrador" / "resultados.json")

    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.8), dpi=200)

    # Panel 1: Barras de Tasa de Aprobación Tarea A y Tarea B
    labels_a = [f"Tarea A\n{x[0]}" for x in tasas_a]
    vals_a = [x[1] for x in tasas_a]
    labels_b = [f"Tarea B\n{x[0]}" for x in tasas_b]
    vals_b = [x[1] for x in tasas_b]

    all_labels = labels_a + labels_b
    all_vals = vals_a + vals_b
    colors = ["#E53E3E", "#DD6B20", "#3182CE", "#276749"] + ["#E53E3E", "#D69E2E", "#276749"]

    bars = ax1.bar(range(len(all_labels)), all_vals, color=colors, edgecolor="#1A202C", width=0.6, alpha=0.9)
    ax1.set_xticks(range(len(all_labels)))
    ax1.set_xticklabels(all_labels, fontsize=8.5, fontweight="bold")
    ax1.set_ylabel("Tasa de Aprobación (%)", fontsize=10, fontweight="bold", color="#1A365D")
    ax1.set_title("Evolución de Tasa de Aprobación (promptfoo)", fontsize=11.5, fontweight="bold", color="#1A365D", pad=10)
    ax1.set_ylim(0, 118)
    ax1.axhline(85, color="#2B6CB0", linestyle="--", linewidth=1.2, label="Meta mínima guía (85%)")
    ax1.axvline(3.5, color="#CBD5E1", linestyle="-", linewidth=1.5)
    ax1.legend(loc="upper left", fontsize=8.5, frameon=True)

    raw_counts = [f"{x[2]}/{x[3]}" for x in tasas_a] + [f"{x[2]}/{x[3]}" for x in tasas_b]
    for bar, val, cnt in zip(bars, all_vals, raw_counts):
        ax1.text(
            bar.get_x() + bar.get_width() / 2.0,
            val + 2.5,
            f"{val:.1f}%\n({cnt})",
            ha="center",
            va="bottom",
            fontsize=8,
            fontweight="bold",
            color="#1A202C",
        )

    # Panel 2: Mapa de calor de casos H1..H9 (Tarea A)
    casos_a = ["H1", "H2", "H3", "H4", "H5", "H6", "H7", "H8", "H9"]
    matrix = np.zeros((len(casos_a), len(orden_a)))
    for r_i, cid in enumerate(casos_a):
        for c_i, ver in enumerate(orden_a):
            matrix[r_i, c_i] = stats_a[ver]["cases"].get(cid, 0)

    cmap = plt.matplotlib.colors.ListedColormap(["#FED7D7", "#C6F6D5"])
    ax2.imshow(matrix, cmap=cmap, aspect="auto", vmin=0, vmax=1)
    ax2.set_xticks(range(len(orden_a)))
    ax2.set_xticklabels(orden_a, fontsize=9.5, fontweight="bold", color="#1A365D")
    ax2.set_yticks(range(len(casos_a)))
    etiquetas_casos = [
        "H1 (Normal)", "H2 (Normal)", "H3 (Normal)", "H4 (QA-01)",
        "H5 (Normal)", "H6 (Normal)", "H7 (No INVEST)", "H8 (Técnica)", "H9 (Inyección)"
    ]
    ax2.set_yticklabels(etiquetas_casos, fontsize=8.5, color="#2D3748")
    ax2.set_title("Matriz Caso × Versión — Tarea A (Criterios)", fontsize=11.5, fontweight="bold", color="#1A365D", pad=10)

    for r_i in range(len(casos_a)):
        for c_i in range(len(orden_a)):
            ok = matrix[r_i, c_i] == 1
            txt = "PASS" if ok else "FAIL"
            col = "#22543D" if ok else "#9B2C2C"
            ax2.text(c_i, r_i, txt, ha="center", va="center", fontsize=8.5, fontweight="bold", color=col)

    # Cuadrícula en matriz
    ax2.set_xticks(np.arange(-0.5, len(orden_a), 1), minor=True)
    ax2.set_yticks(np.arange(-0.5, len(casos_a), 1), minor=True)
    ax2.grid(which="minor", color="#A0AEC0", linestyle="-", linewidth=0.8)
    ax2.tick_params(which="minor", bottom=False, left=False)

    plt.tight_layout()
    out = REPO_ROOT / "prompts" / "resultados_evals.png"
    plt.savefig(out, bbox_inches="tight")
    print(f"Gráfico guardado en {out}")


if __name__ == "__main__":
    main()
