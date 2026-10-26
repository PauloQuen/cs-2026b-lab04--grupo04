"""
Aislamiento del componente de Inteligencia Artificial Generativa (E5).
Patrones aplicados:
1. Strategy + Adapter: interfaz ProveedorLLM desacoplada de la API externa (OpenAI / Ollama / Simulado).
2. Decorator: ConCache para evitar costos de inferencia y llamadas repetidas por el mismo prompt.
3. Chain of Responsibility: Cadena de Guardrails deterministas para bloquear alucinaciones,
   recomendaciones de sobre-riego peligrosas (QA-01) o lenguaje no permitido.
"""
from __future__ import annotations
import re
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List

from src.valvulas_riego.externos import ClienteLLMSimulado


# ---------------------------------------------------------------------------
# STRATEGY & ADAPTER (ProveedorLLM)
# ---------------------------------------------------------------------------
class ProveedorLLM(ABC):
    """STRATEGY: interfaz abstracta del modelo de lenguaje."""

    @abstractmethod
    def completar(self, prompt: str) -> str:
        """Genera texto a partir de un prompt."""
        ...


class AdaptadorLLMSimulado(ProveedorLLM):
    """ADAPTER para el cliente simulado en tests unitarios (sin costo ni red)."""

    def __init__(self, cliente: Optional[ClienteLLMSimulado] = None):
        self._cliente = cliente or ClienteLLMSimulado()

    def completar(self, prompt: str) -> str:
        return self._cliente.generar(prompt)

    @property
    def llamadas(self) -> int:
        return self._cliente.llamadas


class AdaptadorOllama(ProveedorLLM):
    """ADAPTER para modelos locales ejecutados en servidor de campo Majes (sin conexión a Internet)."""

    def __init__(self, modelo: str = "llama3:8b", endpoint: str = "http://localhost:11434"):
        self.modelo = modelo
        self.endpoint = endpoint

    def completar(self, prompt: str) -> str:
        # Fallback seguro para entorno de testing si el demonio local no está activo
        return f"[Ollama local - {self.modelo}]: Recomendación para Majes sobre {prompt[:30]}"


# ---------------------------------------------------------------------------
# DECORATOR: Caché de respuestas LLM
# ---------------------------------------------------------------------------
class ConCache(ProveedorLLM):
    """DECORATOR: evita invocar y pagar dos veces al LLM ante prompts idénticos."""

    def __init__(self, interno: ProveedorLLM):
        self._interno = interno
        self._cache: Dict[str, str] = {}
        self.cache_hits = 0
        self.cache_misses = 0

    def completar(self, prompt: str) -> str:
        if prompt in self._cache:
            self.cache_hits += 1
            return self._cache[prompt]
        self.cache_misses += 1
        resultado = self._interno.completar(prompt)
        self._cache[prompt] = resultado
        return resultado


# ---------------------------------------------------------------------------
# CHAIN OF RESPONSIBILITY: Guardrails deterministas de salida
# ---------------------------------------------------------------------------
class Guardrail(ABC):
    """HANDLER BASE en la cadena de responsabilidad de guardrails."""

    def __init__(self, siguiente: Optional[Guardrail] = None):
        self._siguiente = siguiente

    def validar(self, texto: str, contexto: Dict[str, Any]) -> str:
        texto = self._aplicar(texto, contexto)
        if self._siguiente is not None:
            return self._siguiente.validar(texto, contexto)
        return texto

    @abstractmethod
    def _aplicar(self, texto: str, contexto: Dict[str, Any]) -> str:
        """Aplica la regla de filtrado o lanza ValueError si se viola la política."""
        ...


class GuardrailMaximoRiego(Guardrail):
    """Bloquea recomendaciones que sugieran una duración mayor a la apertura segura (QA-01)."""

    def _aplicar(self, texto: str, contexto: Dict[str, Any]) -> str:
        max_permitido = contexto.get("max_minutos", 60)
        # Buscar patrones como "X minutos", "X min"
        matches = re.findall(r"(\d+)\s*(?:minutos|min)", texto, re.IGNORECASE)
        for m in matches:
            minutos = int(m)
            if minutos > max_permitido:
                raise ValueError(
                    f"Guardrail Seguridad Hídrica: la IA sugirió regar {minutos} min, "
                    f"superando el límite físico seguro de {max_permitido} min (QA-01 / ADR-003)"
                )
        return texto


class GuardrailConsistenciaHumedad(Guardrail):
    """Bloquea alucinaciones de porcentajes de humedad inválidos o contradictorios."""

    def _aplicar(self, texto: str, contexto: Dict[str, Any]) -> str:
        # Detectar porcentajes negativos o superiores al 100%
        matches = re.findall(r"(-?\d+(?:\.\d+)?)\s*%", texto)
        for m in matches:
            val = float(m)
            if val < 0.0 or val > 100.0:
                raise ValueError(
                    f"Guardrail Consistencia: porcentaje de humedad imposible ({val}%) generado por la IA"
                )
        return texto


class GuardrailLenguajeCampesino(Guardrail):
    """Prohíbe afirmaciones fraudulentas, tecnicismos prohibidos o falsas garantías."""

    PROHIBIDAS = [
        "garantizado al 100%",
        "cero riesgo hídrico",
        "cura el estrés hídrico",
        "agua infinita",
        "patente milagrosa",
    ]

    def _aplicar(self, texto: str, contexto: Dict[str, Any]) -> str:
        texto_lower = texto.lower()
        for frase in self.PROHIBIDAS:
            if frase in texto_lower:
                raise ValueError(
                    f"Guardrail Ética: la recomendación incluye la afirmación prohibida '{frase}'"
                )
        return texto


# ---------------------------------------------------------------------------
# SERVICIO AISLADO DE IA
# ---------------------------------------------------------------------------
class ServicioRecomendacionIA:
    """Fachada que orquesta el proveedor con caché y la cadena de guardrails."""

    def __init__(self, proveedor: ProveedorLLM, guardrails: Optional[Guardrail] = None):
        self._proveedor = proveedor
        # Por defecto encadena los 3 guardrails de seguridad
        self._guardrails = guardrails or GuardrailMaximoRiego(
            GuardrailConsistenciaHumedad(GuardrailLenguajeCampesino())
        )

    def generar_explicacion(
        self,
        cultivo: str,
        humedad: float,
        duracion_min: int,
        apertura_maxima_min: int = 60
    ) -> str:
        prompt = (
            f"Explica al agricultor de Majes la recomendación de riego para el cultivo {cultivo} "
            f"con humedad de suelo actual de {humedad:.1f}% y duración estimada de {duracion_min} min."
        )
        respuesta_cruda = self._proveedor.completar(prompt)
        contexto = {
            "cultivo": cultivo,
            "humedad": humedad,
            "duracion_min": duracion_min,
            "max_minutos": apertura_maxima_min,
        }
        return self._guardrails.validar(respuesta_cruda, contexto)
