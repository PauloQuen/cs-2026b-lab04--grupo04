# Lienzo de Diseño del Sistema Agéntico — ChacraSmart Majes (E1)

> **Laboratorio 10:** Sistemas agénticos en la construcción de software  
> **Caso 9:** ChacraSmart Majes · **Grupo 04:** Quenta Ahumada Paulo Estefano & Callo Ccagiavilca Kevin Joel  

---

## 1. Las 7 Decisiones de Diseño

| # | Decisión de diseño | Elección para ChacraSmart Majes | Justificación técnica (Secciones 1.1–1.8) |
|---|---|---|---|
| **1** | **¿Agente o flujo de trabajo fijo?** | **Agente** para resolución de issues; **flujo fijo** para validación de telemetría/JSON en producción. | La corrección de bugs (`ISSUE-01..03`) exige explorar archivos, reproducir fallos con `pytest`, localizar causas y editar código (los pasos no son fijos de antemano). En cambio, validar una lectura de humedad en producción o ejecutar `promptfoo` en CI sigue un flujo fijo determinista más barato y seguro. |
| **2** | **Arquetipo de agente** | **ReAct** (exploración autónoma de código) + **Planificador-Ejecutor / Actor-Crítico** para issues de autorización/seguridad. | ReAct intercala pensamiento, acción y observación para diagnosticar fallos (`ISSUE-01`, `ISSUE-03`). En `ISSUE-02` (seguridad/turnos de riego), el par actor-crítico separa quién edita de quién audita el diff antes de pasar al humano. |
| **3** | **Herramientas** | Mínimo privilegio: `listar_archivos`, `leer_archivo`, `buscar`, `editar_archivo`, `ejecutar_pruebas`, `ver_cambios`, `ejecutar_comando` (lista blanca), `mapa_repo`, `anotar`, `leer_notas`. | Se evita dar shell abierto sin restricciones (`rm`, `curl`, acceso fuera del sandbox). `editar_archivo` exige coincidencia única (`count == 1`) para evitar ediciones ambiguas. |
| **4** | **Memoria** | **Corto plazo** (historial de sesión) + **Notas / pizarra** (`notas.md` mediante `anotar()` y `leer_notas()`). | El historial ReAct crece linealmente; las notas en `notas.md` permiten conservar hipótesis, firmas del repositorio (`mapa_repo`) y archivos ya verificados evitando relecturas redundantes. |
| **5** | **Coordinación multiagente** | **Agente único** en issues locales (`ISSUE-01`, `ISSUE-03`); **Gestor + Actor-Crítico** (máx. 2 rondas) en `ISSUE-02` (seguridad). | Por el principio de parsimonia (Albada, 2025, cap. 8), no se añaden múltiples agentes donde uno basta. Para `ISSUE-02`, el revisor de solo lectura detecta inyecciones indirectas y fugas de autorización sin poder editar archivos. |
| **6** | **Rol humano (Human-in-the-Loop)** | **Aprobar o rechazar** cada edición (`aprobar_edicion`) + revisión obligatoria del Pull Request. | El sistema controla software ciberfísico crítico (QA-01: electroválvulas en Majes). Ningún agente tiene permiso para fusionar cambios a `main` ni modificar `tests/`. |
| **7** | **Control y límites** | Contrato JSON estricto (`validar_decision`), política por rol, `rutas_protegidas=("tests/",)`, lista blanca de comandos, máx. `12–15` pasos y máx. `2` rondas. | Previene la "trampa del JSON frágil", bucles infinitos, costos desbocados y el exceso de agencia (**OWASP LLM06**). |

---

## 2. Cuándo NO Usar un Agente en ChacraSmart Majes

* **Cierre seguro de válvula ante corte de red (`QA-01 / ADR-003`):** Debe ser **100 % determinista** mediante temporizador local en hardware, jamás delegado a un agente LLM por latencia e incertidumbre.
* **Validación de contratos JSON Schema de prompts (Lab 09):** Es un flujo fijo y barato con `jsonschema.validate()`, sin necesidad de razonamiento agéntico.
