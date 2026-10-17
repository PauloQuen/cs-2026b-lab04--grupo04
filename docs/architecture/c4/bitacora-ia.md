# Bitácora de interacciones con la IA (E7)

Registro de las interacciones con IA durante el Lab 06, con el formato de la Tabla 7 de la guía
(fecha, herramienta, prompt, propuesta, verificación, decisión). Regla aplicada: **la IA propone, el equipo
decide y verifica**; las 6 interacciones ocurrieron el 17/10/2026 y todas se contrastaron con los artefactos
del repositorio o con comandos medidos.

## Interacción 1 — Enfoque del modelo (Prompt IA 1)

| Campo | Contenido |
|---|---|
| Fecha | 17/10/2026 |
| Herramienta | Asistente IA (opencode) — rol arquitecto, adaptación del **Prompt IA 1** de la guía |
| Prompt | "Avanzaremos con el Lab 06. Analiza `lab06/analisis_lab06.md`, `docs/design/paquetes.puml`, `drivers.md`, ADR-001 y `despliegue.py`, y propón el enfoque del workspace de Structurizr DSL: personas, sistema, externos, contenedores, componentes, dinámica y despliegue." |
| Propuesta de la IA | 2 personas (Agricultor RF-02 a RF-05, Técnico RF-06/07); controlador de campo y servicio de mensajería como sistemas externos con tag "Externo"; 5 contenedores; 6 componentes = los 6 paquetes de `paquetes.puml`; dinámica del flujo crítico; despliegue en un VPS. |
| Verificación del equipo | ADR-001 nombra textualmente "las integraciones externas (controlador de campo, servicio de mensajería)"; el README del Lab 04 ya los dibuja con `classDef externo`; `paquetes.puml` tiene exactamente 6 paquetes; `drivers.md` define los RF y R citados. |
| Decisión | **Aceptada**. Se registra elemento por elemento en `inventario.md` (E1). |

## Interacción 2 — Borrador completo del workspace y alcance de contenedores (Prompt IA 1)

| Campo | Contenido |
|---|---|
| Fecha | 17/10/2026 |
| Herramienta | Asistente IA (opencode) — rol arquitecto, **Prompt IA 1** con el inventario y el ADR-001 pegados |
| Prompt | "Escribe un workspace de Structurizr DSL con las vistas systemContext, container, component, dynamic (programar riego) y deployment (Producción). Usa SOLO las tecnologías del ADR-001, `!identifiers hierarchical` y relaciones con descripción y protocolo. Formato: solo el código DSL." |
| Propuesta de la IA | Borrador de `workspace.dsl` con 5 vistas; los contenedores del nivel 2 se limitan a los 5 del ADR-001 (PWA, API, Worker, Base de datos, Cola y caché), dejando Nginx, Prometheus y Grafana fuera de ese nivel. |
| Verificación del equipo | `structurizr.sh validate` → **exit 0** (1,6 s medidos); el ADR-001 solo enumera esos 5 contenedores y E2 exige que "coincidan con el ADR-001"; `despliegue.py` sí conserva Nginx/monitoreo como infraestructura de operación. |
| Decisión | **Aceptada con documentación**: la omisión queda registrada en `revision-c4.md` §5 (Alcance), no como olvido sino como decisión. |

## Interacción 3 — Arista Programación → Alertas (revisión de coherencia con Lab 05)

| Campo | Contenido |
|---|---|
| Fecha | 17/10/2026 |
| Herramienta | Asistente IA (opencode) — revisión de coherencia entre `secuencia-programar-riego.puml` y el modelo C4 |
| Prompt | "Coteja los pasos de la secuencia del Lab 05 con las relaciones del modelo C4 y con `paquetes.puml`; señala cualquier contradicción." |
| Propuesta de la IA | Agregar la relación Módulo Programación → Módulo Alertas en el nivel 3: el paso 7 de la secuencia es `ServicioRiego → notificarAlerta(...)`, y esa arista no existía en `paquetes.puml`. |
| Verificación del equipo | Se recalculó el grafo de dependencias: programación → lecturas → alertas ya lo hacía transitiva, así que el DAG sigue acíclico (la verificación C4 de `consistencia.md` seguía en pie); en `paquetes.puml` la dependencia está representada vía los paquetes, no con flecha directa. |
| Decisión | **Aceptada solo en el modelo C4**; `paquetes.puml` (Lab 05, ya etiquetado) no se modifica y la diferencia se documenta en `comparacion.md` §1. |

## Interacción 4 — `comparacion.md` con números presentados como medidos

| Campo | Contenido |
|---|---|
| Fecha | 17/10/2026 |
| Herramienta | Asistente IA (opencode) — redacción de `comparacion.md` (E4/E6) |
| Prompt | "Redacta la comparación secuencia UML vs vista dinámica y el experimento de renombrado del modelo, con los tiempos de la herramienta." |
| Propuesta de la IA | Presentar tiempos **estimados** ("validate ≈ 2 s, export ≈ 5 s, render ≈ 20 s") como si fueran observados. |
| Verificación del equipo | Se corrió `time` en cada comando: validate **1,6 s**; export c4plantuml **1,0 s**; export mermaid **1,0 s**; render de los 5 PNG **8 s**. El experimento de renombrado (`Cola y caché` → `Cola de tareas Redis`) midió con `sed` + export + `diff`: **0 / 1 / 1 / 2 / 1** líneas cambiadas por vista. |
| Decisión | **Corregida**: se reemplazaron todos los estimados por los valores medidos, y se anotó el método de medición. |

## Interacción 5 — Segundo revisor IA (Prompt IA 2 — auditor C4)

| Campo | Contenido |
|---|---|
| Fecha | 17/10/2026 |
| Herramienta | Asistente IA (opencode) — rol revisor, **Prompt IA 2** de la guía |
| Prompt | "Actúa como revisor de diagramas de arquitectura. Evalúa estas vistas exportadas [los 5 archivos `.puml` de `docs/architecture/c4/export/`] con la lista de revisión de c4model.com. Responde en tabla (vista, pregunta, cumple sí/no, evidencia, corrección sugerida). No inventes problemas." |
| Propuesta de la IA | 8 hallazgos: tecnología faltante en relaciones con personas; etiqueta del paso 2 distinta a la del modelo; versión de PostgreSQL; flecha de Redis que mezcla dos intenciones; leyenda/título/descripción en todas las vistas; ausencia de Nginx/monitoreo; arista Programación→Alertas ausente de `paquetes.puml`; códigos RF/QA/ADR poco autónomos. |
| Verificación del equipo | Cotejo uno por uno contra los exports: `Contexto.puml:23-24` (personas sin tecnología, igual que el ejemplo del docente); par origen→destino de los pasos dinámicos presente en componentes y ejemplo `POST /pedidos/{id}/pago` en la guía; `Despliegue.puml:34` muestra `PostgreSQL 16`; ADR-001 para el alcance; DAG recalculado para la arista. |
| Decisión | **3 falsos positivos descartados** (personas, etiquetas de pasos, versión de PostgreSQL), **1 aceptado sin cambio** (flecha Redis, igual que en la guía), **3 resueltos con documentación** (alcance, arista, acrónimos) y **1 confirmación de cumplimiento** (leyenda/título/descripción). Todo en `revision-c4.md` §4. |

## Interacción 6 — Explicación para público no técnico (Prompt IA 3)

| Campo | Contenido |
|---|---|
| Fecha | 17/10/2026 |
| Herramienta | Asistente IA (opencode) — rol redactor, **Prompt IA 3** de la guía adaptado al caso |
| Prompt | "Explica el diagrama de contexto de ChacraSmart Majes al dueño de una asociación de agricultores de Majes, no técnico, en máximo 120 palabras: qué hace el sistema, quién lo usa y de qué servicios externos depende. Evita la jerga técnica." |
| Propuesta de la IA | Borrador de `explicacion.md` de 119 palabras; en su primera versión terminaba con "recibe un aviso si algo falla". |
| Verificación del equipo | `wc -w` real sobre el texto; cada afirmación cotejada contra `workspace.dsl` (2 externos con tag "Externo", RF-02 a RF-07, ADR-003 "cierra solo… aunque se pierda la conexión", WhatsApp/SMS en R-06). Las alertas del modelo son por falta de agua y estado del riego (RF-05), no genéricas. |
| Decisión | **Corregida**: se acotó la frase de alertas al alcance real y se recortó el texto a **109 ≤ 120 palabras**. Tabla de verificación en `explicacion.md`. |
