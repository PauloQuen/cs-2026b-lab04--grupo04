"""Contrato estructurado para cada decisión del bucle ReAct (Paso 4, E3)."""
from __future__ import annotations

from typing import Any, Iterable, Tuple


def validar_decision(d: Any, herramientas_conocidas: Iterable[str]) -> Tuple[bool, str]:
    """Valida que la decisión del modelo cumpla estrictamente el protocolo JSON."""
    if not isinstance(d, dict):
        return False, "la decisión debe ser un objeto JSON"
    if not isinstance(d.get("pensamiento"), str) or not d["pensamiento"].strip():
        return False, "falta 'pensamiento' (texto no vacío)"
    if ("final" in d) == ("accion" in d):
        return False, "debe incluir 'accion' o 'final', pero no ambos"
    if "final" in d:
        return (True, "") if isinstance(d["final"], str) and d["final"].strip() else (False, "'final' debe ser texto no vacío")
    if not isinstance(d["accion"], str) or not d["accion"].strip():
        return False, "'accion' debe ser una cadena no vacía"
    if d["accion"] not in set(herramientas_conocidas):
        return False, f"herramienta desconocida: {d['accion']!r}"
    if "args" in d and not isinstance(d["args"], dict):
        return False, "'args' debe ser un objeto JSON"
    extra = set(d) - {"pensamiento", "accion", "args"}
    if extra:
        return False, f"campos no permitidos: {sorted(extra)}"
    return True, ""
