# ADR-007: Fail-Safe Autónomo en Hardware, Watchdog y Circuit Breaker para Válvulas

- **Estado:** Aceptado
- **Fecha:** 2026-10-28
- **Autores:** Quenta Ahumada Paulo Estefano y Callo Ccagiavilca Kevin Joel (Grupo 04)
- **Contexto de decisión:** Lab 08 — Falla segura ante cortes de red en 2000 parcelas (Iteración 2 de ADD)
- **Escenario asociado:** QA-02 (Safety Crítico: ninguna válvula abierta > 5 s tras corte de red) y QA-03 (Resiliencia de comandos)

---

## Contexto y Problema

En las parcelas del Valle de Majes, las comunicaciones celulares sufren caídas frecuentes debido a topografía y microclima. Si una válvula de riego se encuentra abierta cuando ocurre una desconexión y el sistema dependiera de que el servidor central envíe una orden de cierre `cerrar()`, dicha orden jamás llegaría, provocando el anegamiento de cultivos y desperdicio del recurso hídrico (**daño agronómico severo**).

La IA propuso inicialmente manejar la resiliencia mediante "reintentos exponenciales infinitos desde el servidor". Esta propuesta fue **rechazada** porque si el enlace físico está caído, los reintentos únicamente saturan la red y consumen las baterías del gateway sin cerrar la válvula física.

---

## Decisión

1. **Falla Segura (Fail-Safe) en Hardware Autónomo (ADR-003 reafirmado y extendido):**  
   Toda orden de riego enviada al controlador de campo embebido (ESP32) debe ser **atómica e incluir la duración máxima programada** (`duracion_segundos`). El microcontrolador utiliza un temporizador local por interrupción de hardware y un módulo RTC DS3231 con batería de litio independiente.
2. **Electroválvulas Normalmente Cerradas (NC):**  
   Las electroválvulas en campo requieren energía activa para mantenerse abiertas; si falla la alimentación eléctrica, el muelle mecánico fuerza el cierre inmediato.
3. **Patrón Decorator con Circuit Breaker en el Servidor:**  
   En la API, el puerto `ControladorValvula` se decora con un Circuit Breaker que detecta 3 fallas consecutivas y entra en estado ABIERTO por 120 s, evitando bombardear dispositivos de campo fuera de línea.
4. **Tabla Outbox Transaccional en PostgreSQL:**  
   Los comandos emitidos durante caídas de red no se descartan; se persisten en una tabla `outbox_comandos` para ser ejecutados de forma controlada cuando el enlace se restablezca.

---

## Evidencia Cuantitativa

En [`fitness/disponibilidad.py`](../../../fitness/disponibilidad.py) se simuló una jornada intensiva de 1000 operaciones de riego sometidas a 144 cortes de conectividad:
- **Estrategia Centralizada (Servidor):** 144 parcelas anegadas con sobretiempo de hasta 1752 segundos (~29 minutos de riego no deseado).
- **Estrategia con Reintentos:** 144 parcelas anegadas y 1440 llamadas inútiles a la red.
- **Fail-Safe Local + Circuit Breaker:** **0 válvulas abiertas más de 5 s** (sobretiempo máximo medido de **0.4 s**, originado únicamente por jitter de reloj RTC). Reducción del 89.5% de llamadas innecesarias sobre enlaces caídos.

---

## Consecuencias y Trade-offs

- **Positivas:**
  - Cumplimiento estricto del atributo crítico QA-02 (cero incidentes de anegamiento).
  - Tolerancia total a cortes de telecomunicaciones en zonas rurales de Majes.
- **Negativas (Trade-off aceptado):**
  - **Inconsistencia temporal de visualización:** Durante un corte prolongado, la PWA del agricultor mostrará la válvula como "abierta con temporizador local activo", hasta que la red se recupere y el controlador transmita el evento de cierre local sincronizado.
