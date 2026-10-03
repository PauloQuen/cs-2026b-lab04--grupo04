# ADR-001: Adoptar un monolito modular para el MVP de EcoRecicla AQP

- **Estado:** Aceptado
- **Fecha:** 2026-10-03
- **Decisores:** Quenta Ahumada Paulo Estefano, Kevin Joel Callo Ccagiavilca

---

## Contexto

EcoRecicla AQP coordina el recojo de residuos reciclables con recicladores formalizados en distritos de
Arequipa. El sistema debe permitir que el vecino solicite un recojo (RF-01), que el reciclador consulte su
ruta del día (RF-02) y confirme el recojo registrando el peso (RF-03), que el vecino acumule y canjee puntos
(RF-04), que la municipalidad consulte toneladas recicladas (RF-05), administre distritos y reglas de puntos
(RF-06) y que el vecino reciba avisos por WhatsApp (RF-07).

El atributo de calidad **crítico del caso es la modificabilidad**: incorporar un nuevo distrito o una nueva
regla de puntos debe tomar **≤ 2 días-persona y sin modificar los demás módulos** (QA-01). Este es el único
dato medible que entrega el enunciado, y por eso concentra el 30 % del peso en la matriz de decisión
([`matriz-decision.md`](../matriz-decision.md)).

Las restricciones que condicionan la decisión son:

- **R-01 — Plazo:** el MVP debe estar en producción en **1 mes**.
- **R-02 — Equipo:** **2 developers** (Quenta Ahumada Paulo Estefano y Kevin Joel Callo Ccagiavilca), con
  Python/Django como stack principal.
- **R-03 — Presupuesto:** **un solo VPS**; todo servicio de pago debe justificarse.
- **R-06 — Integración:** WhatsApp Business API es obligatoria (RF-07) y es un tercero del que no controlamos
  ni el costo ni la disponibilidad.

La carga esperada es **moderada y predecible**: no hay dato de concurrencia ni picos extremos en el
enunciado. Solo 2 personas, y ninguna experiencia previa en DevOps.

## Alternativas consideradas

1. **Monolito en capas (3,80).** Una aplicación, una sola capa de lógica de negocio con todos los módulos
   juntos y un esquema único de base de datos. Simple, barato y rápido de entregar, pero la lógica compartida
   hace que agregar un distrito obligue a revisar Solicitudes, Rutas y Puntos. **No cumple QA-01.**
   Se diagrama en [`../diagramas/alternativa.puml`](../diagramas/alternativa.puml).

2. **Microservicios (3,00).** Un servicio por módulo, cada uno con su base de datos, comunicados por red y un
   broker de eventos. Gana en modificabilidad (5/5) y escalabilidad (5/5), pero exige 6 despliegues, 6 bases
   de datos, un broker, orquestación y monitoreo distribuido: capacidad operativa que **R-02 no permite
   adquirir en un mes** y que **R-03 no financia**. La IA lo recomendó por escalabilidad; el caso no declara
   ningún driver de escalabilidad que lo justifique.

3. **Monolito modular (4,05).** Una aplicación y un solo despliegue, dividida en módulos de dominio que se
   comunican únicamente por interfaces públicas, con un esquema de base de datos por módulo y las
   integraciones externas implementadas como adaptadores. **Elegido.**

## Decisión

**Usaremos un monolito modular en Django**, con seis módulos de dominio: **Solicitudes** (RF-01, RF-03),
**Rutas** (RF-02), **Puntos y Canjes** (RF-04), **Distritos y Reglas** (RF-06), **Reportes** (RF-05) y
**Notificaciones** (RF-07).

Los módulos se comunicarán **solo mediante interfaces públicas** (servicios de aplicación); ningún módulo importará tablas ni clases de otro módulo. Cada módulo tendrá su propio esquema en PostgreSQL. Las
integraciones externas (WhatsApp y ruteo) se implementarán como **adaptadores** detrás de puertos definidos
en el dominio, de modo que un cambio de proveedor no toque la lógica de negocio.

**Cómo se materializa QA-01 (el detalle que hace verificable la decisión):** el mecanismo de modificabilidad
no es "escribir el módulo bien", es que **un distrito nuevo y una regla de puntos nueva sean *datos*, no
*código***. Un distrito se agrega con un `INSERT` en las tablas del módulo Distritos y Reglas; una regla nueva
es un registro con su vigencia. El módulo Puntos la consume a través de su interfaz pública
`obtener_regla_vigente()`, sin importar sus tablas. Como consecuencia:

- **0 archivos de Solicitudes, Rutas, Reportes o Notificaciones se modifican** al dar de alta un distrito.
- Solo se toca el esquema `distritos` y, si la regla cambia la forma de calcular, el módulo Puntos.
- El reporte de toneladas (RF-05) agrupa por distrito **consultando la tabla de distritos**, por lo que un
  distrito nuevo aparece en el reporte sin cambiar la consulta.

## Consecuencias

**Positivas**

- **Un solo despliegue y un solo servidor**, lo que respeta R-03 y cabe en un VPS.
- **Entregable en el plazo de R-01**: dos developers pueden poner el MVP en producción en 1 mes sin invertir
  ese tiempo en infraestructura.
- **QA-01 se vuelve verificable**: el costo de un distrito nuevo es una carga de datos, no un desarrollo.
- **Baja carga operativa** (criterio que vale 20 % de la matriz): un proceso, una base de datos, un Nginx.
- **Ruta de escape clara**: si un módulo luego necesita escalar o desplegarse por separado, el patrón modular
  permite extraerlo como servicio sin reescribir los demás.
- **Portable entre proveedores** (WhatsApp, ruteo) gracias a los adaptadores.

**Negativas / riesgos**

- **La disciplina de límites es la principal amenaza.** Con 2 developers, nada impide técnicamente que un
  módulo importe tablas de otro y el monolito modular degenere en monolito en capas. **Mitigación:** el
  criterio de QA-01 se revisa en cada Pull Request, y queda bajo decisión del equipo agregar `import-linter` a la CI para que una
  dependencia prohibida entre módulos falle la integración.
- **Una falla grave afecta a todo el sistema**, porque es un solo proceso. Aceptable en el MVP; si aparece un
  módulo que Justifica aislamiento, se extrae.
- **Los límites entre módulos se definirán por convención, no por el compilador.** Por eso Modificabilidad
  puntuó 4 y no 5 para esta alternativa.
- **Escalar es más difícil que en microservicios**: se escala el proceso completo, no un módulo suelto.
- **Acoplamiento de la base de datos**: las transacciones que cruzan módulos (acreditar puntos al confirmar un
  recojo, que toca Solicitudes y Puntos) son posibles precisamente porque es un solo esquema. Es una
  ventaja hoy y una deuda si mañana se extrae un módulo.

## Alternativas descartadas, referencia

- Monolito en capas — [`alternativa.puml`](../diagramas/alternativa.puml)
- Microservicios con Kubernetes — rechazado por R-01, R-02 y R-03; ver §5.2 de
  [`matriz-decision.md`](../matriz-decision.md)