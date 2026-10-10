<!--
  ChacraSmart Majes — Lab 05 (UML como código) · Caso 9 · Grupo 04
  E1: historia de usuario crítica y criterios de aceptación.
  Habilita: clases.puml (E1), secuencia-*.puml (E2), estados-*.mmd (E3).
-->

# Historia de usuario crítica — ChacraSmart Majes

> Lab 05 · Construcción de Software · EPIS-UNSA · 2026-B · Caso 9.
> Esta es la historia de la columna **E2** de la Tabla 7 de la guía: *"Programar un riego y abrir la válvula de
> forma remota"*. Es la que gobierna el diseño detallado del sistema.

El diseño del interior de los módulos se hace sobre **una sola historia crítica**, no sobre todo el sistema
(Fowler, 2003: UML como boceto/plano de las partes críticas). Esta historia toca los módulos **Programación de
riego** y **Control de válvulas** definidos en el [ADR-001](../architecture/adr/001-estilo-arquitectonico.md), y
por eso es la que más riesgo concentra: si la válvula no se cierra bien, falla el atributo crítico **QA-01**.

---

## HU-04 — Programar un riego y abrir la válvula de forma remota

**Como** agricultor de una parcela en Majes,
**quiero** programar un riego indicando hora y duración y que el sistema abra la válvula de forma remota,
**para** regar mi cultivo en el momento adecuado sin tener que estar presente en la parcela.

**Trazabilidad:** RF-03 (programar riego), RF-04 (abrir/cerrar válvula remota), RF-05 (alerta por falta de agua)
· QA-01 (fiabilidad y protección) · [ADR-002](../architecture/adr/002-protocolo-de-comunicacion.md) (protocolo
HTTP con buffer local) y [ADR-003](../architecture/adr/003-apagado-seguro-en-controlador.md) (apagado seguro en
el controlador de campo).

### Criterios de aceptación

**CA-01 — Programación y apertura en el caso normal**

- **Dado** un agricultor con una **válvula en línea** en su parcela,
- **cuando** programa un riego con hora de inicio y duración,
- **entonces** el sistema **abre la válvula** a la hora programada y la **cierra automáticamente** al cumplirse
  la duración indicada.

**CA-02 — Cierre seguro ante pérdida de conexión** *(materializa QA-01)*

- **Dado** un riego en curso con la **válvula abierta**,
- **cuando** se pierde la conexión entre el servidor y el controlador de campo,
- **entonces** el controlador **cierra la válvula por su temporizador local** al cumplirse el tiempo programado y
  registra el evento, sin dejarla abierta más de **5 s sobre el tiempo programado**.

**CA-03 — Válvula fuera de línea**

- **Dado** un agricultor cuya **válvula está fuera de línea**,
- **cuando** intenta programar un riego o abrir la válvula de forma remota,
- **entonces** el sistema **no confirma la apertura** y le **notifica** que el dispositivo no responde.

---

## Alcance del modelo

De estos criterios se derivan directamente:

- **Clases del dominio** (E1): `Agricultor`, `Parcela`, `Valvula`, `ProgramacionRiego`, `LecturaHumedad` y el
  servicio de aplicación `ServicioRiego`.
- **Puertos** (interfaces) hacia servicios externos: `ControladorValvula` (controlador de campo, servicio
  externo) y `Notificador` (servicio de mensajería); más `RepositorioRiego` para la persistencia.
- **Enumeraciones**: `EstadoValvula` y `EstadoProgramacion`.
- **Entidad para la máquina de estados** (E3): `Valvula`, con `Cerrada → Abriendo → Abierta → Cerrando`, y la
  transición de **Falla (cierre seguro)**.
- **Flujo para la secuencia** (E2): programar un riego y abrir la válvula de forma remota.
