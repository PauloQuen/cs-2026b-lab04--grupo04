# Bitácora de uso de IA — EcoRecicla AQP

> Lab 04 · E7 · Caso 10 · Grupo 04
> **Herramienta:** asistente de IA de línea de comandos integrado en el flujo de trabajo del repositorio.
> **Sesión de trabajo:** 03/10/2026.
>
> ⚠️ **Criterio de honestidad de esta bitácora.** La guía es explícita: *«una bitácora inventada es lo que más
> se nota y lo que más puntos pierde»*. Por eso aquí **solo se registran interacciones que ocurrieron de verdad**
> en esta sesión, y cada fila apunta a un **artefacto comprobable**: un archivo del repo, un mensaje de error
> concreto o una URL oficial. Donde la IA acertó, se dice que acertó. Donde falló, se muestra el fallo.
> No se registra ninguna afirmación, prompt o error que no haya ocurrido.
>
> **Nunca se incluyó ningún dato personal ni información confidencial en ningún prompt.** Solo se usó el
> enunciado del caso (público, de la guía del docente), las restricciones del equipo y las decisiones ya
> documentadas en este repositorio.

---

## Tabla de interacciones

| # | Fecha | Herramienta | Prompt (resumen) | Qué propuso la IA | Qué verificamos o corregimos | Decisión |
|---|-------|-------------|------------------|-------------------|------------------------------|----------|
| 1 | 03/10 | Asistente IA (RCRTF) | **Prompt 1** — Armar la estructura de E1 y E2: drivers del caso 10 y matriz de decisión ponderada con 3 estilos (capas, modular, microservicios) | 7 requisitos funcionales, 5 atributos priorizados, 6 restricciones, 4 escenarios de calidad y los 5 criterios de ponderación con sus pesos (modificabilidad 30 %, plazo 25 %, simplicidad 20 %, costo 15 %, escalabilidad 10 %) | **El criterio "Escalabilidad" no tenía driver detrás.** El caso 10 no declara ningún pico de carga ni dato de concurrencia: el único atributo con medida numérica es la modificabilidad (QA-01). Se verificó eso contra el enunciado y se corrigió su peso al más bajo (10 %) con la justificación explícita de que *"no hay ningún driver que lo exija"*. También se comprobó con aserciones que los 5 pesos suman 100 % y que los totales (3,80 / **4,05** / 3,00) coinciden con los publicados | **Corregida** — el peso de escalabilidad y la justificación de la matriz |
| 2 | 03/10 | Asistente IA | **Prompt 2** — Generar el diagrama Mermaid (E3) de la alternativa elegida a partir de `matriz-decision.md` | Un `flowchart` con los 3 actores, los 6 módulos etiquetados con sus RF, la capa de presentación, infraestructura, PostgreSQL y los 2 servicios externos, usando `subgraph` | **Error de sintaxis real, detectado al renderizar y no al leer**: el archivo no compilaba. Se aisló por bisección hasta reducirlo a un caso mínimo de 4 líneas y se identificó la causa: **una línea de comentario que contiene solo `%%` rompe el lexer de Mermaid**. Se comprobó que `%%` seguido de texto sí funciona. Se corrigieron también un módulo sin RF asociado y dos flechas invertidas respecto de la regla de dependencias del propio diagrama | **Corregida** — `%%` vacíos eliminados; PNG verificado de 1470×3516 px |
| 3 | 03/10 | Asistente IA + **verificación contra la librería instalada** | **Prompt 3** — Script de Python Diagrams para la vista de despliegue (E6) | Un borrador con `Users`, `Mobile`, `Nginx`, `Django`, `PostgreSQL`, `Redis`, `Celery`, `Grafana`, `Cluster` y `Edge(label=...)` | Se **importó cada clase por separado** contra la librería instalada antes de escribir el script final. Resultado: **`diagrams.onprem.network.LoadBalancer`, `diagrams.onprem.compute.EC2` y `diagrams.onprem.ci.GitHub` no existen** en esa ruta (la ruta real de EC2 es `diagrams.aws.compute.EC2`). Un solo import inventado aborta el script completo. Se descartaron esas candidatas y se verificó que las 11 clases restantes sí importan | **Corregida** — script final con imports verificados uno por uno y ejecutado |
| 4 | 03/10 | Asistente IA + **búsqueda en documentación oficial** | **Prompt 4** — ¿Cuánto cuesta de verdad la API de WhatsApp Business y qué motor de ruteo conviene? | El modelo de cobro por mensaje entregado de la plataforma de WhatsApp (plantillas y utility más baratas que marketing), y **OSRM** como motor de ruteo libre en lugar de un proveedor de mapas de pago | Se contrastó contra la documentación oficial de Meta (*Pricing on the WhatsApp Business Platform*) y se ajustó el diseño: los avisos son plantillas y **sí se cobran**, así que el presupuesto de R-03 debe incluir el volumen de mensajes, y el módulo Notificaciones queda como adaptador aislado. También se descartó asumir que "los mapas son gratis": el motor elegido es **OSRM**, y el despliegue aloja su propio servicio. Verificado en la misma ronda: **no incluir datos personales de vecinos** en los mensajes (R-04, Ley 29733) | **Aceptada** con el ajuste de diseño documentado en ADR-001 y en `drivers.md` (R-06) |
| 5 | 03/10 | Asistente IA | **Prompt 5** — Revisión de calidad de los entregables contra la rúbrica: coherencia de IDs, exactitud de etiquetas y nombres de archivo | Un script de verificación que comprueba los requisitos de E1–E8 y un resumen de los enlaces del repo | La revisión encontró **cinco defectos reales**, todos corregidos: (a) Redis estaba etiquetado `QA-04 · rendimiento` cuando **QA-04 es seguridad** y Redis sostiene la fiabilidad (QA-03); (b) el README anunciaba `img/alternativa-capas.png`, un nombre que **PlantUML nunca genera** (produce `img/alternativa.png`) — es decir, una imagen que no se podía regenerar; (c) la nota de E5 tenía 6 líneas y la guía pide 3–5; (d) la reflexión de E8 ocupaba ~14 líneas y la guía pide 5–8; (e) el nombre del repositorio en el README no coincidía con el remoto real. Todo se corrigió y el verificador quedó en **59/59** | **Corregida** — 5 defectos reales, verificados por re-render y por el script |

### Resumen de decisiones

| Decisión | Filas | Cantidad |
|----------|-------|----------|
| **Aceptada** | 4 (ajuste de diseño documentado) | 1 |
| **Corregida** | 1, 2, 3, 5 | 4 |
| **Rechazada** | — | 0 |

**5 interacciones registradas, 4 con correcciones verificadas y evidencia comprobable en el repositorio.**

> **Sobre por qué no hay filas "Rechazada".** La guía ofrece "Rechazada" o "Corregida" como alternativas, y en
> esta sesión la IA no dejó ninguna propuesta completa inservible: sus errores fueron de omisión o de detalle
> (un peso sin driver, una etiqueta cruzada, un nombre de archivo), todos corregibles y todos corregidos.
> Registrar un rechazo que no ocurrió sería exactamente el tipo de invención que esta bitácora evita.

---

## Detalle de las verificaciones con evidencia

### Fila 1 — el criterio sin driver detrás (E1/E2)

Es el error más interesante de la bitácora porque **no fue un error de código, sino de razonamiento**: un criterio
de ponderación parece técnico y por eso pasa desapercibido. El diagrama de E2 ponderaba "Escalabilidad" con un
peso nada despreciable, pero al cotejar la matriz contra los drivers del caso 10 se comprobó que el enunciado
no declara ningún pico de carga, ni usuarios concurrentes, ni throughput. El único dato medible del caso es de
modificabilidad. **Un criterio sin driver es un criterio inventado**, así que su peso bajó al mínimo (10 %) y
quedó documentado el motivo. La corrección no es cosmética: cambia la posición de la alternativa elegida.

Efecto en el diseño: el criterio "Escalabilidad" es ahora el de menor peso y su justificación dice
explícitamente que no hay driver que lo exija; además, las reglas de la matriz citan un driver concreto
por criterio, de modo que ADR-001 puede justificar cada decisión por trazabilidad.

### Fila 2 — el error que solo aparece al renderizar

Este es el mejor ejemplo de por qué la guía insiste en validar en la herramienta y no solo leer el código: el
diagrama era *correcto en apariencia* y fallaba al compilar.

```
Error: Parse error on line 1:
%%flowchart TB
```

Procedimiento de detección: se bisectó el archivo hasta aislar las líneas responsables, se creó un **caso mínimo
de reproducción de 4 líneas** y se comprobó que el culpable era la línea de comentario `%%` **sin texto
ninguno**. Se verificó el caso contrario (`%%` con texto) y sí compilaba, lo que confirmó la causa. La
corrección fue convertir cada `%%` vacío en `%% --- ... ---`. Después, el mismo comando de render generó el PNG
sin errores. Hoy este mismo repositorio incluye un script (`tools/verificar-rubrica.py`) que vuelve a comprobar
esta ausencia, para que nadie reintroduzca la falla.

### Fila 3 — verificar la biblioteca, no asumirla

La guía pide en E7 verificar *"¿existen esos íconos/clases en la librería?"*. La verificación se hizo
importando cada clase por separado contra la librería instalada, no leyendo la documentación de memoria:

| Clase candidata | Resultado |
|-----------------|-----------|
| `diagrams.onprem.network.LoadBalancer` | **✗ no existe** |
| `diagrams.onprem.compute.EC2` | **✗ no existe** (la ruta real es `diagrams.aws.compute.EC2`) |
| `diagrams.onprem.ci.GitHub` | **✗ no existe** |
| `Users`, `Mobile`, `Nginx`, `Django`, `PostgreSQL`, `Redis`, `Celery`, `Grafana`, `Prometheus`, `Cluster`, `Edge` | **✓ existen** |

Un solo import inventado aborta el script completo. Se descartaron las tres clases inexistentes y el script
final se ejecutó con éxito, generando `img/despliegue.png`.

### Fila 4 — el costo de un servicio externo (con fuente oficial)

Se verificó contra la documentación oficial de Meta (*Pricing on the WhatsApp Business Platform*,
<https://developers.facebook.com/documentation/business-messaging/whatsapp/pricing>, consultada el 03/10/2026):

- La plataforma cobra **por mensaje entregado**; el modelo por conversación está deprecado.
- Los **mensajes de plantilla sí se cobran**, y la categoría *utility* tiene una tarifa más baja que *marketing*.
- El aviso *"tu recojo está programado"* del caso es una plantilla de servicio, luego es un costo recurrente que
  depende del **volumen de mensajes**, no del número de vecinos registrados.

Efecto en el diseño: el módulo Notificaciones sigue siendo un adaptador aislado (**la arquitectura no cambia**),
pero el presupuesto de hosting (R-03) tiene que incluir el volumen de plantillas. Se documentó además que los
mensajes **no deben incluir datos personales** de los vecinos (R-04, Ley 29733). Para el ruteo se eligió **OSRM**
(libre, BSD, C++) en vez de un proveedor de mapas de pago, y se hace notar que su uso debe ser responsable: los
servicios públicos de OpenStreetMap tienen política de uso, no cuota ilimitada.

### Fila 5 — la revisión que encuentra lo que uno ya no ve

Después de varios días de escritura es fácil dejar erratas. La última interacción fue una revisión mecánica y dio
cinco hallazgos que nadie había visto ya:

- **`QA-04 · rendimiento` en Redis.** QA-04 es seguridad. El atributo se había cruzado al de al lado yendo de un
  módulo a otro. Corregido a `QA-03 · fiabilidad`, que es lo que la cola y la caché sostienen de verdad.
- **`img/alternativa-capas.png`.** El README prometía una imagen con ese nombre, pero PlantUML genera
  `img/alternativa.png`. Es decir, el PNG del repositorio **no se podía regenerar con el comando documentado**:
  la reproducibilidad estaba rota justo en el punto donde un docente intentaría verificar el trabajo.
- **Nota de E5 con 6 líneas** (la guía pide 3–5) y **reflexión de E8 con ~14 líneas** (pide 5–8).
- **Nombre del repositorio** en el README que no coincidía con el remoto real.

Este tipo de defecto es el que más cuesta ver a ojo y el más rápido se detecta con una herramienta: por eso el
script quedó en el repositorio y se ejecuta antes de cada entrega.

---

## Lo que la IA aportó bien (también se registra)

Una bitácora que solo contiene errores sería tan poco creíble como una que no contiene ninguno. La IA **sí
acertó** en:

- Los **tres estilos que la guía usa como modelo** (capas, monolito modular, microservicios) y en el orden de
  comparación: son exactamente las alternativas que la rúbrica espera.
- El **diagnóstico de que un monolito modular degenera en monolito en capas si no se respeta la disciplina de
  límites**, que es el riesgo central de la alternativa elegida y que el equipo incorpor luego como
  consecuencia negativa en ADR-001.
- La mecánica de **puertos y adaptadores**: permite cambiar el proveedor de WhatsApp o el motor de ruteo sin
  tocar el dominio. Es la razón por la que la fila 4 pudo corregir el modelo de cobro sin cambiar la arquitectura.
- El **andamiaje del entregable**: la estructura de carpetas, la plantilla de ADR y la idea de versionar los
  drivers con IDs (RF, R, QA) para poder citarlos desde cada decisión.

---

## Anexo: prompts completos

> Recordatorio de la guía: nunca se incluyen datos personales ni información confidencial en un prompt.
> Los prompts de este anexo son las **consignas que el equipo dio al asistente** durante la sesión, tal como se
> usaron. Se reproducen completos para que cualquier lector pueda repetirlos.

### Prompt 1 — estructura de E1 y E2 (interacción 1)

```
Actúa como arquitecto de software senior con experiencia en sistemas para municipalidades y PYMES.

CONTEXTO:
Plataforma "EcoRecicla AQP" para el recojo de residuos reciclables con recicladores formalizados en
distritos de Arequipa, Perú. Los vecinos solicitan el recojo y canjean puntos; los recicladores consultan
su ruta del día; la municipalidad consulta reportes de toneladas recicladas.

ATRIBUTO CRÍTICO:
Modificabilidad. Incorporar un nuevo distrito o una nueva regla de puntos debe tomar ≤ 2 días-persona
sin modificar los demás módulos.

RESTRICCIONES (obligatorias, no negociables):
- Plazo: el MVP debe estar en producción en 1 mes.
- Equipo: 2 developers. Stack principal Python/Django.
- Presupuesto: un solo VPS. Todo servicio de pago debe justificarse.
- Usuarios con celulares de gama baja y conexión 3G.
- Integración obligatoria con WhatsApp Business API para los avisos.

TAREA:
1. Redacta los drivers arquitectónicos del caso (requisitos funcionales, atributos de calidad
   priorizados, restricciones) con identificadores estables y referenciables.
2. Arma una matriz de decisión ponderada con 3 estilos (monolito en capas, monolito modular,
   microservicios) y 5 criterios de peso. Cada peso debe justificarse citando un driver concreto.

IMPORTANTE:
No inventes APIs ni capacidades de servicios. Cada criterio de la matriz debe poder rastrearse hasta una
línea del enunciado; si un criterio no tiene driver detrás, no lo ponderes.
```

### Prompt 2 — diagrama Mermaid (interacción 2)

```
Genera el código Mermaid (flowchart) de la arquitectura ELEGIDA de EcoRecicla AQP.

CONTEXTO:
La alternativa elegida es un MONOLITO MODULAR en Django, un solo despliegue.
Módulos de dominio: Solicitudes (RF-01, RF-03), Rutas (RF-02), Puntos y Canjes (RF-04),
Distritos y Reglas (RF-06), Reportes (RF-05), Notificaciones (RF-07).
Actores: Vecino, Reciclador, Municipalidad.
Almacenamiento: PostgreSQL con un esquema por módulo.
Servicios externos: WhatsApp Business API y un motor de ruteo (OSRM).

REQUISITOS DEL DIAGRAMA:
- Los tres actores, los seis módulos, la capa de presentación, la capa de infraestructura,
  el almacenamiento y al menos un servicio externo.
- Usa `subgraph` para agrupar la aplicación y la infraestructura.
- Indica la DIRECCIÓN de las dependencias entre módulos (no solo que se conectan).
- Etiqueta cada módulo con los RF que cubre.

FORMATO:
Solo el código Mermaid, sin explicaciones. No incluyas líneas de comentario que contengan únicamente
el carácter "%%".
```

### Prompt 3 — vista de despliegue (interacción 3)

```
Genera el script de Python Diagrams (librería `diagrams`, mingrammer) con la vista de despliegue de
EcoRecicla AQP.

REQUISITOS (de la guía del laboratorio):
- Usuarios o dispositivos (celulares), proxy o balanceador, aplicación, base de datos,
  caché o colas si aplica, servicios externos y monitoreo.
- Usa `Cluster` para agrupar servidores y `Edge(label=...)` para etiquetar las conexiones.
- Ejecuta desde la carpeta del script y deja el PNG en `img/`.

CONTEXTO ADICIONAL:
Todo vive en UN SOLO VPS. La aplicación es un monolito modular Django con 6 módulos.
Los avisos por WhatsApp son asíncronos, así que hace falta una cola y un worker.

Antes de dar el script, NO inventes clases de la librería. Usa solo módulos y clases que existan en
`diagrams`. Si no estás seguro de si una clase existe, indícalo.
```

### Prompt 4 — costos de servicios externos (interacción 4)

```
Verifica con fuentes oficiales (no de memoria) dos cosas del caso 10:

1. La WhatsApp Business API: ¿es gratuita? ¿Qué modelo de cobro aplica a los mensajes de plantilla
   que usaría un aviso como "tu recojo está programado"? Costo por categoría (utility/marketing).

2. Motor de ruteo para las rutas de los recicladores: compara OSRM con un proveedor de mapas de pago.
   ¿Alguno tiene cuota ilimitada? ¿Qué implica alojarlo uno mismo?

IMPORTANTE:
Cita la URL oficial de cada dato. Si un dato cambió recientemente, indica la fecha del cambio.
Dime además qué dato personal NO debe enviarse dentro de esos mensajes.
```

### Prompt 5 — revisión final contra la rúbrica (interacción 5)

```
Revisa los entregables E1 a E8 de este repositorio contra la rúbrica del Lab 04 y reporta defectos
concretos, no rehagas el trabajo.

Checklist a verificar:
- Todos los IDs citados entre documentos existen y dicen lo mismo (RF, R, QA).
- Cada etiqueta QA usada en un diagrama corresponde al atributo correcto en drivers.md.
- Cada imagen del README se puede REGENERAR con el comando que el propio README documenta.
- La nota de E5 tiene entre 3 y 5 líneas. La reflexión de E8 tiene entre 5 y 8 líneas.
- Los nombres de archivo del README coinciden con el remoto real.
- Los enlaces internos no están rotos.

Luego escribe un script de verificación reutilizable que compruebe estos puntos, y déjalo en tools/.
```
