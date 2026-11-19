# ADR-010: Arquitectura del sistema agéntico para mantenimiento asistido

- Estado: Aceptado
- Fecha: 2026-11-21
- Decisores: Quenta Ahumada Paulo Estefano, Kevin Joel Callo Ccagiavilca

## Contexto
El mantenimiento evolutivo de **ChacraSmart Majes** exige diagnosticar fallos reales (`ISSUE-01` cierre seguro ante corte de red, `ISSUE-02` autorización de turnos entre agricultores, `ISSUE-03` validación de humedad en sensores), localizar la causa en el repositorio, editar código seguro y verificar con `pytest` y `radon` sin comprometer el atributo crítico **QA-01** ni exponer el código ante inyecciones indirectas (**OWASP LLM01**) o exceso de agencia (**OWASP LLM06**).

## Alternativas consideradas
1. **Alternativa A (Flujo de trabajo fijo / pipeline rígido):** Ejecutar un único prompt `v3` que reciba el issue y genere un parche completo en un solo paso sin herramientas.
   * *Desventaja:* No puede explorar archivos dinámicamente, inspeccionar firmas reales ni iterar tras errores de pruebas (`pytest`).
2. **Alternativa B (Enjambre autónomo sin límites ni aprobación humana):** Múltiples agentes con acceso abierto a consola (`shell`), edición sobre `tests/` y `git push` directo a `main`.
   * *Desventaja:* Incurre en exceso de agencia (**OWASP LLM06**), riesgo de modificar pruebas para forzar verdes y vulnerabilidad crítica ante comentarios maliciosos (`curl | sh`).
3. **Alternativa C (Agente ReAct como máquina de estados + Actor-Crítico acotado con humano en el circuito — Seleccionada):** Combina arquetipos adaptados al riesgo de cada issue con políticas deterministas de mínimo privilegio.

## Decisión
Usaremos la siguiente arquitectura para el subsistema `agentes/`:
1. **Arquetipo y Coordinación por Parsimonia:**
   - **Agente único ReAct** para issues locales acotados (`ISSUE-01`, `ISSUE-03`).
   - **Gestor (Planificador de solo lectura) + Actor-Crítico** (Ejecutor + Revisor de solo lectura, máximo `2` rondas) para issues de seguridad o multitenencia (`ISSUE-02`).
2. **Máquina de Estados y Contrato Estructurado (`agente/nucleo.py`, `agente/contrato.py`):**
   - Estados explícitos (`INICIO`, `DECIDIENDO`, `VALIDANDO_CONTRATO`, `CONTRATO_INVALIDO`, `EVALUANDO_POLITICA`, `ESPERANDO_APROBACION`, `EJECUTANDO`, `OBSERVANDO`, `BLOQUEADO`, `LIMITE_ALCANZADO`, `FINALIZADO`).
   - Toda decisión debe cumplir el protocolo JSON (`pensamiento` + `accion`/`args` o `final`).
3. **Herramientas con Mínimo Privilegio y Memoria (`agente/herramientas.py`, `agente/politica.py`):**
   - Sandbox estricto sobre la copia de trabajo, lista blanca de comandos (`pytest`, `radon`, `lint-imports`, `git status/diff`), rutas protegidas (`tests/`, `agentes/pruebas_agente/`), herramienta AST `mapa_repo()` y memoria de pizarra `anotar()` / `leer_notas()` en `notas.md`.
4. **Límites y Rol Humano (`delegacion.md`):**
   - Presupuesto estricto (`max_pasos = 12–15`, `MAX_RONDAS = 2`), confirmación humana `aprobar_edicion` (`"s"/"n"`) y aprobación humana obligatoria para todo Pull Request hacia `main`.

## Consecuencias
- **Positivas:**
  - Bloqueó el 100 % de decisiones mal formadas (`CONTRATO_INVALIDO` en `ISSUE-01`) e intentos de ejecución maliciosa (`curl | sh` en `ISSUE-02`).
  - La herramienta `mapa_repo()` + memoria de notas redujo en un **28.6 %** los pasos necesarios (`7 -> 5`) en `ISSUE-03`.
  - El revisor crítico detectó en Ronda 1 una inyección indirecta residual que el agente único había dejado en el archivo.
  - Trazabilidad completa mediante registros `.jsonl` y diagramas Mermaid autogenerados.
- **Negativas / riesgos asumidos:**
  - El esquema Actor-Crítico consume más pasos (`13` vs `5`) y más contexto acumulado (`19,377` vs `5,492` caracteres), por lo que su uso se reserva exclusivamente para cambios críticos de seguridad y autorización.
