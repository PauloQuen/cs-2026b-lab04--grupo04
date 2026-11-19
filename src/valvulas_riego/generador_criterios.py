"""
Integración del prompt versionado de Tarea A (criterios de aceptación) detrás
del puerto ProveedorLLM (Lab 07) con defensa en capas y validación JSON Schema (E6).
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict

from jsonschema import ValidationError, validate

from src.valvulas_riego.ia import ProveedorLLM

RAIZ_REPO = Path(__file__).resolve().parent.parent.parent
RAIZ_CRITERIOS = RAIZ_REPO / "prompts" / "criterios"
ESQUEMA_CRITERIOS = json.loads((RAIZ_CRITERIOS / "esquema.json").read_text(encoding="utf-8"))
MARCADORES_SISTEMA = ("# ROL", "# RESTRICCIONES", "# FORMATO DE SALIDA")


class SalidaInvalida(Exception):
    """La respuesta del LLM no cumple el contrato o viola las capas de seguridad."""


def sanitizar_entrada(texto: str) -> str:
    """Capa 1 de defensa: neutraliza cierres o aperturas falsas de delimitadores XML."""
    limpio = re.sub(r"<\s*(/?)\s*(historia|notas)\b([^>]*)>", r"[\1\2\3]", texto, flags=re.IGNORECASE)
    return limpio


def validar_sin_fuga_prompt(texto_crudo: str) -> None:
    """Capa 3: rechaza respuestas que filtren encabezados internos de la plantilla."""
    for marcador in MARCADORES_SISTEMA:
        if marcador in texto_crudo:
            raise SalidaInvalida(f"Posible fuga de instrucciones internas detectada: '{marcador}'")


class GeneradorCriterios:
    """Genera criterios de aceptación Gherkin validados mediante contrato JSON Schema."""

    def __init__(self, proveedor: ProveedorLLM, version: str = "v3.1") -> None:
        self._proveedor = proveedor
        self.version = version
        ruta_plantilla = RAIZ_CRITERIOS / f"{version}.txt"
        if not ruta_plantilla.exists():
            raise FileNotFoundError(f"Plantilla no encontrada: {ruta_plantilla}")
        self._plantilla = ruta_plantilla.read_text(encoding="utf-8")

    def generar(self, id_historia: str, historia: str) -> Dict[str, Any]:
        """Construye el prompt sanitizado, invoca al LLM y valida el contrato de salida."""
        historia_segura = sanitizar_entrada(historia)
        prompt = self._plantilla.replace("{{id}}", id_historia).replace("{{historia}}", historia_segura)
        texto = self._proveedor.completar(prompt)
        validar_sin_fuga_prompt(texto)

        try:
            criterios = json.loads(texto)
            validate(instance=criterios, schema=ESQUEMA_CRITERIOS)
        except (json.JSONDecodeError, ValidationError) as exc:
            raise SalidaInvalida(f"{self.version}/{id_historia}: {exc}") from exc

        if criterios["invest_ok"] and not criterios["escenarios"]:
            raise SalidaInvalida(f"{self.version}/{id_historia}: invest_ok=true requiere al menos un escenario")

        return criterios
