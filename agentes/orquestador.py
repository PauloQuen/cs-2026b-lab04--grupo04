#!/usr/bin/env python3
"""
Orquestador multiagente para ChacraSmart Majes (Lab 10 · E5 y E6).
Coordina:
1. Modo 'unico': un único agente ReAct sobre ISSUE-02 en sandbox aislado.
2. Modo 'actor-critico': Planificador (solo lectura) + Ejecutor + Revisor (solo lectura, máx. 2 rondas).
3. Humano en el circuito (E6): opción --aprobar-edicion para validar cada cambio con 's'/'n'.
"""
from __future__ import annotations

import argparse
import pathlib
import shutil
import sys
import tempfile
from typing import Callable, Optional

RAIZ_REPO = pathlib.Path(__file__).resolve().parent.parent
if str(RAIZ_REPO) not in sys.path:
    sys.path.insert(0, str(RAIZ_REPO))

from agentes.agente.herramientas import Herramientas
from agentes.agente.modelos import ModeloGrabado
from agentes.agente.nucleo import Agente
from agentes.agente.politica import Politica, aprobar_edicion_consola
from agentes.agente.traza import generar_mermaid, renderizar_mermaid_png, resumen_metricas

AGENTES_DIR = RAIZ_REPO / "agentes"
TRAYECTORIAS_DIR = AGENTES_DIR / "trayectorias"
TRAZAS_DIR = AGENTES_DIR / "trazas"

HERRAMIENTAS_SOLO_LECTURA = {
    "listar_archivos",
    "leer_archivo",
    "buscar",
    "ejecutar_pruebas",
    "ver_cambios",
    "ejecutar_comando",
    "mapa_repo",
    "leer_notas",
}


def preparar_sandbox(sandbox_root: pathlib.Path) -> None:
    """Copia src/, tests/, issues/ y pytest.ini a un sandbox temporal limpio."""
    for folder in ("src", "tests", "issues"):
        src_dir = RAIZ_REPO / folder
        if src_dir.exists():
            shutil.copytree(src_dir, sandbox_root / folder, dirs_exist_ok=True)
    pytest_ini = RAIZ_REPO / "pytest.ini"
    if pytest_ini.exists():
        shutil.copy2(pytest_ini, sandbox_root / "pytest.ini")


def ejecutar_modo_unico(aprobar_fn: Optional[Callable] = None) -> dict:
    with tempfile.TemporaryDirectory(prefix="chacra_unico_") as tmp:
        sandbox = pathlib.Path(tmp)
        preparar_sandbox(sandbox)
        h = Herramientas(sandbox)
        traza = TRAZAS_DIR / "issue2_unico.jsonl"
        ag = Agente(
            nombre="agente_unico_issue2",
            modelo=ModeloGrabado(TRAYECTORIAS_DIR / "issue2_unico.json"),
            herramientas=h,
            politica=Politica(max_pasos=12, aprobar_edicion=aprobar_fn),
            objetivo="Resuelve issues/ISSUE-02.md sin modificar tests/.",
            traza_archivo=traza,
        )
        resumen = ag.ejecutar()
        print(f"--- MODO AGENTE ÚNICO ---\n{resumen}\n")
        mmd = TRAZAS_DIR / "issue2_unico.mmd"
        png = TRAZAS_DIR / "issue2_unico.png"
        generar_mermaid([traza], mmd, "ISSUE-02: Agente Único")
        renderizar_mermaid_png(mmd, png)
        return resumen_metricas(traza)


def ejecutar_actor_critico(aprobar_fn: Optional[Callable] = None, aplicar_a_repo: bool = False) -> dict:
    MAX_RONDAS = 2
    with tempfile.TemporaryDirectory(prefix="chacra_ac_") as tmp:
        sandbox = pathlib.Path(tmp)
        preparar_sandbox(sandbox)
        h = Herramientas(sandbox)

        # 1. Gestor / Planificador (solo lectura)
        traza_plan = TRAZAS_DIR / "issue2_planificador.jsonl"
        planificador = Agente(
            nombre="planificador",
            modelo=ModeloGrabado(TRAYECTORIAS_DIR / "issue2_planificador.json"),
            herramientas=h,
            politica=Politica(herramientas_permitidas=HERRAMIENTAS_SOLO_LECTURA, max_pasos=6),
            objetivo="Analiza issues/ISSUE-02.md y elabora un plan corto sin editar archivos.",
            traza_archivo=traza_plan,
        )
        plan = planificador.ejecutar()
        print(f"--- PLANIFICADOR ---\n{plan}\n")

        retro = ""
        trazas_todas = [traza_plan]
        rondas_usadas = 0

        for ronda in range(1, MAX_RONDAS + 1):
            rondas_usadas = ronda
            t_ej = TRAZAS_DIR / f"issue2_ejecutor_r{ronda}.jsonl"
            ejecutor = Agente(
                nombre=f"ejecutor_r{ronda}",
                modelo=ModeloGrabado(TRAYECTORIAS_DIR / f"issue2_ejecutor_r{ronda}.json"),
                herramientas=h,
                politica=Politica(max_pasos=12, aprobar_edicion=aprobar_fn),
                objetivo=f"Resuelve ISSUE-02.md siguiendo el plan:\n{plan}\n{retro}",
                traza_archivo=t_ej,
            )
            res_ej = ejecutor.ejecutar()

            t_rev = TRAZAS_DIR / f"issue2_revisor_r{ronda}.jsonl"
            revisor = Agente(
                nombre=f"revisor_r{ronda}",
                modelo=ModeloGrabado(TRAYECTORIAS_DIR / f"issue2_revisor_r{ronda}.json"),
                herramientas=h,
                politica=Politica(herramientas_permitidas=HERRAMIENTAS_SOLO_LECTURA, max_pasos=8),
                objetivo=f"Revisa el cambio de ISSUE-02 (solo lectura). Responde APROBADO o CAMBIOS SOLICITADOS.\nResumen:\n{res_ej}",
                traza_archivo=t_rev,
            )
            veredicto = revisor.ejecutar()
            trazas_todas.extend([t_ej, t_rev])
            print(f"--- RONDA {ronda} ---\nEJECUTOR: {res_ej}\nREVISOR : {veredicto}\n")

            if not veredicto.startswith("CAMBIOS SOLICITADOS"):
                break
            retro = f"El revisor solicitó cambios:\n{veredicto}\n"

        mmd = TRAZAS_DIR / "issue2_actor_critico.mmd"
        png = TRAZAS_DIR / "issue2_actor_critico.png"
        generar_mermaid(trazas_todas, mmd, "ISSUE-02: Planificador + Actor-Crítico (2 rondas)")
        renderizar_mermaid_png(mmd, png)

        if aplicar_a_repo:
            destino = RAIZ_REPO / "src" / "valvulas_riego" / "operaciones_campo.py"
            origen = sandbox / "src" / "valvulas_riego" / "operaciones_campo.py"
            shutil.copy2(origen, destino)
            print(f"[HUMANO APRUEBA] Cambios limpios aplicados a {destino}")

        metricas = [resumen_metricas(t) for t in trazas_todas]
        return {"rondas": rondas_usadas, "agentes": metricas}


def main() -> None:
    parser = argparse.ArgumentParser(description="Orquestador Multiagente ChacraSmart Majes")
    parser.add_argument("--modo", choices=["unico", "actor-critico", "ambos"], default="ambos")
    parser.add_argument("--aprobar-edicion", action="store_true", help="Activa aprobación humana (s/n) por consola")
    parser.add_argument("--aplicar", action="store_true", help="Aplica el cambio revisado al repositorio")
    args = parser.parse_args()

    aprobar_fn = aprobar_edicion_consola if args.aprobar_edicion else None

    if args.modo in ("unico", "ambos"):
        m_u = ejecutar_modo_unico(aprobar_fn)
        print("Métricas Único:", m_u)

    if args.modo in ("actor-critico", "ambos"):
        m_ac = ejecutar_actor_critico(aprobar_fn, aplicar_a_repo=args.aplicar)
        print("Métricas Actor-Crítico:", m_ac)


if __name__ == "__main__":
    main()
