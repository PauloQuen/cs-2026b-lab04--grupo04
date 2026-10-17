# Comparación — secuencia UML vs. vista dinámica C4 (E4) · y DSL vs. dibujar a mano (E6)

> Lab 06 · ChacraSmart Majes · Grupo 04

## 1. Secuencia UML (Lab 05, E2) vs. vista dinámica C4 (Lab 06, E4)

Ambas vistas cubren **el mismo flujo crítico**: *programar un riego y abrir la válvula de forma remota*
(`docs/design/secuencia-programar-riego.puml` ↔ vista `ProgramarRiego` del `workspace.dsl`).
La secuencia UML muestra el **cómo** se implementa: 9 líneas de vida con clases concretas
(`ServicioRiego`, `RepositorioRiego`, `ControladorCampoAdapter`), retornos, `alt`/`loop`/`opt` y
mensajes asíncronos. La vista dinámica C4 muestra el **quién y en qué orden**: 9 pasos numerados entre
personas, contenedores, componentes y sistemas externos, sin ramas ni bucles, y **cada paso es una
relación que ya existe** en el modelo. Se usa la secuencia para diseñar e implementar el módulo
(toca clases y operaciones) y la dinámica para comunicar el recorrido del caso de uso por la
arquitectura (solo toca relaciones): la primera se rompe si cambia una clase, la segunda solo si
cambia una relación.

| Dimensión            | Secuencia UML (`secuencia-programar-riego.puml`) | Vista dinámica C4 (`ProgramarRiego`) |
|----------------------|--------------------------------------------------|--------------------------------------|
| Pregunta que responde | *¿cómo lo implementa?*                           | *¿quién participa y en qué orden?*   |
| Granularidad         | Métodos y mensajes entre objetos (`programarRiego(...)`, `abrir(...)`) | Relaciones entre elementos C4 (`pwa → programación → control de válvulas → controlador`) |
| Control de flujo     | `alt`, `loop`, `opt`, mensajes asíncronos        | Ninguno: una secuencia lineal de pasos numerados |
| Audiencia            | Developers del módulo                            | Equipo técnico que revisa la arquitectura |
| Costo de cambio      | Se rompe si cambia una clase o una operación     | Solo si cambia una relación del modelo |
| Correspondencia      | 9 mensajes clave                                 | 9 pasos; cada uno corresponde a un par origen→destino ya definido en `workspace.dsl` |

**Correspondencia paso a paso (flujo crítico):**

| # | Paso en `ProgramarRiego` (C4)                 | Mensaje equivalente en la secuencia UML                     |
|---|-----------------------------------------------|-------------------------------------------------------------|
| 1 | Agricultor → PWA                              | `Agricultor -> UI : Programa riego (parcela, hora, duración)`|
| 2 | PWA → Módulo Programación (`POST /riegos`)    | `UI -> C : POST /riegos` → `C -> S : programarRiego(...)`    |
| 3 | Módulo Programación → Base de datos           | `S -> R : guardarProgramacion(p)`                            |
| 4 | Programación → Control de válvulas            | `S -> V : abrir(duracionMin)` vía `ControladorValvula`       |
| 5 | Control de válvulas → Controlador de campo    | `S -> G : abrir(valvulaId, duracionMin)` (adaptador)         |
| 6 | Controlador de campo → Control de válvulas    | `G --> S : acuse de apertura` / `evento de cierre (ADR-003)` |
| 7 | Programación → Alertas                        | `S ->> N : notificarAlerta(...)`                             |
| 8 | Alertas → Cola y caché                        | (encolado de la tarea de envío)                              |
| 9 | Worker → Servicio de mensajería               | (el worker ejecuta el envío de la alerta)                    |

> Los pasos 3, 5, 6 y 7 existen como mensaje en la secuencia y como **relación ya definida** en el
> modelo C4: no se inventó ninguna relación solo para la vista dinámica.

---

## 2. Structurizr DSL vs. dibujar cada vista a mano (E6)

### 2.1 Experimento: cambiar el nombre de un contenedor

Se renombró el contenedor **`Cola y caché` → `Cola de tareas Redis`** en una copia del `workspace.dsl`
y se volvieron a exportar las 5 vistas, comparando contra la versión original:

```bash
# copia de prueba, sin tocar el entregable
sed 's/Cola y caché/Cola de tareas Redis/g' workspace.dsl > /tmp/prueba.dsl
./structurizr.sh validate -w /tmp/prueba.dsl
./structurizr.sh export -w /tmp/prueba.dsl -f mermaid -o /tmp/export-prueba
diff -u export/*.mmd /tmp/export-prueba/*.mmd | grep -c '^+'   # líneas afectadas
```

**Resultado (líneas cambiadas en cada `.mmd` exportado, medidas con `diff`):**

| Vista | Líneas cambiadas |
|---|---|
| Contexto | **0** (la cola no pertenece al nivel 1) |
| Contenedores | 1 |
| Componentes | 1 |
| ProgramarRiego | 2 |
| Despliegue | 1 |

Un solo archivo fuente cambió (`workspace.dsl`) y **4 diagramas se actualizaron solos**, incluido el de
despliegue, donde el nodo de Docker arrastra el nuevo nombre. El nivel 1 quedó intacto, que es justo lo
que corresponde: el renombrado es un cambio de nivel 2 y no debe manchar el contexto.

Si cada vista estuviera dibujada a mano (C4-PlantUML o Mermaid sueltos), el mismo cambio exigiría
editar `Contenedores`, `Componentes`, `ProgramarRiego` y `Despliegue` **uno por uno**, con la probabilidad
real de olvidarse de uno — típicamente el de despliegue, el que menos se mira — y dejar el repo con un
diagrama mintiendo sobre el nombre del contenedor.

### 2.2 Tiempo y errores observados en la sesión

Tiempos **medidos con `time`** en esta sesión (máquina local, sin ediciones al DSL):

| Acción | Tiempo medido | Errores |
|--------|----------------|---------|
| `validate` del DSL completo | **1,6 s** | 0 errores del modelo en todo el lab (los fallos que hubo fueron de *scripts* propios de automatización, no del DSL) |
| `export` a C4-PlantUML | **1,0 s** | 0 |
| `export` a Mermaid | **1,0 s** | 0 |
| Render de los 5 PNG con `plantuml.jar` | **8 s** | 0 (la primera vez descarga la librería C4: requiere red por `!include <C4/...>`) |
| Escritura a mano de `contexto-manual.puml` (1 vista) | minutos de trabajo humano — el único paso no automatizado del flujo | Requiere acordarse de `System_Ext`, `Rel(...)`, `LAYOUT_LEFT_RIGHT()` y `SHOW_LEGEND()`; un nombre mal escrito no falla, solo **dibuja algo distinto** al modelo |

La diferencia central: con DSL, el error lo detecta `validate` **antes** de publicar; escrito a mano,
el error es silencioso y recién lo ves (o no) en la imagen. Ese es exactamente el riesgo que motivó
"arquitectura como código".

### 2.3 Equivalencia de `contexto-manual.puml`

`contexto-manual.puml` es la única vista escrita a mano (lo pide E6) y se generó **comparándola contra
`export/structurizr-Contexto.puml`**: mismos 5 elementos (2 personas, el sistema, 2 externos con
`System_Ext`), mismas 5 relaciones con el mismo texto y protocolos. Sirve como control: si un día el
automático y el manual dejan de coincidir, es que el modelo cambió y alguien no regeneró las imágenes.
