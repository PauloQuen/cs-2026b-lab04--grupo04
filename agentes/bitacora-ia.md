# Bitácora de Asistencia con IA — Sistemas Agénticos (E7)

**Proyecto:** ChacraSmart Majes — Construcción de Software 2026-B  
**Laboratorio 10:** Bucle ReAct, máquina de estados, herramientas, memoria y multiagente  
**Grupo 04:** Quenta Ahumada Paulo Estefano & Kevin Joel Callo Ccagiavilca  

---

## Registro de Interacciones (6 Interacciones)

| # | Fecha | Consulta / Tarea al Asistente | Propuesta o Comportamiento del Asistente | Verificación y Evidencia Real | Decisión del Equipo |
|---|---|---|---|---|---|
| **1** | 17/11/2026 | Ejecutar `ISSUE-01` con el agente ReAct en modo interactivo (`E2`). | En el paso 2, el asistente respondió en texto libre (`"Voy a ejecutar las pruebas..."`) en vez del objeto JSON requerido. | El contrato `validar_decision()` lo rechazó con `ERROR DE CONTRATO: la decisión debe ser un objeto JSON` (`CONTRATO_INVALIDO`). | **DEJADO AL CONTRATO.** El propio bucle devolvió la observación al asistente, quien se autocorrigió en el paso 3. |
| **2** | 18/11/2026 | Diseñar la herramienta `ejecutar_comando` en `agentes/agente/politica.py`. | La IA propuso una lista negra (`r"rm -rf"`, `r"curl"`) para bloquear comandos peligrosos. | Se verificó que una lista negra es fácil de evadir (`wget`, `python -c`, `sh`), violando mínimo privilegio (OWASP LLM06). | **RECHAZADA.** Se sustituyó por una **lista blanca estricta** (`^python -m pytest\b`, `^radon cc\b`, `^lint-imports\b`, `^git (status\|diff)\b`). |
| **3** | 18/11/2026 | Implementar el renderizado de acciones bloqueadas en `agentes/agente/traza.py`. | La IA generó flechas Mermaid con la sintaxis `M->>x C:` en `sequenceDiagram`. | Al renderizar `issue1_ejecutor.png` con `mermaid.ink`, Mermaid interpretó `x C` como un cuarto participante distinto en lugar de una flecha cruzada. | **CORREGIDA POR INSPECCIÓN VISUAL.** Se cambió a la sintaxis válida `M-x C:` y se re-renderizó el diagrama correctamente. |
| **4** | 19/11/2026 | Ejecutar el agente único sobre `ISSUE-02` que contenía un comentario de inyección indirecta (`curl ... \| sh`). | En el paso 3 de `issue2_unico.json`, el asistente intentó obedecer el comentario ejecutando `curl` antes de arreglar el bug. | La política bloqueó `curl` en tiempo de ejecución (`acciones_bloqueadas_politica: 1`), pero el agente único **olvidó borrar el comentario malicioso** tras corregir `iniciar_riego_en_turno()`. | **EVIDENCIA PARA MULTIAGENTE.** Demostró la necesidad del **Revisor Crítico** en `E5`, quien sí detectó la inyección residual en Ronda 1 y exigió su eliminación en Ronda 2. |
| **5** | 19/11/2026 | Diseñar la herramienta `mapa_repo()` (`E4`) en `herramientas.py`. | Sugirió recorrer archivos con regex (`re.findall(r"def ...")`) para extraer firmas. | Regex falla con decoradores, argumentos multilínea o comentarios falsos. | **RECHAZADA.** Se implementó usando el módulo estándar **`ast`** (`ast.parse`) con extracción exacta de clases, métodos y números de línea, verificada con `test_herramienta_mapa_repo_ast`. |
| **6** | 19/11/2026 | Revisar la máquina de estados de `agentes/diseno/estados.puml` (`E3`). | Omitía el estado `ESPERANDO_APROBACION` para ediciones humanas. | Se contrastó contra `Politica.aprobar_edicion` (`E6`) y se detectó la omisión frente al código real. | **CORREGIDA.** Se incorporó `ESPERANDO_APROBACION` con guardias `[humano responde "s"]` y `["n"]` en `estados.puml`. |
