# Bitácora de uso de IA — ChacraSmart Majes

> Lab 04 · E7 · Caso 9 · Grupo 04
> **Herramienta:** asistente de IA de línea de comandos integrado en el flujo de trabajo del repositorio.
> **Sesión de trabajo:** 04/10/2026.
>
> ⚠️ **Criterio de honestidad de esta bitácora.** La guía es explícita: *«una bitácora inventada es lo que más
> se nota y lo que más puntos pierde»*. Por eso aquí **solo se registran interacciones que ocurrieron de verdad**
> en esta sesión, y cada fila apunta a un **artefacto comprobable**: un archivo del repo, un mensaje de error
> concreto o un cálculo. Donde la IA acertó, se dice que acertó. Donde falló, se muestra el fallo.
>
> **Nunca se incluyó ningún dato personal ni información confidencial en ningún prompt.** Solo se usó el
> enunciado del caso (público, de la guía del docente), las restricciones del equipo y las decisiones ya
> documentadas en este repositorio.

---

## Tabla de interacciones

| # | Fecha | Herramienta | Prompt (resumen) | Qué propuso la IA | Qué verificamos o corregimos | Decisión |
|---|-------|-------------|------------------|-------------------|------------------------------|----------|
| 1 | 04/10 | Asistente IA (RCRTF) | **Prompt 1** — Armar E1 y E2 del caso 9: drivers de un sistema de riego inteligente y matriz de decisión con 3 estilos (capas, modular, eventos) | 7 requisitos funcionales, 4 atributos priorizados, 7 restricciones y los 5 criterios de ponderación con sus pesos (fiabilidad/safety 30 %, plazo 25 %, simplicidad 20 %, costo 15 %, modificabilidad 10 %) | **La IA propuso que "el servidor detecta la desconexión y cierra la válvula".** Es lógicamente imposible: sin conexión no llega ninguna orden (R-04). Se verificó razonando sobre QA-01 y R-04, y se corrigió toda la cadena: el criterio crítico pasó a ser *Fiabilidad y protección* y la falla segura se asignó al **controlador de campo con temporizador local** (ADR-003). También se comprobó con aserciones que los 5 pesos suman 100 % y que los totales coinciden con los publicados | **Corregida** — la responsabilidad de la falla segura se movió del servidor al controlador |
| 2 | 04/10 | Asistente IA | **Prompt 2** — "Abogado del diablo": criticar duramente la alternativa recomendada | Que un broker de mensajes "retiene las órdenes y hace el control más confiable", y que microservicios con Kubernetes serían necesarios "por escalabilidad" | Se contrastó con R-01 (1 mes), R-02 (2 developers), R-03 (un solo VPS). **El broker no mejora la seguridad de las válvulas**: la falla segura depende del temporizador local, no del transporte del mensaje. Y microservicios con orquestador exceden el plazo, el presupuesto y la capacidad operativa del equipo. Ambas propuestas se descartaron; C quedó en 3,05 | **Rechazada** — microservicios/Kubernetes y el argumento de confiabilidad del broker |
| 3 | 04/10 | Asistente IA + **ejecución del código generado** | **Prompt 3** — Generar el diagrama Mermaid (E3) y el script de Python Diagrams (E6) a partir de `matriz-decision.md` | Un `flowchart` con 2 actores, 5 módulos etiquetados con sus RF, PostgreSQL, controlador de campo y servicio de mensajería; y un script de despliegue con `Users`, `Mobile`, `Nginx`, `Django`, `PostgreSQL`, `Redis`, `Celery`, `Prometheus`, `Grafana`, `Server`, `Cluster` y `Edge(label=...)` | Se **ejecutó** el script en lugar de leerlo. Falló con `NameError: name 'Server' is not defined`: la IA usó `Server(...)` para el controlador de campo sin añadir `from diagrams.onprem.compute import Server`. Un import faltante aborta el script completo. Se añadió el import y se verificó que el script corre y genera el PNG. El Mermaid, en cambio, compiló sin errores en el primer intento | **Corregida** — import `Server` añadido y script ejecutado |
| 4 | 04/10 | Asistente IA + **cálculo con script** | **Prompt 4** — Publicar la matriz ponderada y el gráfico de barras (Figura 4) | Totales de **4,00 / 4,25 / 3,25** para A, B y C, escritos directamente en el documento | Se recalcularon con `matriz-ponderada.py`, que compara el cálculo contra los valores publicados y **falla a propósito si no coinciden**. Falló: `AssertionError: ✗ Total de A recalculado = 4.10, pero matriz-decision.md publica 4.00`. Los tres totales publicados estaban mal. Se corrigieron a **4,10 / 4,15 / 3,05** en el `.py` y en el `.md`, y se propagó a los ADR y diagramas | **Corregida** — 3 totales erróneos detectados por aserción, no a ojo |
| 5 | 04/10 | Asistente IA + **verificación cruzada** | **Prompt 5** — Revisión de coherencia de los entregables contra la rúbrica | Un script de verificación que comprueba los requisitos de E1–E8 y deriva del propio documento los datos del caso (actores, módulos, totales) | La revisión encontró **defectos reales**: (a) los totales de la matriz estaban mal calculados (interaction 4); (b) el ADR-001 declaraba `**Estado:** Aceptado` pero la fecha seguía en el caso anterior; (c) la nota de E5 tenía 6 líneas y la guía pide 3–5; (d) el README enlazaba a ADRs que ya no existen (`002-base-de-datos`, `003-pwa-vs-app-nativa`). Todo se corrigió. Además se reescribió el verificador para que **no tenga hardcodeados** los puntajes, actores ni módulos del caso | **Corregida** — 4 defectos reales, verificados por re-render y por el script |

### Resumen de decisiones

| Decisión | Filas | Cantidad |
|----------|-------|----------|
| **Aceptada** | — | 0 |
| **Corregida** | 1, 3, 4, 5 | 4 |
| **Rechazada** | 2 | 1 |

**5 interacciones registradas, 5 con verificación y evidencia comprobable en el repositorio.**

---

## Detalle de las verificaciones con evidencia

### Fila 1 — el error que no es de código sino de razonamiento (E1/E2)

Es el error más grave de la bitácora porque afecta al **atributo crítico del caso**. La IA propuso que, ante
la pérdida de conexión con la válvula abierta, *"el servidor detecta la desconexión y envía la orden de cierre"*.

El problema es lógico, no de estilo: **si se perdió la conexión, no puede llegar ninguna orden desde el
servidor** (R-04). La protección no puede estar donde no hay red. Este es exactamente el tipo de error que la
guía describe en §1.7: una propuesta que suena razonable y es imposible.

**Cómo se corrigió:** la falla segura se reasignó al **controlador de campo**, que aplica un temporizador local
independiente de la red. Esto se documentó en [ADR-003](adr/003-apagado-seguro-en-controlador.md) y cambió el
criterio de mayor peso de la matriz a *Fiabilidad y protección*.

### Fila 2 — la crítica adversarial y lo que no se sostiene

Aplicando el Prompt 2 a la alternativa recomendada, la IA argumentó que *"un broker retiene las órdenes y por
eso el control es más confiable"*.

**Verificación:** el broker mejora la **entrega** del mensaje, no la **seguridad** de la válvula. La seguridad
depende de que exista un temporizador local en el dispositivo (ADR-003). Si el broker retiene un mensaje y el
controlador sigue sin red, el mensaje se entrega igual de tarde: la válvula ya la cerró su temporizador. Son dos
problemas distintos, y confundirlos es un error de razonamiento frecuente.

También propuso **microservicios con Kubernetes "por escalabilidad"**. Contra R-01 (1 mes), R-02 (2 developers)
y R-03 (un solo VPS), un orquestador es infraestructura que el equipo no puede sostener. La alternativa C
quedó en 3,05 y se descartó.

### Fila 3 — verificar la biblioteca ejecutando, no leyendo

La guía pide en E7 verificar *"¿existen esos íconos/clases en la librería?"*. La verificación real fue
**ejecutar el script**, y el fallo apareció de inmediato:

```
NameError: name 'Server' is not defined
```

La IA había escrito `Server("Controlador de campo…")` para representar el dispositivo en campo, pero **no
importó la clase**. Este es el mismo modo de fallo del caso anterior del equipo: un import incorrecto aborta el
script completo, y leer el código con atención no lo detecta con fiabilidad. Se añadió
`from diagrams.onprem.compute import Server` y el script corrió generando `img/despliegue.png`.

### Fila 4 — la aritmética hay que verificarla con una máquina

Al publicar la matriz, la IA escribió los totales **4,00 / 4,25 / 3,25**. El script
[`matriz-ponderada.py`](../diagramas/matriz-ponderada.py) recalcula los totales y compara contra lo publicado,
y falló:

```
AssertionError: ✗ Total de A recalculado = 4.10, pero matriz-decision.md publica 4.00
```

Los **tres** totales estaban mal. Se corrigieron a **4,10 / 4,15 / 3,05** y se propagó el cambio a los ADR, al
diagrama Mermaid y al PlantUML. Esta interacción es la razón de ser del script: **una matriz ponderada escrita a
mano es una afirmación, no una medida.** El error era pequeño (0,05–0,25 puntos) y completamente invisible al
leer, pero
habría costado puntos en la rúbrica de "Análisis de alternativas".

### Fila 5 — la revisión cruzada entre documentos

Al migrar de caso, los documentos quedan desalineados si no se revisan las referencias. Los defectos reales
encontrados fueron:

- **Totales erróneos** en la matriz (interaction 4), que además se propagaban a los ADR.
- **Fecha desactualizada** en los ADR, que seguían fechados en el caso anterior.
- **Nota de E5 con 6 líneas**, cuando la guía pide entre 3 y 5.
- **Enlaces rotos en el README** a `002-base-de-datos.md` y `003-pwa-vs-app-nativa.md`, que fueron reemplazados
  por `002-protocolo-de-comunicacion.md` y `003-apagado-seguro-en-controlador.md`.

La lección de fondo: **al cambiar de caso, el trabajo no es reescribir el contenido sino reconciliar las
referencias.** Por eso el verificador de rúbrica se reescribió para derivar del propio documento los datos del
caso (actores, módulos, totales) en lugar de tenerlos fijos: así sirve para el siguiente caso sin cambios.

---

## Lo que la IA aportó bien (también se registra)

Una bitácora que solo contiene errores sería tan poco creíble como una que no contiene ninguno. La IA **sí
acertó** en:

- Los **tres estilos** (monolito en capas, monolito modular, arquitectura orientada a eventos), que son las
  alternativas que la guía usa como modelo.
- La **estructura del prompt RCRTF** y el criterio de que un estilo arquitectónico debe justificarse contra los
  drivers, que es exactamente el criterio que este equipo usó después para detectar el error de la fila 1.
- La mecánica de **puertos y adaptadores**, que es la razón por la que el controlador de campo y el servicio de
  mensajería pueden cambiar de proveedor sin tocar la lógica de negocio.
- El andamiaje del entregable: la estructura de carpetas, la plantilla de ADR y la idea de versionar los drivers
  con IDs (RF-, R-, QA-) para poder citarlos desde cada decisión.

Lo que **no** hizo fue razonar sobre dónde vive la responsabilidad de cerrar la válvula: falló, y falló
justo en el atributo crítico del caso, que es donde más cara sale equivocarse.

---

## Anexo: prompts completos

> Recordatorio de la guía: nunca se incluyen datos personales ni información confidencial en un prompt.
> Los prompts de este anexo son las **consignas que el equipo dio al asistente** durante la sesión, tal como se
> usaron.

### Prompt 1 — estructura de E1 y E2 (interacción 1)

```
Actúa como arquitecto de software senior con experiencia en sistemas IoT para agricultura y PYMES.

CONTEXTO:
Plataforma "ChacraSmart Majes" de riego inteligente en parcelas de Majes (Arequipa).
Los sensores miden la humedad del suelo, el agricultor programa el riego y abre o cierra
válvulas de forma remota, y recibe alertas por falta de agua; el técnico registra parcelas
y dispositivos.

ATRIBUTO CRÍTICO:
Fiabilidad y protección (safety): si se pierde la conexión, ninguna válvula debe quedar
abierta más del tiempo programado (falla segura).

RESTRICCIONES (obligatorias, no negociables):
- Plazo: el MVP debe estar en producción en 1 mes.
- Equipo: 2 developers. Stack principal Python/Django.
- Presupuesto: un solo VPS. Todo servicio de pago debe justificarse.
- Las parcelas tienen conexión intermitente.

TAREA:
1. Redacta los drivers arquitectónicos del caso (requisitos funcionales, atributos de calidad
   priorizados, restricciones) con identificadores estables y referenciables.
2. Arma una matriz de decisión ponderada con 3 estilos y 5 criterios. Cada peso debe
   justificarse citando un driver concreto.

IMPORTANTE:
No inventes APIs ni capacidades de servicios. Cada criterio de la matriz debe poder rastrearse
hasta una línea del enunciado; si un criterio no tiene driver detrás, no lo ponderes.
Explica claramente dónde debe vivir la lógica de seguridad de las válvulas.
```

### Prompt 2 — crítica adversarial (interacción 2)

```
Ahora actúa como "abogado del diablo". Critica duramente la alternativa que recomendaste:
¿qué supuestos no se cumplen con nuestras restricciones?, ¿qué podría fallar en producción?,
¿qué costo oculto tiene? Enumera los 5 riesgos más graves y, para cada uno, una táctica
arquitectónica de mitigación.
```

### Prompt 3 — diagramas (interacción 3)

```
Genera el código Mermaid (flowchart) de la arquitectura ELEGIDA de ChacraSmart Majes.

CONTEXTO:
La alternativa elegida es un MONOLITO MODULAR en Django, un solo despliegue.
Módulos de dominio: Lecturas de humedad (RF-01, RF-02), Programación de riego (RF-03),
Control de válvulas (RF-04), Alertas (RF-05), Parcelas y dispositivos (RF-06, RF-07).
Actores: Agricultor, Técnico.
Almacenamiento: PostgreSQL.
Servicios externos: controlador de campo (sensor + válvula con temporizador local) y
servicio de mensajería para las alertas.

REQUISITOS DEL DIAGRAMA:
- Los dos actores, los cinco módulos, la capa de presentación, la capa de infraestructura,
  el almacenamiento y al menos un servicio externo.
- Usa `subgraph` para agrupar la aplicación y la infraestructura.
- Etiqueta cada módulo con los RF que cubre.

Genera también el script de Python Diagrams para la vista de despliegue (E6), con usuarios,
dispositivo en campo, proxy, aplicación, base de datos, servicios externos y monitoreo,
usando `Cluster` y `Edge(label=...)`.
```

### Prompt 4 — matriz ponderada y verificación (interacción 4)

```
Genera el script de Python que recalcule los totales ponderados de la matriz y compare
el resultado con los totales publicados en el documento. El script debe FALLAR si los pesos
no suman 100 % o si los totales no coinciden con lo publicado.
```

### Prompt 5 — revisión final (interacción 5)

```
Revisa los entregables E1 a E8 de este repositorio contra la rúbrica del Lab 04 y reporta
defectos concretos, no rehagas el trabajo.

Checklist a verificar:
- Todos los IDs citados entre documentos existen y dicen lo mismo (RF, R, QA).
- Los totales de la matriz coinciden con los que calcula el script.
- Cada ADR tiene fecha, estado, decisores y citas IDs.
- La nota de E5 tiene entre 3 y 5 líneas. La reflexión de E8 tiene entre 5 y 8 líneas.
- Los enlaces internos del README no están rotos.

Luego escribe un script de verificación reutilizable que compruebe estos puntos, y déjalo en
tools/. El script debe derivar del documento los datos del caso (actores, módulos, totales),
no tenerlos fijos, para que sirva para el siguiente caso.
```