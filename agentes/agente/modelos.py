"""Interfaz Strategy para el modelo de decisión del agente (Paso 7)."""
from __future__ import annotations

import json
import os
import pathlib
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class Modelo(ABC):
    """STRATEGY: abstrae el proveedor de decisiones (grabado, interactivo o API real)."""

    @abstractmethod
    def decidir(self, historial: List[Dict[str, str]]) -> Any:
        """Devuelve el objeto JSON (o texto crudo si falló) con la siguiente decisión."""
        ...


class ModeloGrabado(Modelo):
    """Reproduce una trayectoria JSON pregrabada para pruebas y CI sin clave API."""

    def __init__(self, ruta_trayectoria: str | pathlib.Path) -> None:
        self.ruta = pathlib.Path(ruta_trayectoria)
        self._decisiones: List[Any] = json.loads(self.ruta.read_text(encoding="utf-8"))
        self._indice = 0

    def decidir(self, historial: List[Dict[str, str]]) -> Any:
        if self._indice >= len(self._decisiones):
            return {"pensamiento": "Fin de trayectoria grabada", "final": "Trayectoria completada"}
        item = self._decisiones[self._indice]
        self._indice += 1
        return item


class ModeloInteractivo(Modelo):
    """Modo sin API key: muestra el contexto al estudiante, lee JSON pegado y guarda trayectoria."""

    def __init__(self, ruta_guardar: Optional[str | pathlib.Path] = None) -> None:
        self.ruta_guardar = pathlib.Path(ruta_guardar) if ruta_guardar else None
        self.grabadas: List[Any] = []

    def decidir(self, historial: List[Dict[str, str]]) -> Any:
        print("\n=== CONTEXTO PARA EL ASISTENTE DE IA ===")
        print(historial[-1]["content"][:1500])
        raw = input("\nPegue la decisión JSON del asistente: ").strip()
        try:
            decision: Any = json.loads(raw)
        except json.JSONDecodeError:
            decision = raw
        self.grabadas.append(decision)
        if self.ruta_guardar:
            self.ruta_guardar.parent.mkdir(parents=True, exist_ok=True)
            self.ruta_guardar.write_text(json.dumps(self.grabadas, ensure_ascii=False, indent=2), encoding="utf-8")
        return decision


class ModeloAnthropicStub(Modelo):
    """Referencia segura para proveedor real mediante variable de entorno ANTHROPIC_API_KEY."""

    def __init__(self, modelo: str = "claude-sonnet-4-20250514") -> None:
        self.modelo = modelo
        self.api_key = os.getenv("ANTHROPIC_API_KEY")

    def decidir(self, historial: List[Dict[str, str]]) -> Any:
        if not self.api_key:
            raise RuntimeError("Configure ANTHROPIC_API_KEY en el entorno; nunca la escriba en el código.")
        raise NotImplementedError("Conecte el SDK oficial usando self.api_key en producción.")
