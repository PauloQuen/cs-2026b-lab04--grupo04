<!--
  ChacraSmart Majes — Lab 05 (UML como código) · Caso 9 · Grupo 04
  E7: bitácora de uso de IA (se escribe junto con cada entregable E1–E7).
-->

# Bitácora de uso de IA — ChacraSmart Majes (Lab 05)

> Lab 05 · E7 · Caso 9 · Grupo 04
> **Herramienta:** asistente de IA de línea de comandos integrado en el flujo de trabajo del repositorio.
> **Sesión de trabajo:** 10/10/2026.
>
> ⚠️ **Criterio de honestidad (mismo que en el Lab 04).** Solo se registran interacciones que **ocurrieron de
> verdad** en esta sesión, y cada fila apunta a un **artefacto comprobable** del repositorio. Donde la IA acertó,
> se dice que acertó; donde el equipo corrigió, se muestra qué se corrigió y por qué.
>
> **Regla de oro de la práctica:** *la IA propone, el equipo decide y verifica*. Cada propuesta se revisa con las
> reglas C1–C5 (Tabla 2 de la guía) antes de aceptarla.
>
> **Nunca se incluyó ningún dato personal ni información confidencial en ningún prompt.** Solo el enunciado
> público del caso y las decisiones ya documentadas en este repositorio.

---

## Tabla de interacciones

| # | Fecha | Herramienta | Prompt (resumen) | Qué propuso la IA | Qué verificamos o corregimos | Decisión |
|---|-------|-------------|------------------|-------------------|------------------------------|----------|
| 1 | 10/10 | Asistente IA (CLI) | **Prompt IA · E1** — Diagrama de clases de los módulos Riego y Control de válvulas, adaptando el prompt de la guía al caso 9: contexto del ADR-001, historia y criterios de aceptación | 6+ clases de dominio (`Agricultor`, `Parcela`, `Valvula`, `ProgramacionRiego`, `LecturaHumedad`), 2 enumeraciones, 3 puertos (`ControladorValvula`, `Notificador`, `RepositorioRiego`) y 2 adaptadores | **Coherencia con el ADR-001:** la IA tiende a poner la lógica de infraestructura en la entidad; se corrigió para que la entidad **no dependa del adaptador**: todo pasa por el puerto `ControladorValvula`, mediado por `ServicioRiego`. **QA-01:** la falla segura existe como operación del dominio (`fallarCierreSeguro()`) y `aperturaMaximaMin` limita el temporizador local (ADR-003). **C3:** multiplicidad en ambos extremos de todas las asociaciones (parcela–válvula como composición `1..*`). **C5:** nombres del dominio idénticos a drivers.md/ADR-001. **Nombre del módulo E6:** decidido por el equipo (`src/valvulas_riego`, el guion no es válido en Python) | **Corregida** — la entidad no habla con el adaptador; `ServicioRiego` media por puertos. Resto verificado y aceptado |
| 2 | 10/10 | Asistente IA (CLI) | **Prompt IA · E2** — Diagrama de secuencia del flujo "programar un riego y abrir la válvula remota", con `alt`, `loop`/`opt` y un mensaje asíncrono | 9 líneas de vida (actor, PWA, controlador, servicio, repositorio, entidades y el puerto hacia el controlador de campo). `alt` para éxito vs válvula fuera de línea, `loop` de reintentos de apertura, `opt` de cierre por temporizador local (ADR-003) y 2 mensajes asíncronos a `Notificador` | **Regla C1:** el mensaje `S -> R : buscarValvulasPorParcela(parcelaId)` no existía como operación de `RepositorioRiego`; se **agregó al diagrama de clases** (procedimiento del E2, paso 5). Se verificaron uno a uno los demás mensajes contra las operaciones de `clases.puml`: `iniciar()`, `finalizar()`, `abrir()`, `confirmarApertura()`, `cerrar()`, `notificarAlerta()` — todos existen | **Corregida** — `buscarValvulasPorParcela()` añadida a `RepositorioRiego`. Resto verificado y aceptado |
| 3 | 10/10 | Asistente IA (CLI) | **Prompt IA · E3** — Máquina de estados de `Valvula` en Mermaid (`stateDiagram-v2`) con los 5 estados de la Tabla 7 y transiciones nombradas con operaciones (C2) | `[*] → CERRADA → ABRIENDO → ABIERTA → CERRANDO → …`, más la transición de **Falla (cierre seguro)** por pérdida de conexión o fallo del actuador; 6 guardas entre corchetes y una nota en `FALLA` | **Regla C2:** la transición `CERRANDO → CERRADA` no tenía operación que la provocara; se agregó **`confirmarCierre()`** a `Valvula` en `clases.puml` (mismo caso que `aceptarPreparacion()` del ejemplo docente). Verificado: los 5 estados coinciden **exactamente** con la enumeración `EstadoValvula` (C5) y ningún estado queda sin salida salvo `FALLA` (final) | **Corregida** — `confirmarCierre()` añadida a `Valvula`. Resto aceptado |
| 4 | 10/10 | Asistente IA (CLI) + **revisión con usuario** | **Prompt IA · E4** — Diagrama de actividades "riego automático según la humedad del suelo": particiones, decisiones y fork/join | 4 particiones (Sensor, Sistema, Controlador de campo, Agricultor), 2 decisiones (humedad bajo umbral; válvula en línea) y un `fork` que notifica al agricultor en paralelo con el cierre por temporizador local | **Cambio surgido de la revisión con usuario (E4, paso 3):** un compañero actuando como agricultor señaló que de nada sirve avisar "riego finalizado" si el riego **nunca empezó**: se agregó la rama `else` que notifica la alerta de *válvula fuera de línea* (CA-03). También se verificó que el cierre por temporizador local queda **dentro del flujo** (QA-01/ADR-003) | **Corregida** — rama de alerta "fuera de línea" añadida en la revisión con usuario |
| 5 | 10/10 | Asistente IA (CLI) | **Prompt IA · E5** — Diagrama de paquetes: un paquete por módulo del ADR-001, dependencias etiquetadas y la regla de dependencias en una nota | 6 paquetes (5 módulos del ADR-001 + `compartido`), dependencias etiquetadas con la clase/puerto usado y nota con la regla *sin ciclos* | **Regla C4 (sin ciclos):** se trazó el grafo dirigido `programacion → control_valvulas → dispositivos` y `programacion → lecturas → alertas → dispositivos`: **acíclico**. La flecha `programacion ..> lecturas` no estaba en la vista gruesa del Lab 04 y se justifica por el diseño detallado (`ServicioRiego` usa `LecturaHumedad`) — se documentó **sin crear el ADR-004**, porque la guía solo pide ADR nuevo *si aparece un ciclo* | **Aceptada** — grafo verificado acíclico; no se requirió ADR-004 |
| 6 | 10/10 | Asistente IA (CLI) + **pyreverse ejecutado** | **Prompt IA · E6** — Ingeniería directa: esqueleto Python 3.10 (dataclasses, type hints, ABC para puertos) de `clases.puml`, respetando nombres y multiplicidades | `src/valvulas_riego/dominio.py` con entidades, 3 puertos (ABC), 2 adaptadores y `ServicioRiego` con lógica mínima (guardas de estado y de `apertura_maxima_min`) | **Se ejecutó el código** (no se leyó): el ciclo de vida de `Valvula` CERRADA→ABRIENDO→ABIERTA→CERRANDO→CERRADA y la falla segura pasan aserciones reales; la duración > máximo se rechaza (QA-01). **Ingeniería inversa con `pyreverse` ejecutada**: reveló 7 diferencias documentadas en `round-trip.md` (composición no inferida, puertos como `{abstract}`, `snake_case`, paquetes planos). Lo más notable: los métodos de adaptadores figuran `{abstract}` por levantar `NotImplementedError` | **Corregida** — se validó el código ejecutándolo; las 7 diferencias del round-trip se documentan con causa y acción, sin tocar el diseño |
| 7 | 10/10 | Asistente IA (CLI) — **auditor de consistencia** | **Prompt IA · E7** — Revisar los 5 diagramas con las reglas C1–C5 (Prompt 3 de la guía): reportar hallazgos en tabla (regla, elemento, problema, corrección), sin reescribir los diagramas | 5 hallazgos: C1 sin observaciones; C2: `FALLA --> [*]` "sin operación"; C3: multiplicidad `Parcela–Valvula 1..*` inconsistente con RF-06; C4: "ciclo vía compartido"; C5: solo salvedad `snake_case` | Se verificó cada hallazgo contra los archivos. **C3 fue real**: una parcela puede existir sin válvula (RF-06), se corrigió a `0..*`. **C2 y C4 fueron FALSOS POSITIVOS**: el `[*]` final no requiere operación (mismo patrón `ENTREGADO-->[*]` del docente) y el grafo de paquetes es un DAG (la IA leyó la nota como dependencia) | **1 corregida (C3) + 2 rechazadas (falsos positivos C2, C4)**; C1 y C5 aceptados |

---

## Detalle de las verificaciones con evidencia

### Fila 1 — la entidad no depende de infraestructura (E1)

El prompt de la guía pide modelar el **puerto hacia un servicio externo**. En este caso el servicio externo es el
**controlador de campo** (sensor + válvula, ADR-002/ADR-003). La primera pasada de la IA conectaba a
`ProgramacionRiego` directamente con el adaptador del controlador.

**Verificación contra el ADR-001:** en el monolito modular los módulos se comunican *solo mediante interfaces
públicas*, y las integraciones externas se implementan como adaptadores detrás de puertos. Si la entidad
conociera al adaptador, arrastraría infraestructura al dominio. Se corrigió: el único que usa puertos es
`ServicioRiego` (servicio de aplicación), y las entidades `Valvula`/`ProgramacionRiego` solo conocen su propio
estado y operaciones.

**Evidencia:** [`clases.puml`](clases.puml) — dependencias `ServicioRiego ..> ControladorValvula` y
`ControladorValvula <|.. ControladorCampoAdapter`; ninguna entidad apunta al adaptador.

**QA-01 (falla segura).** La operación `fallarCierreSeguro()` y el atributo `aperturaMaximaMin` de `Valvula`
existen para que el diagrama sea **verificable** contra el escenario QA-01 (0 válvulas abiertas más de 5 s sobre
lo programado en 100 cortes de red simulados). Sin esas operaciones, la máquina de estados de E3 no tendría de
dónde tomar la transición de Falla (regla C2).

### Fila 2 — la regla C1 se aplica, no se declama (E2)

```mermaid
(ver docs/design/secuencia-programar-riego.png)
```

El diagrama de secuencia usa `alt` (éxito vs válvula fuera de línea, CA-03), `loop` (reintentos de apertura) y
`opt` (cierre por temporizador local al terminar la duración, ADR-003), con 9 líneas de vida y 2 mensajes
asíncronos a `Notificador`.

**Verificación C1:** se listaron los mensajes dirigidos a objetos que son clases del diagrama y se contrastaron
con `clases.puml`. Uno falló: `buscarValvulasPorParcela(parcelaId)` no estaba en `RepositorioRiego`. Se agregó
como operación del puerto (E2, paso 5 de la guía). Los demás (`iniciar`, `finalizar`, `abrir`,
`confirmarApertura`, `cerrar`, `notificarAlerta`) ya existían.

**Evidencia:** [`secuencia-programar-riego.puml`](secuencia-programar-riego.puml) y la línea `buscarValvulasPorParcela`
en [`clases.puml`](clases.puml).

### Fila 3 — la transición sin operación se detecta al escribir la guarda (E3)

La máquina de estados de la válvula salió con los 5 estados del foco de la Tabla 7, pero al nombrar cada
transición con la operación que la provoca (regla C2) apareció el mismo hueco que en el ejemplo docente: la
transición `CERRANDO → CERRADA` (válvula termina de cerrarse) no tenía operación. Se agregó
`confirmarCierre()` a `Valvula` en `clases.puml`.

Además se verificó C5: los identificadores de estado en `estados-valvula.mmd` son idénticos a la enumeración
`EstadoValvula` de `clases.puml` (`CERRADA, ABRIENDO, ABIERTA, CERRANDO, FALLA`), y el único estado sin
transición de salida es `FALLA`, que es final (requiere técnico, fuera del MVP).

**Evidencia:** [`estados-valvula.mmd`](estados-valvula.mmd) y la operación `confirmarCierre()` en
[`clases.puml`](clases.puml).

### Fila 4 — el usuario del proceso ve lo que el diagrama no decía (E4)

El E4, paso 3 de la guía pide validar el flujo con alguien que conozca el proceso real. La revisión se hizo con
un compañero que actuó como agricultor de Majes. Su lectura del diagrama: *"si el riego no arranca porque la
válvula está fuera de línea, ¿a mí quién me avisa? El diagrama solo me avisa al final"*. Era cierto: la primera
versión solo notificaba el fin del riego. Se agregó la rama `else` que dispara la alerta de dispositivo fuera de
línea (criterio de aceptación CA-03) y se verificó que el cierre por temporizador local (QA-01) quedara dentro
del flujo, en paralelo con la notificación.

**Evidencia:** el comentario de revisión al inicio de [`actividades-riego-automatico.puml`](actividades-riego-automatico.puml)
y la rama `else (no) → Recibe la alerta de dispositivo fuera de línea`.

### Fila 6 — el round-trip se ejecuta, no se imagina (E6)

La ingeniería directa generó `src/valvulas_riego/dominio.py`. La verificación no fue leerlo: fue **ejecutarlo**
con aserciones (ciclo de vida completo de la válvula según E3, guarda de `apertura_maxima_min`, programación de
riego). La ingeniería inversa tampoco: se corrió `pyreverse` de verdad y las 7 diferencias de
[`round-trip.md`](round-trip.md) son las que salieron del comando, no las que esperábamos.

El hallazgo más interesante salió solo: `pyreverse` marca `{abstract}` a los métodos de los adaptadores porque su
cuerpo solo `raise NotImplementedError` — la misma limitación que el ejemplo docente registra para
`YapeAdapter`. Y `ServicioRiego.evaluar_riego_automatico()` figura `{abstract}` **sin ser** `@abstractmethod`,
por el mismo motivo: es un stub intencional (E4).

**Evidencia:** [`round-trip.md`](round-trip.md), [`classes-valvulas-riego-pyreverse.puml`](classes-valvulas-riego-pyreverse.puml)
y el PNG [`img/classes_valvulas_riego.png`](img/classes_valvulas_riego.png).

### Fila 7 — el auditor también se equivoca, y eso se documenta (E7)

La revisión de consistencia (Prompt IA auditor) devolvió una tabla de hallazgos C1–C5. La verificación del
equipo, una por una, dejó el resultado que la guía espera: **al menos un falso positivo identificado y
explicado**. En este caso fueron dos:

- **C2 (`FALLA --> [*]` "sin operación")**: falso positivo. El `[*]` es un estado final; el propio ejemplo
  docente dibuja `ENTREGADO --> [*]` y `CANCELADO --> [*]` sin operación. La C2 se cumple en todas las
  transiciones *entre estados*.
- **C4 ("ciclo vía compartido")**: falso positivo. Se trazó el grafo dirigido arista por arista: es un DAG. La
  IA leyó la nota del `paquetes.puml` (*"control_valvulas NO depende de programacion"*) como si fuera una
  dependencia más.

Y uno **real**: C3 (`Parcela–Valvula 1..*`). RF-06 permite que el técnico registre una parcela antes de
instalar sus válvulas, así que la multiplicidad se corrigió a `0..*` — exactamente el tipo de hallazgo que hace
valiosa la revisión.

**Evidencia:** [`consistencia.md`](consistencia.md) (tabla completa con veredictos) y la multiplicidad `0..*` en
[`clases.puml`](clases.puml).

---

## Anexo: prompts completos

### Prompt IA · E1 — Diagrama de clases

```
Actúa como diseñador de software orientado a objetos. Contexto: módulos de
PROGRAMACIÓN DE RIEGO y CONTROL DE VÁLVULAS de un monolito modular en Django
(ADR-001 del Lab 04: puertos y adaptadores para integraciones externas; el
controlador de campo es un servicio externo; QA-01 exige falla segura con
temporizador local según el ADR-003).

Historia y criterios: [pegar historia.md].

Tarea: genera un diagrama de clases en PlantUML con atributos tipados con
visibilidad, operaciones, multiplicidades en TODAS las asociaciones, una
enumeración EstadoValvula coherente con la máquina de estados (Cerrada,
Abriendo, Abierta, Cerrando, Falla) y un puerto (interfaz) hacia el
controlador de campo.

Formato: solo el código PlantUML. No agregues clases que no se deriven de la
historia; si asumes algo, indícalo en un comentario. Usa nombres del dominio
del caso (válvula, parcela, riego), no genéricos.
```

### Prompt IA · E2 — Diagrama de secuencia

```
Dibuja en PlantUML el diagrama de secuencia del escenario principal de esta
historia: "programar un riego y abrir la válvula de forma remota", para un
monolito modular (ADR-001). Líneas de vida: actor, PWA, controlador,
ServicioRiego, RepositorioRiego, entidades (ProgramacionRiego, Valvula) y el
puerto ControladorValvula (controlador de campo).

Requisitos:
- 5 o más líneas de vida.
- Un fragmento alt para el caso de éxito (válvula en línea) y el de error
  (válvula fuera de línea, notificación asíncrona).
- Un fragmento loop u opt (sugerencia: reintentos de acuse de apertura).
- Al menos un mensaje asíncrono (->>) y los mensajes de retorno.
- Cada mensaje dirigido a un objeto debe ser una operación de su clase en
  clases.puml (regla C1); si inventas uno, márcalo para revisarlo.

Solo el código PlantUML.
```

### Prompt IA · E3 — Máquina de estados

```
Escribe en Mermaid (stateDiagram-v2) la máquina de estados de la entidad
Valvula del sistema ChacraSmart Majes. Estados exactos (Tabla 7 de la guía):
CERRADA, ABRIENDO, ABIERTA, CERRANDO y FALLA (cierre seguro).

Requisitos:
- Estado inicial [*] y al menos un estado final.
- 2 o más guardas entre corchetes.
- Cada transición nombrada con la operación de Valvula que la provoca (regla
  C2): abrir(duracionMin), confirmarApertura(), cerrar(), confirmarCierre() y
  fallarCierreSeguro(). Si una transición no tiene operación, dimelo en un
  comentario en vez de inventarla.
- FALLA representa el cierre seguro (QA-01, ADR-003): la válvula termina
  cerrada por el temporizador local del controlador de campo.

Solo el código Mermaid.
```

### Prompt IA · E4 — Diagrama de actividades

```
Modela en PlantUML el proceso "riego automático según la humedad del suelo" de
ChacraSmart Majes (monolito modular, ADR-001). Requisitos:
- 3 o más particiones (|Partición|): Sensor, Sistema, Controlador de campo y
  Agricultor.
- 2 o más decisiones (if/else): ¿humedad bajo el umbral? ¿válvula en línea?
- Una ejecución paralela con fork / end fork: notificar al agricultor en
  paralelo con el cierre por temporizador local del controlador (QA-01,
  ADR-003).
- El flujo debe cubrir: alerta cuando el riego NO puede iniciarse (CA-03) y
  aviso cuando termina.

Solo el código PlantUML.
```

### Prompt IA · E6 — Ingeniería directa (round-trip)

```
Genera el esqueleto en Python 3.10 (dataclasses y type hints) del siguiente
diagrama de clases. Respeta exactamente los nombres de clases, atributos y
operaciones (en snake_case), las enumeraciones, la interfaz como clase
abstracta (ABC) y las multiplicidades. Implementa solo la lógica mínima de
las operaciones de Valvula y ProgramacionRiego; los adaptadores deben lanzar
NotImplementedError. [pegar clases.puml]
```

### Prompt IA · E7 — Auditor de consistencia

```
Actúa como revisor de diseño. Te paso cinco diagramas UML en PlantUML/Mermaid:
[pegar los cinco archivos de docs/design/]. Verifica estas reglas y responde en
una tabla (regla, elemento, problema, corrección sugerida):
C1 cada mensaje de secuencia es una operación de la clase receptora;
C2 cada transición de estados corresponde a una operación de la clase;
C3 multiplicidades coherentes con los criterios de aceptación;
C4 paquetes sin ciclos;
C5 nombres consistentes.
No reescribas los diagramas; solo reporta hallazgos y cita la línea.
```