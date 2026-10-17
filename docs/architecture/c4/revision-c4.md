# Revisión del modelo C4 con la lista oficial (E7)

**Lista aplicada**: resumen de la lista de revisión de c4model.com/diagrams/checklist (Tabla 3 de la guía).
**Método**: cada pregunta se evaluó sobre los artefactos exportados (`export/*.puml`, `export/*.mmd`, `img/*.png`)
y sobre `workspace.dsl`. Un "Sí" solo se marca con evidencia verificable (archivo + línea o conteo); un "No"
queda registrado con su corrección. Las cinco vistas: Contexto, Contenedores, Componentes, ProgramarRiego y
Despliegue.

## 1. Criterios generales (título, tipo de diagrama, alcance, leyenda)

| Vista | ¿Título que identifica el tipo? | ¿Descripción con alcance? | ¿Leyenda? |
|---|---|---|---|
| Contexto | Sí — `System Context View: ChacraSmart Majes` (`structurizr-Contexto.puml:2`) | Sí — "Nivel 1: ChacraSmart Majes y su entorno." | Sí — `SHOW_LEGEND(true)` (`structurizr-Contexto.puml:29`) |
| Contenedores | Sí — `Container View: ChacraSmart Majes` (`structurizr-Contenedores.puml:2`) | Sí — "Nivel 2: contenedores de ChacraSmart Majes." | Sí — `SHOW_LEGEND(true)` |
| Componentes | Sí — `Component View: ChacraSmart Majes - API ChacraSmart` (`structurizr-Componentes.puml:2`) | Sí — "Nivel 3: módulos del monolito modular (ADR-001)." | Sí — `SHOW_LEGEND(true)` |
| ProgramarRiego | Sí — `Dynamic View: ChacraSmart Majes - API ChacraSmart` (`structurizr-ProgramarRiego.puml:2`) | Sí — "Dinámico: programar un riego y abrir la válvula de forma remota (flujo crítico del Lab 05)." | Sí — `SHOW_LEGEND(true)` |
| Despliegue | Sí — `Deployment View: ChacraSmart Majes - Producción` (`structurizr-Despliegue.puml:2`) | Sí — "Despliegue en producción (MVP, un solo VPS — R-03)." | Sí — `SHOW_LEGEND(true)` (`structurizr-Despliegue.puml:47`) |

**5/5 vistas con título, alcance y leyenda.**

## 2. Elementos (nombre, tipo, descripción, tecnología, acrónimos, formas)

| Vista | Evidencia | ¿Cumple? |
|---|---|---|
| Contexto | 5 elementos con `$descr`: 2 personas (`Person`, `structurizr-Contexto.puml:17,20`), 1 sistema (:21), 2 externos con tag `"Externo"` (`workspace.dsl:24-25`) que el export renderiza con el estilo gris `#999999` (`structurizr-Contenedores.mmd:10,12`) | Sí |
| Contenedores | 5 contenedores, cada uno con tecnología: HTML / CSS / JavaScript (PWA), Python / Django + gunicorn, Celery, PostgreSQL 16, Redis. Ninguno se llama "Docker", "servidor" ni "nube" (lista de E2). Formas: `ContainerDb` y `ContainerQueue` en el export de contenedores (`structurizr-Contenedores.puml:25-26`); tags `Web Browser` / `Database` / `Queue` con sus estilos definidos en `workspace.dsl:10,20,21` y `:147-156` | Sí |
| Componentes | 6 componentes = los 6 paquetes de `paquetes.puml` (lecturas, programacion, control_valvulas, alertas, dispositivos, compartido), todos con `$descr` y `$techn` (`Django app` / `Python`, `structurizr-Componentes.puml:23-28`) | Sí |
| ProgramarRiego | 9 pasos numerados 1 a 9; cada elemento citado (contenedores y componentes) ya existe en el modelo | Sí |
| Despliegue | Nodos con sistema operativo / tamaño: "Android · navegador web (gama baja, R-05)", "conexión intermitente (R-04)", "Ubuntu 24.04 · 2 vCPU · 4 GB RAM (R-03, un solo VPS)", "Docker 27" (`structurizr-Despliegue.puml:19,23,30,31`); 6 instancias: PWA, API, Worker, Base de datos, Cola y caché + controlador (`softwareSystemInstance`) | Sí |

**Acrónimos**: los códigos `RF-xx` (requisitos funcionales), `QA-xx` (atributos de calidad), `R-xx` (restricciones)
y `ADR-xxx` (decisiones de arquitectura) aparecen siempre junto al significado en palabras, p. ej. "Crea, ejecuta
y finaliza programaciones de riego (RF-03)". Son referencias cruzadas al `drivers.md` y a los ADR del Lab 04; se
aclara su significado en la sección "Arquitectura C4 (Lab 06)" del README. **Cumple con nota** (hallazgo 7).

## 3. Relaciones (intención, dirección, protocolo, estilos)

| Vista | ¿Etiqueta con intención (verbo + objeto)? | ¿Dirección coherente? | ¿Protocolo donde corresponde? |
|---|---|---|---|
| Contexto | 5/5 ("Consulta humedad…", "Envía órdenes de riego…", etc.) | Sí — personas → sistema; sistema ⇄ externos en ambos sentidos | 3/5 con protocolo; las 2 sin tecnología son persona→sistema (ver hallazgo 2) |
| Contenedores | 9/9 | Sí — API→db (no a la inversa), API⇄controlador, worker→Redis | **9/9 con protocolo** (conteo: 0 relaciones con `$techn=""`) |
| Componentes | 21/21 | Sí — llamadas y dependencias en el sentido de uso | 10/21 con protocolo (HTTPS/JSON, HTTP/JSON, SQL/TCP, Redis protocol); las 11 sin tecnología son llamadas módulo→módulo dentro del mismo proceso (ver nota) |
| ProgramarRiego | 9/9 numerados 1..9 | Sí — cada paso en la dirección del flujo | 7/9 con protocolo; los 2 sin (pasos 4 y 7) son internos a la API |
| Despliegue | 6/6 ("Llama a la API", "Lee y escribe", …) | Sí | **6/6 con protocolo** |

**Nota sobre relaciones sin tecnología**: las 11 de la vista de componentes y los 2 pasos dinámicos son
comunicaciones en memoria dentro del mismo proceso (módulo → módulo); la guía pide protocolo "si corresponde" y
el ejemplo del docente hace lo mismo (`agro.api.pedidos -> agro.api.catalogo "Reserva stock"` sin tecnología).
**Estilos de línea**: todas las flechas del modelo son dependencias con la misma punta; no hay líneas de
despliegue ni punteadas que deban explicarse.

## 4. Segundo revisor IA (Prompt IA 2)

Prompt usado (adaptado de la guía): *"Actúa como revisor de diagramas de arquitectura. Evalúa estas vistas
exportadas de un modelo C4 [los 5 archivos `.puml` de `export/`] con la lista de revisión de c4model.com:
generales, elementos y relaciones. Responde en una tabla (vista, pregunta de la lista, cumple sí/no, evidencia,
corrección sugerida). No inventes problemas: si algo cumple, indícalo."*

| Vista | Hallazgo de la IA | Verificación del equipo | Veredicto |
|---|---|---|---|
| Contexto | "Faltan las tecnologías de las relaciones con las personas." | En el nivel 1 no se exige tecnología en persona→sistema; el ejemplo AgroConecta de la guía tampoco la pone (`productor -> AgroConecta "Descubre ofertas…"`). | **Falso positivo** (sin corrección) |
| ProgramarRiego | "El paso 2 (`POST /riegos`) no coincide con la etiqueta de la relación del modelo («Crea, ejecuta y finaliza programaciones…»)." | El par origen→destino del paso sí existe: PWA → Módulo Programación, definido en la vista de componentes (`workspace.dsl` dinámico usa solo relaciones ya modeladas). La guía hace lo mismo: paso `POST /pedidos/{id}/pago` frente a la relación "Gestiona pedidos". | **Falso positivo** (sin corrección) |
| Despliegue | "No se indica la versión de PostgreSQL." | El export muestra `$techn="PostgreSQL 16"` (`structurizr-Despliegue.puml:34`) y también `Redis` (sin versión, porque el ADR-001 no la fija). | **Falso positivo** (cumple) |
| Contenedores | "La flecha «Encola alertas y cachea el estado de las válvulas» mezcla dos intenciones." | Ambas operaciones ocurren hacia el mismo destino con el mismo protocolo (`Redis protocol`); el ejemplo de la guía acepta el mismo caso ("Encola tareas y lee caché → Correcto"). | Hallazgo real **aceptado sin cambio** (se documenta aquí) |
| Todas | "Hay leyenda, título y descripción en cada vista." | Confirmado con evidencia en §1 (5/5). | **Cumple** |
| Contenedores | "Faltan Nginx, Prometheus y Grafana, que sí aparecen en `despliegue.py` (Lab 04)." | Son infraestructura de operación (proxy, métricas, paneles), no contenedores con casos de uso del MVP; el ADR-001 solo nombra PWA, API, worker, base de datos y Redis. | Hallazgo real **resuelto con documentación** (§5) |
| Componentes | "Módulo Programación llama a Módulo Alertas, pero en `paquetes.puml` esa arista no existe." | La secuencia del Lab 05 muestra `ServicioRiego → Notificador`; en `paquetes.puml` la dependencia es transitiva (programación → lecturas → alertas) y `consistencia.md` C4 pasaba. Se documentó en `comparacion.md` §1 sin tocar el Lab 05. | Hallazgo real **resuelto con documentación** |
| Todas | "Los códigos RF-02 / QA-01 / ADR-002 no se entienden sin leer el repositorio." | Cada código va acompañado de su significado en palabras en la misma descripción; son trazabilidad, no jerga que oculte el sentido. | Hallazgo real **resuelto con documentación** (README aclara RF / QA / R / ADR) |

**Resumen del auditor**: 8 hallazgos → 3 falsos positivos, 1 aceptado sin cambio, 3 resueltos con
documentación y 1 "cumple". No se corrigió el modelo: ninguna corrección alteraba los diagramas.

## 5. Alcance documentado (hallazgo de Nginx / monitoreo)

`despliegue.py` (Lab 04) sí incluye Nginx, Prometheus y Grafana, y el README los dibuja en su figura de
arquitectura. No se modelaron como contenedores del nivel 2 porque son infraestructura de operación (proxy
reverso y observabilidad), no componentes con casos de uso del MVP; el ADR-001 —fuente obligatoria de E2— solo
enumera PWA, API, worker, base de datos y Redis. El despliegue real de Docker Compose los conserva. Esta es la
única diferencia de alcance entre el C4 y `despliegue.py` y queda registrada aquí.

## 6. Resultado

- **Título / alcance / leyenda**: 5/5 vistas (§1).
- **Elementos**: 5/5 vistas con nombre, tipo, descripción y tecnología donde corresponde (§2).
- **Relaciones**: etiqueta con intención en 50/50 flechas; protocolo en todas las relaciones entre procesos o
  sistemas distintos (§3).
- **Falsos positivos de la IA**: 3 (tecnología en personas, etiquetas de pasos dinámicos, versión de PostgreSQL).
- **Hallazgos aceptados o documentados**: 4 (flecha mixta Redis, alcance Nginx/monitoreo, arista
  programación→alertas, acrónimos RF/QA/R/ADR).
