"""
Implementación del patrón Command para órdenes de riego y control de actuadores (E4).
Encapsula una solicitud como un objeto, permitiendo parametrizar órdenes,
mantener historial auditable y soportar paradas de emergencia.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime, timezone

from src.valvulas_riego.estados import Valvula
from src.valvulas_riego.actuadores import ControladorValvula, ResultadoOperacion


class ComandoRiego(ABC):
    """COMMAND: interfaz común para órdenes sobre actuadores de riego."""

    @abstractmethod
    def ejecutar(self) -> ResultadoOperacion:
        """Ejecuta la orden sobre el dispositivo."""
        ...


class ComandoAbrirValvula(ComandoRiego):
    """Comando concreto que encapsula la solicitud de apertura con duración."""

    def __init__(self, valvula: Valvula, controlador: ControladorValvula, duracion_min: int):
        self.valvula = valvula
        self.controlador = controlador
        self.duracion_min = duracion_min
        self.fecha_solicitud = datetime.now(timezone.utc)
        self.ejecutado = False

    def ejecutar(self) -> ResultadoOperacion:
        self.valvula.abrir(self.duracion_min)
        resultado = self.controlador.abrir(self.valvula.id, self.duracion_min)
        if resultado.aprobado:
            self.valvula.confirmar_apertura()
            self.valvula.ack_operacion = resultado.ack
        else:
            self.valvula.fallar_cierre_seguro()
        self.ejecutado = True
        return resultado


class ComandoCerrarValvula(ComandoRiego):
    """Comando concreto para corte de riego manual o por temporizador cumplido."""

    def __init__(self, valvula: Valvula, controlador: ControladorValvula):
        self.valvula = valvula
        self.controlador = controlador
        self.fecha_solicitud = datetime.now(timezone.utc)

    def ejecutar(self) -> ResultadoOperacion:
        self.valvula.cerrar()
        resultado = self.controlador.cerrar(self.valvula.id)
        if resultado.aprobado:
            self.valvula.confirmar_cierre()
        else:
            self.valvula.fallar_cierre_seguro()
        return resultado


class InvocadorRiego:
    """INVOKER: Despacha comandos de riego y mantiene el historial de órdenes ejecutadas."""

    def __init__(self):
        self.historial: List[ComandoRiego] = []

    def ejecutar_comando(self, comando: ComandoRiego) -> ResultadoOperacion:
        resultado = comando.ejecutar()
        self.historial.append(comando)
        return resultado
