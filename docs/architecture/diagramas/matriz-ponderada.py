#!/usr/bin/env python3
"""
Matriz de decisión ponderada — EcoRecicla AQP (Lab 04, E2 / Figura 4)

Recalcula los totales ponderados de docs/architecture/matriz-decision.md y genera
el grafico de barras comparativo.

Este script existe para que la matriz NO sea una afirmacion: si alguien cambia un
peso o un puntaje sin justificativa, las aserciones de abajo fallan y el equipo se
entera antes de que el docente lo note.

Uso (desde esta carpeta):
    pip install matplotlib
    python matriz-ponderada.py

Salida: img/matriz-ponderada.png
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")          # sin ventana: util en servidor / CI
import matplotlib.pyplot as plt

# --------------------------------------------------------------------------- #
# Datos: deben coincidir EXACTAMENTE con las tablas de matriz-decision.md
# --------------------------------------------------------------------------- #
CRITERIOS = [
    # (nombre, peso, {alternativa: puntaje}, driver que lo justifica)
    ("Modificabilidad",       0.30, {"A": 2, "B": 4, "C": 5}, "QA-01 (atributo critico)"),
    ("Tiempo de entrega",     0.25, {"A": 5, "B": 4, "C": 2}, "R-01 + R-02"),
    ("Simplicidad operativa", 0.20, {"A": 5, "B": 4, "C": 1}, "R-02"),
    ("Costo operativo",       0.15, {"A": 5, "B": 5, "C": 2}, "R-03"),
    ("Escalabilidad",         0.10, {"A": 2, "B": 3, "C": 5}, "carga moderada (sin driver)"),
]

ALTERNATIVAS = {
    "A": "A. Monolito en capas",
    "B": "B. Monolito modular",
    "C": "C. Microservicios",
}

# Totales publicados en matriz-decision.md. Si el calculo no coincide, el documento miente.
TOTALES_PUBLICADOS = {"A": 3.80, "B": 4.05, "C": 3.00}

COLOR = {"A": "#90A4AE", "B": "#2E7D32", "C": "#C0392B"}


def calcular() -> dict[str, float]:
    """Total ponderado = Σ (peso × puntaje)."""
    return {
        alt: round(sum(peso * puntajes[alt] for _, peso, puntajes, _ in CRITERIOS), 2)
        for alt in ALTERNATIVAS
    }


def verificar() -> None:
    """Aserciones: fallan si la matriz deja de ser coherente."""
    suma_pesos = round(sum(peso for _, peso, _, _ in CRITERIOS), 10)
    assert suma_pesos == 1.0, f"✗ Los pesos suman {suma_pesos}, deben sumar exactamente 1.00 (100 %)"
    assert len(CRITERIOS) >= 5, f"✗ La guia exige minimo 5 criterios; hay {len(CRITERIOS)}"
    for nombre, _, puntajes, _ in CRITERIOS:
        assert set(puntajes) == set(ALTERNATIVAS), f"✗ Falta puntuar alguna alternativa en '{nombre}'"
        assert all(1 <= v <= 5 for v in puntajes.values()), f"✗ Puntaje fuera de 1..5 en '{nombre}'"
    total = calcular()
    for alt, publicado in TOTALES_PUBLICADOS.items():
        assert abs(total[alt] - publicado) < 1e-9, (
            f"✗ Total de {alt} recalculado = {total[alt]:.2f}, "
            f"pero matriz-decision.md publica {publicado:.2f}"
        )
    ganador = max(total, key=lambda alt: total[alt])
    assert ganador == "B", f"✗ Ganadora recalculada = {ganador}, el ADR-001 declara B"
    print("✓ Verificaciones OK: pesos = 100 %, 5 criterios, puntajes 1..5, "
          f"totales {total}, ganadora {ganador} (consistente con ADR-001)")


def grafica(total: dict[str, float]) -> Path:
    nombres = [ALTERNATIVAS[a] for a in ALTERNATIVAS]
    valores = [total[a] for a in ALTERNATIVAS]

    fig, ax = plt.subplots(figsize=(10, 5.6))
    barras = ax.barh(nombres, valores, color=[COLOR[a] for a in ALTERNATIVAS],
                     edgecolor="#263238", linewidth=1.2, height=0.55)
    ax.invert_yaxis()

    for barra, alt in zip(barras, ALTERNATIVAS):
        v = total[alt]
        ax.text(v + 0.06, barra.get_y() + barra.get_height() / 2,
                f"{v:.2f}".replace(".", ","),
                va="center", fontweight="bold", fontsize=13, color="#212121")

    ax.set_xlim(0, 5)
    ax.set_xticks(range(6))
    ax.set_xlabel("Total ponderado  (1 = muy malo  ·  5 = excelente)", fontsize=11)
    ax.set_title("EcoRecicla AQP — Matriz de decisión ponderada\n"
                 "Gana el monolito modular (B, 4,05)", fontsize=13.5, fontweight="bold")

    ax.text(0.995, -0.16,
            "Pesos: Modificabilidad 30 % · Tiempo de entrega 25 % · Simplicidad operativa 20 % · "
            "Costo operativo 15 % · Escalabilidad 10 %",
            transform=ax.transAxes, ha="right", va="top", fontsize=8.6, color="#546E7A")

    ax.grid(axis="x", linestyle="--", alpha=0.35)
    ax.set_axisbelow(True)
    for lado in ("top", "right", "left"):
        ax.spines[lado].set_visible(False)

    plt.tight_layout()
    salida = Path(__file__).parent / "img" / "matriz-ponderada.png"
    salida.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(salida, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return salida


def detalle() -> None:
    print("\nDetalle del calculo (Total = Σ peso × puntaje):")
    for nombre, peso, puntajes, driver in CRITERIOS:
        calc = "  ".join(f"{a}: {peso:.2f}×{puntajes[a]} = {peso*puntajes[a]:.2f}"
                         .replace(".", ",") for a in ALTERNATIVAS)
        print(f"  {nombre:<22} {peso:.0%}  [{driver}]".ljust(64) + calc)
    total = calcular()
    for a in ALTERNATIVAS:
        print(f"  TOTAL {ALTERNATIVAS[a]:<26} = {total[a]:.2f}".replace(".", ","))


if __name__ == "__main__":
    verificar()
    detalle()
    print(f"\n✓ Imagen generada en {grafica(calcular())}")