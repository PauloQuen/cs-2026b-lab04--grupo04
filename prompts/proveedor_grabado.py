"""
Proveedor de respuestas grabadas para evaluación reproducible sin clave de API (E2, E6).
Compatible con:
1. promptfoo (`call_api(prompt, options, context)`)
2. Código Python detrás del puerto `ProveedorLLM` (`ProveedorGrabado`)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any, Dict

RAIZ_PROMPTS = Path(__file__).resolve().parent
RAIZ_REPO = RAIZ_PROMPTS.parent
if str(RAIZ_REPO) not in sys.path:
    sys.path.insert(0, str(RAIZ_REPO))

from src.valvulas_riego.ia import ProveedorLLM


def _extraer_version(context: Dict[str, Any], options: Dict[str, Any], prompt: str) -> str:
    """Determina la versión del prompt (v1, v2, v3, v3.1) desde el contexto de promptfoo."""
    cfg_ver = (options or {}).get("config", {}).get("version")
    if cfg_ver:
        return str(cfg_ver)

    prompt_meta = (context or {}).get("prompt", {})
    for key in ("label", "id"):
        val = str(prompt_meta.get(key, ""))
        # Buscar v3.1 antes que v3
        m = re.search(r"\b(v\d+(?:\.\d+)?)\b", val)
        if m:
            return m.group(1)

    # Respaldo por firma de versión en el texto renderizado
    if "nombra los servicios externos como los ve el usuario" in prompt:
        return "v3.1"
    if "<historia id=" in prompt or "<notas id=" in prompt:
        return "v3"
    if "Responde SOLO con un JSON" in prompt:
        return "v2"
    return "v1"


def call_api(prompt: str, options: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """Punto de entrada estándar de promptfoo para proveedores Python personalizados."""
    config = (options or {}).get("config", {})
    tarea = config.get("tarea", "criterios")
    version = _extraer_version(context, options, prompt)

    vars_ctx = (context or {}).get("vars", {})
    caso_id = str(vars_ctx.get("id", "")).strip()
    if not caso_id:
        return {"error": "No se encontró 'vars.id' en el caso de evaluación."}

    ruta = RAIZ_PROMPTS / tarea / "grabaciones" / version / f"{caso_id}.txt"
    if not ruta.exists():
        return {"error": f"No existe grabación para {tarea}/{version}/{caso_id}: {ruta}"}

    salida = ruta.read_text(encoding="utf-8")
    return {"output": salida}


class ProveedorGrabado(ProveedorLLM):
    """Adaptador Python que implementa ProveedorLLM leyendo respuestas grabadas en disco."""

    def __init__(self, tarea: str = "criterios", version: str = "v3.1"):
        self.tarea = tarea
        self.version = version
        self.llamadas = 0

    def completar(self, prompt: str) -> str:
        self.llamadas += 1
        # Buscar el ID de caso dentro del prompt renderizado (<historia id="H1"> o <notas id="N1"> o (H1))
        m = re.search(r'id="([A-Za-z0-9_-]+)"', prompt)
        if not m:
            m = re.search(r"\b([HN]\d+)\b", prompt)
        if not m:
            raise ValueError("No se pudo identificar el ID del caso dentro del prompt.")
        caso_id = m.group(1)
        ruta = RAIZ_PROMPTS / self.tarea / "grabaciones" / self.version / f"{caso_id}.txt"
        if not ruta.exists():
            raise FileNotFoundError(f"Grabación no encontrada: {ruta}")
        return ruta.read_text(encoding="utf-8")
