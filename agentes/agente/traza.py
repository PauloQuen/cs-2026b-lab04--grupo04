"""Conversión automática de trazas JSONL a diagramas Mermaid (.mmd), PNG y métricas (Paso 9, E7)."""
from __future__ import annotations

import base64
import json
import pathlib
import sys
import urllib.request
from typing import Any, Dict, List


def cargar_traza(ruta_jsonl: str | pathlib.Path) -> List[Dict[str, Any]]:
    p = pathlib.Path(ruta_jsonl)
    return [json.loads(line) for line in p.read_text(encoding="utf-8").splitlines() if line.strip()]


def resumen_metricas(ruta_jsonl: str | pathlib.Path) -> Dict[str, Any]:
    eventos = cargar_traza(ruta_jsonl)
    acciones = [e for e in eventos if e.get("tipo") == "accion"]
    bloqueadas = [e for e in acciones if e.get("bloqueada")]
    contrato_invalido = [e for e in acciones if e.get("estado") == "CONTRATO_INVALIDO"]
    herramientas = {}
    for e in acciones:
        act = e.get("accion", "?")
        herramientas[act] = herramientas.get(act, 0) + 1
    return {
        "agente": eventos[0].get("agente", "agente") if eventos else "agente",
        "pasos": len(acciones),
        "herramientas": herramientas,
        "decisiones_rechazadas_contrato": len(contrato_invalido),
        "acciones_bloqueadas_politica": len(bloqueadas) - len(contrato_invalido),
        "contexto_final_chars": eventos[-1].get("contexto_chars", 0) if eventos else 0,
        "estado_final": eventos[-1].get("estado", "DESCONOCIDO") if eventos else "VACIO",
    }


def generar_mermaid(rutas_jsonl: List[str | pathlib.Path], salida_mmd: str | pathlib.Path, titulo: str = "Trayectoria") -> str:
    """Genera un diagrama sequenceDiagram Mermaid a partir de una o más trazas JSONL."""
    lineas = [
        "sequenceDiagram",
        f"    title {titulo}",
        "    participant M as Modelo (LLM)",
        "    participant C as Contrato + Política",
        "    participant H as Herramientas (Sandbox)",
    ]

    for ruta in rutas_jsonl:
        eventos = cargar_traza(ruta)
        agente_lbl = eventos[0].get("agente", "agente") if eventos else "agente"
        lineas.append(f"    Note over M,H: Turno de {agente_lbl}")
        for ev in eventos:
            tipo = ev.get("tipo")
            if tipo == "accion":
                paso = ev.get("paso")
                accion = ev.get("accion")
                estado = ev.get("estado")
                if estado == "CONTRATO_INVALIDO":
                    lineas.append(f"    M-x C: Paso {paso}: JSON inválido (rechazado por contrato)")
                    lineas.append("    C-->>M: ERROR DE CONTRATO")
                elif ev.get("bloqueada"):
                    lineas.append(f"    M-x C: Paso {paso}: {accion}() [BLOQUEADO]")
                    lineas.append("    C-->>M: Bloqueado por política")
                else:
                    args_short = ", ".join(f"{k}={repr(v)[:20]}" for k, v in ev.get("args", {}).items())
                    lineas.append(f"    M->>C: Paso {paso}: {accion}({args_short})")
                    lineas.append(f"    C->>H: Ejecutar {accion}")
                    lineas.append("    H-->>M: Observación")
            elif tipo == "final":
                paso = ev.get("paso")
                lineas.append(f"    M-->>C: Paso {paso}: Respuesta final (FINALIZADO)")

    mmd_txt = "\n".join(lineas) + "\n"
    out_p = pathlib.Path(salida_mmd)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    out_p.write_text(mmd_txt, encoding="utf-8")
    return mmd_txt


def renderizar_mermaid_png(ruta_mmd: str | pathlib.Path, ruta_png: str | pathlib.Path) -> None:
    """Renderiza el archivo .mmd a PNG mediante mermaid.ink."""
    mmd = pathlib.Path(ruta_mmd).read_text(encoding="utf-8")
    b64 = base64.urlsafe_b64encode(mmd.encode("utf-8")).decode("ascii")
    url = f"https://mermaid.ink/img/{b64}?bgColor=white"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = resp.read()
    out_p = pathlib.Path(ruta_png)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    out_p.write_bytes(data)


if __name__ == "__main__":
    if len(sys.argv) >= 3:
        mmd_out = sys.argv[1]
        png_out = sys.argv[2]
        trazas = sys.argv[3:]
        generar_mermaid(trazas, mmd_out)
        renderizar_mermaid_png(mmd_out, png_out)
        print(f"Generado {mmd_out} y {png_out}")
