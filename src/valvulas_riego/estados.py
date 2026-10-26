"""
Implementación del patrón State para el ciclo de vida de la entidad Valvula (E3).
Basado estrictamente en la máquina de estados de docs/design/estados-valvula.mmd (Lab 05).
Garantiza el atributo de calidad crítico QA-01 y la decisión ADR-003:
ante pérdida de conexión o anomalía, la válvula conmuta inmediatamente a FALLA segura.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional


class TransicionEstadoInvalida(ValueError):
    """Excepción lanzada cuando una operación no está permitida en el estado actual."""
    pass


class EstadoValvulaBase(ABC):
    """Clase base de estado. Por defecto prohíbe todas las transiciones (fail-closed)."""

    nombre: str = "BASE"

    def abrir(self, valvula: "Valvula", duracion_min: int) -> None:
        raise TransicionEstadoInvalida(f"No se puede abrir una válvula en estado {self.nombre}")

    def confirmar_apertura(self, valvula: "Valvula") -> None:
        raise TransicionEstadoInvalida(f"No hay apertura en curso para confirmar en estado {self.nombre}")

    def cerrar(self, valvula: "Valvula") -> None:
        raise TransicionEstadoInvalida(f"No se puede cerrar una válvula en estado {self.nombre}")

    def confirmar_cierre(self, valvula: "Valvula") -> None:
        raise TransicionEstadoInvalida(f"No hay cierre en curso para confirmar en estado {self.nombre}")

    def fallar_cierre_seguro(self, valvula: "Valvula") -> None:
        # Cualquier estado que no sea terminal puede fallar a FALLA segura
        valvula.cambiar_a(EstadoFalla())

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.nombre}>"


class EstadoCerrada(EstadoValvulaBase):
    """Válvula en reposo, estanca y segura."""
    nombre = "CERRADA"

    def abrir(self, valvula: "Valvula", duracion_min: int) -> None:
        if duracion_min > valvula.apertura_maxima_min:
            raise ValueError(
                f"Duración {duracion_min} min excede el máximo seguro de {valvula.apertura_maxima_min} min (QA-01)"
            )
        valvula.cambiar_a(EstadoAbriendo())


class EstadoAbriendo(EstadoValvulaBase):
    """Orden de apertura enviada al actuador físico, esperando acuse de confirmación."""
    nombre = "ABRIENDO"

    def confirmar_apertura(self, valvula: "Valvula") -> None:
        valvula.cambiar_a(EstadoAbierta())

    def fallar_cierre_seguro(self, valvula: "Valvula") -> None:
        valvula.cambiar_a(EstadoFalla())


class EstadoAbierta(EstadoValvulaBase):
    """Válvula abierta regando activamente la parcela."""
    nombre = "ABIERTA"

    def cerrar(self, valvula: "Valvula") -> None:
        valvula.cambiar_a(EstadoCerrando())

    def fallar_cierre_seguro(self, valvula: "Valvula") -> None:
        valvula.cambiar_a(EstadoFalla())


class EstadoCerrando(EstadoValvulaBase):
    """Orden de corte enviada al solenoide/actuador, esperando acuse estanco."""
    nombre = "CERRANDO"

    def confirmar_cierre(self, valvula: "Valvula") -> None:
        valvula.cambiar_a(EstadoCerrada())

    def fallar_cierre_seguro(self, valvula: "Valvula") -> None:
        valvula.cambiar_a(EstadoFalla())


class EstadoFalla(EstadoValvulaBase):
    """Estado de Falla Segura (QA-01 / ADR-003): la válvula queda bloqueada cerrada.
    Requiere inspección manual del técnico; ninguna transición operativa es permitida."""
    nombre = "FALLA"

    def fallar_cierre_seguro(self, valvula: "Valvula") -> None:
        pass  # Ya se encuentra en falla segura


class Valvula:
    """Entidad de dominio Valvula con delegación completa al patrón State."""

    def __init__(
        self,
        id: str,
        nombre: str,
        parcela_id: str,
        apertura_maxima_min: int = 60,
        estado: Optional[str | EstadoValvulaBase] = None,
        estado_inicial: Optional[EstadoValvulaBase] = None,
        ack_operacion: Optional[str] = None,
    ):
        self.id = id
        self.nombre = nombre
        self.parcela_id = parcela_id
        self.apertura_maxima_min = apertura_maxima_min

        # Soporte polimórfico de inicialización por string o por objeto de estado
        if estado_inicial is not None:
            self._estado = estado_inicial
        elif isinstance(estado, EstadoValvulaBase):
            self._estado = estado
        elif isinstance(estado, str):
            mapa = {
                "CERRADA": EstadoCerrada,
                "ABRIENDO": EstadoAbriendo,
                "ABIERTA": EstadoAbierta,
                "CERRANDO": EstadoCerrando,
                "FALLA": EstadoFalla,
            }
            clase_estado = mapa.get(estado.upper(), EstadoCerrada)
            self._estado = clase_estado()
        else:
            self._estado = EstadoCerrada()

        self.ack_operacion = ack_operacion

    @property
    def estado(self) -> str:
        """Propiedad polimórfica que devuelve el string para compatibilidad hacia atrás."""
        return self._estado.nombre

    @property
    def estado_objeto(self) -> EstadoValvulaBase:
        """Acceso al objeto de estado concreto para verificación de patrones."""
        return self._estado

    def cambiar_a(self, nuevo_estado: EstadoValvulaBase) -> None:
        self._estado = nuevo_estado

    def abrir(self, duracion_min: int) -> None:
        self._estado.abrir(self, duracion_min)

    def confirmar_apertura(self) -> None:
        self._estado.confirmar_apertura(self)

    def cerrar(self) -> None:
        self._estado.cerrar(self)

    def confirmar_cierre(self) -> None:
        self._estado.confirmar_cierre(self)

    def fallar_cierre_seguro(self) -> None:
        self._estado.fallar_cierre_seguro(self)
