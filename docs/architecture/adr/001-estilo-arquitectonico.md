# ADR-001: Adoptar un monolito modular para el MVP de ChacraSmart Majes

- **Estado:** Aceptado
- **Fecha:** 2026-10-04
- **Decisores:** Quenta Ahumada Paulo Estefano, Kevin Joel Callo Ccagiavilca

---

## Contexto

ChacraSmart Majes es una plataforma de riego inteligente para parcelas de Majes. El sensor envía lecturas de humedad (RF-01), el agricultor consulta humedad actual/histórico (RF-02), programa riegos (RF-03), abre/cierra válvulas remotamente (RF-04), recibe alertas por falta de agua (RF-05), y el técnico registra parcelas/sensores/válvulas (RF-06) y consulta su estado (RF-07).

El atributo de calidad **crítico es la fiabilidad y protección (safety)**: si se pierde la conexión, ninguna válvula debe quedar abierta más del tiempo programado (QA-01). Esto concentra el **30 %** del peso en la matriz de decisión ([`matriz-decision.md`](../matriz-decision.md)).

Las restricciones que condicionan la decisión son:

- **R-01 — Plazo:** el MVP debe estar en producción en **1 mes**.
- **R-02 — Equipo:** **2 developers** (Quenta Ahumada Paulo Estefano y Kevin Joel Callo Ccagiavilca), con
  Python/Django como stack principal.
- **R-03 — Presupuesto:** **un solo VPS**; todo servicio de pago debe justificarse.
- **R-04 — Conectividad:** las parcelas tienen conexión intermitente; la protección **no puede depender** del servidor.
- **R-06 — Integración:** servicio de mensajería para alertas (RF-05).

## Alternativas consideradas

1. **Monolito en capas (4,10).** Una aplicación, una sola capa de lógica de negocio con todos los módulos juntos. Simple, barato y rápido de entregar. Pero el **Control de válvulas** queda mezclado con el resto; si QA-01 exige aislamiento, esto es problemático. Se diagrama en [`../diagramas/alternativa.puml`](../diagramas/alternativa.puml).

2. **Arquitectura orientada a eventos (3,05).** Desacoplamiento con broker de mensajes. Requiere operar broker, consumidores y depuración distribuida; excede R-01, R-02 y R-03. Además, la falla segura **no se resuelve con el broker**: sigue necesitando temporizador local en el controlador de campo.

3. **Monolito modular (4,15).** Una aplicación y un solo despliegue, dividida en módulos de dominio (Lecturas de humedad, Programación de riego, Control de válvulas, Alertas, Parcelas y dispositivos) que se comunican **solo mediante interfaces públicas**. Las integraciones externas se implementan como adaptadores. **Elegido.**

## Decisión

**Usaremos un monolito modular en Django**, con cinco módulos de dominio: **Lecturas de humedad** (RF-01, RF-02), **Programación de riego** (RF-03), **Control de válvulas** (RF-04), **Alertas** (RF-05) y **Parcelas y dispositivos** (RF-06, RF-07).

Los módulos se comunicarán **solo mediante interfaces públicas** (servicios de aplicación). Las integraciones externas (controlador de campo, servicio de mensajería) se implementarán como **adaptadores** detrás de puertos definidos en el dominio.

**Cómo se materializa QA-01:** la falla segura **se garantiza en el controlador de campo** (ADR-003) con temporizador local. El módulo **Control de válvulas** aísla la lógica de órdenes (apertura/cierre con duración máxima), facilita pruebas con cortes de red simulados y evita que esa lógica quede dispersa. Esto permite verificar QA-01 independientemente del estilo servidor.

## Consecuencias

**Positivas**
- **Un solo despliegue y un solo VPS** (R-03), entregable en 1 mes (R-01) por 2 developers (R-02).
- **QA-01 verificable**: el Control de válvulas queda aislado; la falla segura depende de temporizador local (ADR-003).
- **Baja carga operativa**: un proceso, despliegue único.
- **Portabilidad**: adaptadores para controlador de campo y servicio de mensajería.
- **Ruta de escape**: puede extraerse módulos si escala lo justifica.

**Negativas / riesgos**
- **Disciplina de límites**: nada impide degenerar en capas. Mitigación: revisar límites en PR; considerar `import-linter`.
- **Punto único de fallo**: afecta todo el sistema. Aceptable para MVP.
- **Límites por convención**, no por compilador.
- **Escalado por replicado completo**, no por módulo.

## Alternativas descartadas, referencia
- Monolito en capas — [`alternativa.puml`](../diagramas/alternativa.puml)
- Arquitectura orientada a eventos — rechazada por R-01, R-02, R-03; ver §5.4 de [`matriz-decision.md`](../matriz-decision.md)