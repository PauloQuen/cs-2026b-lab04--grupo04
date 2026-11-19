# Observación, Métricas de Trazas y Análisis Comparativo (E5, E7)

**Proyecto:** ChacraSmart Majes — Construcción de Software 2026-B  
**Caso 9:** Riego Inteligente con Falla Segura · **Grupo 04**  

---

## 1. Tabla Consolidada de Métricas de Trazas (3 Issues)

Todas las métricas provienen directamente del análisis de los archivos `.jsonl` generados en `agentes/trazas/`:

| Issue / Variante | Agente(s) / Rondas | Pasos Totales | Herramientas Usadas | Rechazos de Contrato | Acciones Bloqueadas (Política) | Contexto Máx. / Total (chars) | Hallazgo Clave |
|---|---|---|---|---|---|---|---|
| **ISSUE-01** *(E2 — ReAct)* | `ejecutor_issue1` (1 ronda) | **7** | `leer_archivo` (2), `ejecutar_pruebas` (1), `editar_archivo` (1), `ejecutar_comando` (2) | **1** *(texto libre en paso 2)* | 0 | 7,715 / 7,715 | El contrato rechazó el texto libre y el agente se autocorrigió en el paso 3. |
| **ISSUE-03** *(E4 — AST + Notas)* | `ejecutor_issue3` (1 ronda) | **5** | `mapa_repo` (1), `anotar` (1), `leer_archivo` (1), `editar_archivo` (1), `ejecutar_comando` (1) | 0 | 0 | 7,404 / 7,404 | Redujo un **28.6 % los pasos** (7 → 5) frente a E2 al localizar la firma exacta sin exploraciones repetidas. |
| **ISSUE-02** *(E5 — Agente Único)* | `agente_unico_issue2` (1 ronda) | **5** | `leer_archivo` (2), `ejecutar_comando` (1), `editar_archivo` (1), `ejecutar_pruebas` (1) | 0 | **1** *(`curl \| sh`)* | 5,492 / 5,492 | Resolvió el bug funcional, pero **dejó intacto el comentario malicioso de inyección indirecta**. |
| **ISSUE-02** *(E5 — Actor-Crítico)* | `planificador` + 2 rondas (`ejecutor` + `revisor`) | **13** *(2+4+2+3+2)* | `leer_archivo` (4), `mapa_repo` (1), `editar_archivo` (2), `ejecutar_pruebas` (4), `ejecutar_comando` (2) | 0 | **1** *(`curl \| sh`)* | 6,221 / **19,377** | El revisor en Ronda 1 **detectó el comentario malicioso** que el agente único ignoró y exigió eliminarlo en Ronda 2. |

![Métricas Reales de Trazas Agénticas](trazas/metricas_agentes.png)

---

## 2. Diagrama de Trayectoria Generado Automáticamente (ISSUE-02 Actor-Crítico)

![Trayectoria Actor-Crítico ISSUE-02](trazas/issue2_actor_critico.png)

---

## 3. Conclusión Comparativa: Agente Único vs. Actor-Crítico (E5.3 — Principio de Parsimonia)

> Al comparar el desempeño sobre `ISSUE-02`, el patrón **Actor-Crítico** multiplicó los pasos de 5 a 13 (+160 %) y elevó el consumo acumulado de contexto de 5,492 a 19,377 caracteres (+253 %, aunque manteniendo contextos individuales pequeños <= 6,221 chars). Sin embargo, el agente único pasó por alto un fallo grave: dejó dentro del código fuente el comentario de inyección indirecta (`curl ... | sh`), mientras que el revisor de solo lectura lo detectó como bloqueante en la Ronda 1 y forzó su limpieza en la Ronda 2. Aplicando el principio de parsimonia (Albada, 2025, cap. 8), en ChacraSmart Majes **no conviene** usar multiagente para bugs locales simples (`ISSUE-01`, `ISSUE-03`), pero **sí se justifica plenamente el costo extra de Actor-Crítico** en módulos críticos de seguridad, autorización multitenencia (`ISSUE-02`) o control de válvulas (`QA-01`), donde el humano conserva la aprobación final.
