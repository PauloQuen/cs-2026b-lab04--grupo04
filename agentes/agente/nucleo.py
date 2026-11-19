"""Núcleo del agente ReAct implementado como máquina de estados finitos (Paso 3, E2/E3)."""
from __future__ import annotations

import json
import pathlib
import time
from typing import Any, Dict, List

from agentes.agente.contrato import validar_decision
from agentes.agente.herramientas import Herramientas
from agentes.agente.modelos import Modelo
from agentes.agente.politica import Politica


class Agente:
    """Ejecuta el bucle ReAct con validación de contrato, política y trazabilidad JSONL."""

    def __init__(
        self,
        nombre: str,
        modelo: Modelo,
        herramientas: Herramientas,
        politica: Politica,
        objetivo: str,
        traza_archivo: str | pathlib.Path,
    ) -> None:
        self.nombre = nombre
        self.modelo = modelo
        self.h = herramientas
        self.politica = politica
        self.historial: List[Dict[str, str]] = [{"role": "user", "content": objetivo}]
        self.traza_archivo = pathlib.Path(traza_archivo)
        self.eventos: List[Dict[str, Any]] = []
        self._t0 = 0.0

    def _registrar(self, **campos: Any) -> None:
        evento = {
            "agente": self.nombre,
            "t_ms": round((time.perf_counter() - self._t0) * 1000, 2),
            "contexto_chars": sum(len(m["content"]) for m in self.historial),
            **campos,
        }
        self.eventos.append(evento)

    def ejecutar(self) -> str:
        self._t0 = time.perf_counter()
        self._registrar(tipo="objetivo", estado="INICIO", texto=self.historial[0]["content"])
        conocidas = set(self.h.catalogo())

        for paso in range(1, self.politica.max_pasos + 2):
            d = self.modelo.decidir(self.historial)  # DECIDIENDO
            d_txt = json.dumps(d, ensure_ascii=False) if isinstance(d, (dict, list)) else str(d)
            self.historial.append({"role": "assistant", "content": d_txt})

            ok, motivo = validar_decision(d, conocidas)  # VALIDANDO_CONTRATO
            if not ok:
                obs = f"ERROR DE CONTRATO: {motivo}. Responda solo con el JSON del protocolo."
                self._registrar(
                    tipo="accion",
                    estado="CONTRATO_INVALIDO",
                    paso=paso,
                    pensamiento=str(d)[:200],
                    accion="(ninguna)",
                    args={},
                    observacion=obs,
                    bloqueada=True,
                )
            elif "final" in d:
                self._registrar(
                    tipo="final",
                    estado="FINALIZADO",
                    paso=paso,
                    pensamiento=d["pensamiento"],
                    texto=d["final"],
                )
                break
            else:
                accion, args = d["accion"], d.get("args", {})
                veredicto = self.politica.evaluar(accion, args, paso)  # EVALUANDO_POLITICA
                if veredicto.permitido:
                    try:
                        obs = str(getattr(self.h, accion)(**args))  # EJECUTANDO
                    except Exception as exc:  # el error también vuelve como observación
                        obs = f"ERROR: {type(exc).__name__}: {exc}"
                    self._registrar(
                        tipo="accion",
                        estado="OBSERVANDO",
                        paso=paso,
                        pensamiento=d["pensamiento"],
                        accion=accion,
                        args=args,
                        observacion=obs[:600],
                        bloqueada=False,
                    )
                else:
                    obs = f"BLOQUEADO POR LA POLÍTICA: {veredicto.motivo}"
                    limite = "máximo" in veredicto.motivo
                    self._registrar(
                        tipo="accion",
                        estado="LIMITE_ALCANZADO" if limite else "BLOQUEADO",
                        paso=paso,
                        pensamiento=d["pensamiento"],
                        accion=accion,
                        args=args,
                        observacion=obs,
                        bloqueada=True,
                    )
                    if limite:
                        break
            self.historial.append({"role": "user", "content": f"Observación: {obs}"})

        self.traza_archivo.parent.mkdir(parents=True, exist_ok=True)
        with self.traza_archivo.open("w", encoding="utf-8") as f:
            for ev in self.eventos:
                f.write(json.dumps(ev, ensure_ascii=False) + "\n")

        return str(self.eventos[-1].get("texto", "(sin respuesta final)"))
