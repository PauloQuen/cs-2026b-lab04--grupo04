"""
Integración del prompt versionado de Tarea B (borrador de ADR desde notas de reunión)
detrás del puerto ProveedorLLM (Lab 07) con defensa en capas y validación JSON Schema (E6).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from jsonschema import ValidationError, validate

from src.valvulas_riego.generador_criterios import (
    SalidaInvalida,
    sanitizar_entrada,
    validar_sin_fuga_prompt,
)
from src.valvulas_riego.ia import ProveedorLLM

RAIZ_REPO = Path(__file__).resolve().parent.parent.parent
RAIZ_ADR = RAIZ_REPO / "prompts" / "adr-borrador"
ESQUEMA_ADR = json.loads((RAIZ_ADR / "esquema.json").read_text(encoding="utf-8"))


class GeneradorADR:
    """Genera borradores estructurados de ADR a partir de notas de reunión."""

    def __init__(self, proveedor: ProveedorLLM, version: str = "v3") -> None:
        self._proveedor = proveedor
        self.version = version
        ruta_plantilla = RAIZ_ADR / f"{version}.txt"
        if not ruta_plantilla.exists():
            raise FileNotFoundError(f"Plantilla no encontrada: {ruta_plantilla}")
        self._plantilla = ruta_plantilla.read_text(encoding="utf-8")

    def generar(self, id_reunion: str, notas: str) -> Dict[str, Any]:
        """Construye el prompt sanitizado, invoca al LLM y valida el contrato de ADR."""
        notas_seguras = sanitizar_entrada(notas)
        prompt = self._plantilla.replace("{{id}}", id_reunion).replace("{{notas}}", notas_seguras)
        texto = self._proveedor.completar(prompt)
        validar_sin_fuga_prompt(texto)

        try:
            borrador = json.loads(texto)
            validate(instance=borrador, schema=ESQUEMA_ADR)
        except (json.JSONDecodeError, ValidationError) as exc:
            raise SalidaInvalida(f"{self.version}/{id_reunion}: {exc}") from exc

        if borrador["notas_suficientes"] and borrador["adr"] is None:
            raise SalidaInvalida(f"{self.version}/{id_reunion}: notas_suficientes=true requiere objeto adr")

        return borrador
