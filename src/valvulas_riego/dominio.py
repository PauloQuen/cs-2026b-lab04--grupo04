"""
Módulo valvulas_riego de ChacraSmart Majes.
Esqueleto generado con IA a partir de docs/design/clases.puml (E1) y revisado
por el equipo (reglas C1-C5). Nombre del módulo decidido por el equipo:
"valvulas-riego" no es un identificador válido en Python, se usa valvulas_riego.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from uuid import UUID, uuid4


class EstadoValvula(Enum):
    CERRADA = "CERRADA"
    ABRIENDO = "ABRIENDO"
    ABIERTA = "ABIERTA"
    CERRANDO = "CERRANDO"
    FALLA = "FALLA"


class EstadoProgramacion(Enum):
    PENDIENTE = "PENDIENTE"
    EN_CURSO = "EN_CURSO"
    FINALIZADA = "FINALIZADA"
    CANCELADA = "CANCELADA"


@dataclass
class Agricultor:
    nombre: str
    celular: str
    id: UUID = field(default_factory=uuid4)


@dataclass
class LecturaHumedad:
    valor_porcentaje: Decimal
    fecha_hora: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    id: UUID = field(default_factory=uuid4)

    def esta_bajo_umbral(self, umbral: Decimal) -> bool:
        return self.valor_porcentaje < umbral


@dataclass
class Valvula:
    """Válvula de riego. La falla segura (QA-01) se materializa en los
    métodos que la dejan siempre cerrada o en FALLA (ADR-003)."""

    nombre: str
    parcela_id: UUID
    apertura_maxima_min: int
    estado: EstadoValvula = EstadoValvula.CERRADA
    id: UUID = field(default_factory=uuid4)

    def abrir(self, duracion_min: int) -> None:
        if self.estado is not EstadoValvula.CERRADA:
            raise ValueError("La válvula no está cerrada")
        if duracion_min > self.apertura_maxima_min:
            raise ValueError("Duración mayor que el máximo seguro de apertura")
        self.estado = EstadoValvula.ABRIENDO

    def cerrar(self) -> None:
        if self.estado in (EstadoValvula.CERRADA, EstadoValvula.CERRANDO):
            return
        self.estado = EstadoValvula.CERRANDO

    def confirmar_apertura(self) -> None:
        if self.estado is not EstadoValvula.ABRIENDO:
            raise ValueError("No hay apertura en curso")
        self.estado = EstadoValvula.ABIERTA

    def confirmar_cierre(self) -> None:
        self.estado = EstadoValvula.CERRADA

    def fallar_cierre_seguro(self) -> None:
        # QA-01 / ADR-003: ante cualquier falla la válvula termina cerrada.
        self.estado = EstadoValvula.FALLA


@dataclass
class Parcela:
    nombre: str
    distrito: str
    valvulas: list[Valvula] = field(default_factory=list)
    lecturas: list[LecturaHumedad] = field(default_factory=list)
    id: UUID = field(default_factory=uuid4)

    def humedad_actual(self) -> LecturaHumedad | None:
        return self.lecturas[-1] if self.lecturas else None


@dataclass
class ProgramacionRiego:
    hora_inicio: datetime
    duracion_min: int
    valvula_id: UUID
    estado: EstadoProgramacion = EstadoProgramacion.PENDIENTE
    id: UUID = field(default_factory=uuid4)

    def iniciar(self) -> None:
        self.estado = EstadoProgramacion.EN_CURSO

    def finalizar(self) -> None:
        self.estado = EstadoProgramacion.FINALIZADA

    def cancelar(self, motivo: str) -> None:
        self.estado = EstadoProgramacion.CANCELADA


# ---------------------------------------------------------------------------
# Puertos (interfaces) hacia servicios externos y persistencia (ADR-001)
# ---------------------------------------------------------------------------
class ControladorValvula(ABC):
    """Puerto hacia el controlador de campo (sensor + válvula, ADR-002/003)."""

    @abstractmethod
    def abrir(self, valvula_id: UUID, duracion_min: int) -> None: ...

    @abstractmethod
    def cerrar(self, valvula_id: UUID) -> None: ...

    @abstractmethod
    def consultar_estado(self, valvula_id: UUID) -> EstadoValvula: ...


class ControladorCampoAdapter(ControladorValvula):
    def abrir(self, valvula_id: UUID, duracion_min: int) -> None:
        raise NotImplementedError("Integrar con el controlador de campo")

    def cerrar(self, valvula_id: UUID) -> None:
        raise NotImplementedError("Integrar con el controlador de campo")

    def consultar_estado(self, valvula_id: UUID) -> EstadoValvula:
        raise NotImplementedError("Integrar con el controlador de campo")


class Notificador(ABC):
    """Puerto hacia el servicio de mensajería (RF-05)."""

    @abstractmethod
    def notificar_alerta(self, agricultor_id: UUID, mensaje: str) -> None: ...


class MensajeriaAdapter(Notificador):
    def notificar_alerta(self, agricultor_id: UUID, mensaje: str) -> None:
        raise NotImplementedError("Integrar con el servicio de mensajería")


class RepositorioRiego(ABC):
    """Puerto de persistencia del módulo."""

    @abstractmethod
    def buscar_valvula(self, id: UUID) -> Valvula: ...

    @abstractmethod
    def buscar_valvulas_por_parcela(self, parcela_id: UUID) -> list[Valvula]: ...

    @abstractmethod
    def guardar_programacion(self, p: ProgramacionRiego) -> None: ...


# ---------------------------------------------------------------------------
# Servicio de aplicación: única pieza que usa los puertos (E1, reglas C1/C5)
# ---------------------------------------------------------------------------
class ServicioRiego:
    def __init__(
        self,
        repo: RepositorioRiego,
        controlador: ControladorValvula,
        notificador: Notificador,
    ) -> None:
        self._repo = repo
        self._controlador = controlador
        self._notificador = notificador

    def programar_riego(self, parcela_id: UUID, hora_inicio: datetime,
                        duracion_min: int) -> ProgramacionRiego:
        valvulas = self._repo.buscar_valvulas_por_parcela(parcela_id)
        valvula = next((v for v in valvulas if v.estado is EstadoValvula.CERRADA), None)
        if valvula is None:
            raise ValueError("Ninguna válvula disponible (fuera de línea)")
        programacion = ProgramacionRiego(
            hora_inicio=hora_inicio, duracion_min=duracion_min, valvula_id=valvula.id
        )
        self._repo.guardar_programacion(programacion)
        return programacion

    def apertura_remota(self, valvula_id: UUID, duracion_min: int) -> None:
        valvula = self._repo.buscar_valvula(valvula_id)
        valvula.abrir(duracion_min)
        self._controlador.abrir(valvula_id, duracion_min)

    def evaluar_riego_automatico(self, parcela_id: UUID) -> None:
        raise NotImplementedError("Orquestar con el módulo de lecturas (E4)")