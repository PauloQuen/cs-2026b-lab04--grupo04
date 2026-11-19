# Hoja de Ruta de Delegación Progresiva y Humano en el Circuito (E6)

**Proyecto:** ChacraSmart Majes — Construcción de Software 2026-B  
**Caso 9:** Riego Inteligente con Falla Segura (QA-01 / ADR-003)  
**Referencia:** Albada (2025, cap. 13) y Koenigstein (2026, cap. 2)  

---

## 1. Mecanismo Activo de Humano en el Circuito (`aprobar_edicion`)

En `agentes/agente/politica.py` (`aprobar_edicion_consola`) y `agentes/orquestador.py --aprobar-edicion`, el ejecutor transiciona al estado **`ESPERANDO_APROBACION`** antes de aplicar cualquier `editar_archivo`:

1. El sistema muestra la ruta destino y el fragmento exacto `antes -> despues`.
2. Solicita confirmación humana por consola validando estrictamente `"s"` o `"n"` (rechaza entradas ambiguas).
3. Si la respuesta es `"n"`, la edición se bloquea (`BLOQUEADO`) y el agente recibe la observación de rechazo para replantear.
4. En ningún escenario el agente tiene permiso para editar `tests/`, `agentes/pruebas_agente/` ni ejecutar `git push` / merge sobre `main`.

---

## 2. Matriz de Delegación Progresiva (4 Etapas para ChacraSmart Majes)

| Etapa | Rol Humano | Nivel de Autonomía y Permisos del Agente | Alcance en ChacraSmart Majes | Evidencia Objetiva de Trazas para Avanzar de Etapa |
|---|---|---|---|---|
| **1 (Actual)** | **Humano Ejecutor / Control Estrecho** | Solo lectura (`leer_archivo`, `buscar`, `mapa_repo`) + propuestas en sandbox con `aprobar_edicion` obligatoria (`"s"/"n"`) por cada edición. | Issues acotados fuera de hardware físico (ej. `ISSUE-03`: validación de humedad). | 100 % de pruebas en verde sin modificar `tests/`, **0** violaciones de contrato en 10 corridas seguidas y rechazo correcto de inyecciones indirectas (`curl`). |
| **2** | **Humano Revisor** | El agente edita archivos en una rama aislada y corre `pytest`/`radon`/`lint-imports` sin pausa por línea; el humano revisa y aprueba el Pull Request completo. | Módulos de aplicación y políticas agronómicas (`politicas.py`, `operaciones_campo.py`). | Al menos **20 PRs** fusionados sin regresiones en producción, tasa de aprobación del crítico >= 90 % en ronda 1 y `radon cc <= 10` sostenido. |
| **3** | **Humano Colaborador** | Orquestador actor-crítico crea ramas y abre PRs con diagnóstico completo; el humano colabora solo en cambios de seguridad/autorización (`ISSUE-02`, RLS). | Refactors transversales y mantenimiento de adaptadores (`actuadores.py`, `ia.py`). | **0** incidentes de seguridad (`OWASP LLM01 / LLM06`) durante 1 mes de CI, consumo de contexto acotado (< 10 000 chars) y cobertura >= 90 %. |
| **4 (Meta futura)** | **Humano Gobernador** | Agente con agenda de mantenimiento en ramas de bajo riesgo y políticas dinámicas; el humano define guardrails, presupuestos (`max_pasos`) y aprueba releases críticos (`QA-01`). | Mantenimiento rutinario de documentación, tests y issues no críticos (nunca firmware ni válvulas físicas sin firma humana). | Auditoría trimestral limpia de trazas `.jsonl`, fitness functions `FF-01`–`FF-07` en verde continuo y aprobación explícita de dirección técnica. |

---

## 3. Regla Invariable de Protección (`QA-01 / ADR-003`)

Independientemente del nivel de delegación alcanzado, **ningún agente autónomo** recibe jamás credenciales de producción, acceso directo al broker MQTT en campo ni capacidad para desactivar los temporizadores locales de apagado seguro de las electroválvulas en Majes.
