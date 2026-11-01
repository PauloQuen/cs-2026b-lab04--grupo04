# ADR-006: Índices B-Tree Compuestos y Caché Redis para Telemetría de 2000 Parcelas

- **Estado:** Aceptado
- **Fecha:** 2026-10-27
- **Autores:** Quenta Ahumada Paulo Estefano y Callo Ccagiavilca Kevin Joel (Grupo 04)
- **Contexto de decisión:** Lab 08 — Crecimiento a 2000 parcelas en ChacraSmart Majes (Iteración 1 de ADD)
- **Escenario asociado:** QA-01 (Rendimiento: latencia $p95 \le 500\text{ ms}$ ante 67 req/s sostenidas y ráfagas de 120 req/s)

---

## Contexto y Problema

Al incorporar 2000 parcelas en el Valle de Majes con sensores reportando telemetría cada 30 segundos, el volumen de lecturas alcanza 66.67 req/s continuas y picos de 120 req/s en horarios de riego matutino.
Bajo el diseño inicial (scans secuenciales en tablas relacionales sin índices dedicados), la simulación de colas $M/G/c$ en [`fitness/rendimiento.py`](../../../fitness/rendimiento.py) demostró que a 120 req/s el sistema colapsa con un $p95$ de $39\text{ }846\text{ ms}$ (~40 segundos), saturando los 4 workers de gunicorn y el CPU del único VPS (restricción **R-03**).

La IA propuso inicialmente migrar a microservicios con un clúster de Apache Kafka y Kubernetes. Esta propuesta fue **rechazada tajantemente** porque viola el plazo de 1 mes (**R-01**), supera la capacidad de un equipo de 2 desarrolladores (**R-02**) y la JVM de Kafka provocaría caídas por falta de memoria RAM en el servidor de 4 GB (**R-03**).

---

## Decisión

1. **Crear índices B-Tree compuestos en PostgreSQL:**  
   Se indexan las consultas críticas de lectura de humedad mediante:
   ```sql
   CREATE INDEX idx_lecturas_parcela_fecha ON lecturas_humedad (parcela_id, fecha_registro DESC);
   ```
2. **Implementar Caché en Memoria con Redis:**  
   Se almacena en Redis la última lectura consolidada de cada parcela con una clave `parcela:{id}:humedad_reciente` y un tiempo de vida (TTL) de **60 segundos**.
3. **Mantener el estilo Monolito Modular:**  
   No se altera la arquitectura modular ni se agregan nuevos servidores.

---

## Evidencia Cuantitativa

Los resultados empíricos de la simulación $M/G/c$ arrojaron:
- **Sin tácticas:** $p95 = 39\text{ }846\text{ ms}$ (sistema colapsado).
- **Con solo índice B-Tree:** $p95 = 9.8\text{ ms}$ (reducción del 99.97%).
- **Con índice + caché Redis (75% aciertos):** $p95 = 8.9\text{ ms}$ y reducción del 75% en lecturas a disco.

Aún en el caso de caché fría (0% aciertos tras reinicio de Redis), el índice garantiza que el $p95$ permanezca en $9.8\text{ ms}$, cumpliendo con creces el presupuesto de $500\text{ ms}$ de QA-01.

---

## Consecuencias y Trade-offs

- **Positivas:**
  - Se cumple QA-01 holgadamente sin costo adicional de servidores.
  - Se mantiene la simplicidad operativa del monolito modular (**R-02**, **R-03**).
- **Negativas (Trade-off aceptado):**
  - **Frescura de datos:** Los agricultores pueden visualizar una lectura con hasta 60 segundos de desfase (consistencia eventual en la PWA). Este trade-off es agronómicamente aceptable dado que la humedad del suelo cambia en orden de horas.
  - Consumo de ~15 MB de memoria RAM en Redis para el catálogo de 2000 parcelas, perfectamente asumible dentro de los 4 GB del VPS.
