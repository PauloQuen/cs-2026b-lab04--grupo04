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
| 1 | 10/10 | Asistente IA (CLI) | **Prompt IA 1** — Diagrama de clases de los módulos Riego y Control de válvulas, adaptando el prompt de la guía al caso 9: contexto del ADR-001, historia y criterios de aceptación | 6+ clases de dominio (`Agricultor`, `Parcela`, `Valvula`, `ProgramacionRiego`, `LecturaHumedad`), 2 enumeraciones, 3 puertos (`ControladorValvula`, `Notificador`, `RepositorioRiego`) y 2 adaptadores | **Coherencia con el ADR-001:** la IA tiende a poner la lógica de infraestructura en la entidad; se corrigió para que la entidad **no dependa del adaptador**: todo pasa por el puerto `ControladorValvula`, mediado por `ServicioRiego`. **QA-01:** la falla segura existe como operación del dominio (`fallarCierreSeguro()`) y `aperturaMaximaMin` limita el temporizador local (ADR-003). **C3:** multiplicidad en ambos extremos de todas las asociaciones (parcela–válvula como composición `1..*`). **C5:** nombres del dominio idénticos a drivers.md/ADR-001. **Nombre del módulo E6:** decidido por el equipo (`src/valvulas_riego`, el guion no es válido en Python) | **Corregida** — la entidad no habla con el adaptador; `ServicioRiego` media por puertos. Resto verificado y aceptado |
| 2 | 10/10 | *(pendiente E2)* | | | | |
| 3 | 10/10 | *(pendiente E3)* | | | | |
| 4 | 10/10 | *(pendiente E4)* | | | | |
| 5 | 10/10 | *(pendiente E5)* | | | | |
| 6 | 10/10 | *(pendiente E6)* | | | | |
| 7 | 10/10 | *(pendiente E7)* | | | | |

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

---

## Anexo: prompts completos

### Prompt IA 1 — Diagrama de clases (E1)

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