"""Política de mínimo privilegio, lista blanca de comandos y humano en el circuito (Paso 6, E6)."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional, Set, Tuple


@dataclass
class Decision:
    permitido: bool
    motivo: str = ""


def aprobar_edicion_consola(args: Dict[str, Any], input_fn: Callable[[str], str] = input) -> bool:
    """Patrón humano en el circuito: valida estrictamente 's' o 'n' antes de editar."""
    ruta = args.get("ruta", "")
    antes = str(args.get("antes", ""))[:120].replace("\n", "\\n")
    despues = str(args.get("despues", ""))[:120].replace("\n", "\\n")
    print(f"\n[APROBACIÓN HUMANA] Archivo: {ruta}")
    print(f"  - Antes : {antes}")
    print(f"  + Desp. : {despues}")
    while True:
        resp = input_fn("¿Aprobar esta edición? (s/n): ").strip().lower()
        if resp in ("s", "n"):
            return resp == "s"
        print("Respuesta inválida: ingrese únicamente 's' o 'n'.")


@dataclass
class Politica:
    herramientas_permitidas: Set[str] = field(
        default_factory=lambda: {
            "listar_archivos",
            "leer_archivo",
            "buscar",
            "ejecutar_pruebas",
            "editar_archivo",
            "ver_cambios",
            "ejecutar_comando",
            "mapa_repo",
            "anotar",
            "leer_notas",
        }
    )
    comandos_permitidos: Tuple[str, ...] = (
        r"^python -m pytest\b",
        r"^pytest\b",
        r"^radon cc\b",
        r"^lint-imports\b",
        r"^git (status|diff)\b",
    )
    rutas_protegidas: Tuple[str, ...] = ("tests/", "agentes/pruebas_agente/")
    max_pasos: int = 15
    aprobar_edicion: Optional[Callable[[Dict[str, Any]], bool]] = None

    def evaluar(self, accion: str, args: Dict[str, Any], paso: int) -> Decision:
        if paso > self.max_pasos:
            return Decision(False, f"Se alcanzó el máximo de {self.max_pasos} pasos")
        if accion not in self.herramientas_permitidas:
            return Decision(False, f"Herramienta no permitida para este rol: {accion}")
        if accion == "ejecutar_comando":
            cmd = str(args.get("comando", ""))
            if not any(re.search(p, cmd) for p in self.comandos_permitidos):
                return Decision(False, f"Comando fuera de la lista permitida: {cmd!r}")
        if accion == "editar_archivo":
            ruta = str(args.get("ruta", "")).replace("\\", "/").lstrip("./")
            if ruta.startswith(self.rutas_protegidas):
                return Decision(False, f"Ruta protegida (no modificable por el agente): {ruta}")
            if self.aprobar_edicion and not self.aprobar_edicion(args):
                return Decision(False, "El revisor humano rechazó la edición")
        if accion == "anotar":
            pass
        return Decision(True)
