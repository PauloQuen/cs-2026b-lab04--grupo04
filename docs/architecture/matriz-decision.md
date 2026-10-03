# Matriz de decisión — EcoRecicla AQP

> Lab 04 · E2 · Caso 10 · Grupo 04
> Entradas: este archivo toma **únicamente** los drivers declarados en [`drivers.md`](drivers.md). No se introduce
> ningún criterio que no se pueda rastrear hasta un RF-, QA- o R- de ese documento.

---

## 1. Alternativas consideradas

Las tres alternativas se generaron con un asistente de IA mediante el Prompt 1 (RCRTF), y **se corrigieron
antes de|scorearlas**: la IA propusomicroservicios con Kubernetes, que se retiró por exceder R-01, R-02 y R-03
(ver §5). El prompt completo está en [`bitacora-ia.md`](bitacora-ia.md), anexo A.

- **A. Monolito en capas:** una sola aplicación y un solo despliegue, dividida en Presentación, Lógica de
  negocio y Acceso a datos. **Toda** la lógica del dominio (solicitudes, rutas, puntos, reglas, reportes)
  vive en la misma capa y comparte las mismas entidades.
- **B. Monolito modular:** una sola aplicación y un solo despliegue, dividida en **módulos de dominio**
  (Solicitudes, Rutas, Puntos y Canjes, Distritos y Reglas, Reportes, Notificaciones) que se comunican
  **solo mediante interfaces públicas**. Cada módulo tiene su esquema propio y sus adaptadores externos.
- **C. Microservicios:** un servicio independiente por módulo, cada uno con su **propia base de datos**,
  comunicados por red (REST/gRPC) y un broker de eventos (RabbitMQ), con API Gateway y monitoreo distribuido.

---

## 2. Criterios y pesos (suman exactamente 100 %)

| Criterio                  | Peso | Justificación (driver relacionado)                                                                                                          |
|---------------------------|------|----------------------------------------------------------------------------------------------------------------------------------------------|
| **Modificabilidad**       | 30 % | **QA-01**, el atributo crítico del caso: dar de alta un distrito o una regla nueva en ≤ 2 días-persona **sin tocar los demás módulos**. Pesa más que ningún otro criterio porque es el único atributo con dato medible en el enunciado. |
| **Tiempo de entrega**     | 25 % | **R-01** (MVP en producción en 1 mes) combinado con **R-02** (2 developers). Con dos personas, cada semana perdida *configurando* infraestructura es una semana que no sale funcionalidad nueva. |
| **Simplicidad operativa** | 20 % | **R-02**: 2 developers sin experiencia en DevOps. Un estilo que exija operar orquestadores, brokers, pipelines de despliegue y monitoreo distribuido es un estilo que el equipo no puede sostener tras el MVP. |
| **Costo operativo**       | 15 % | **R-03**: un único VPS. Cada servicio adicional que se paga tiene que justificarse frente a un presupuesto bajo. |
| **Escalabilidad**         | 10 % | La carga es **moderada y predecible** (distritos de Arequipa, sin picos extremos ni horas pico como las del caso AgroConecta). No hay ningún driver que exija escalado fino, así que este criterio no debe decidir la arquitectura por sí solo. |
| **Total**                 | **100 %** | — |

> **Por qué modificabilidad pesa más que el plazo, y no al revés.** Con 3 personas, un equipo puede tolerar
> "microservicios" durante un mes. Con 2, no: la curva de aprendizaje de Docker, ORQ y observabilidad se
> paga justo en el sprint que debería producir el MVP. Aun así, **el atributo crítico del caso manda**, y la
> forma de honrarlo sin pagar esa curva es B, no C.

---

## 3. Matriz de decisión (1 = muy malo … 5 = excelente)

| Criterio (peso)            | A. Monolito en capas | B. Monolito modular | C. Microservicios |
|----------------------------|-----------------------|---------------------|-------------------|
| Modificabilidad (30 %)     | 2                     | **4**               | 5                 |
| Tiempo de entrega (25 %)   | 5                     | **4**               | 2                 |
| Simplicidad operativa (20 %)| 5                    | **4**               | 1                 |
| Costo operativo (15 %)     | 5                     | **5**               | 2                 |
| Escalabilidad (10 %)       | 2                     | **3**               | 5                 |
| **Total ponderado**        | **3,80**              | **4,05** ← ganador | **3,00**          |

### Cálculo (verificable, sin hojas de cálculo ocultas)

Total ponderado = Σ (peso × puntaje).

- **A** = 0,30×2 + 0,25×5 + 0,20×5 + 0,15×5 + 0,10×2 = 0,60 + 1,25 + 1,00 + 0,75 + 0,20 = **3,80**
- **B** = 0,30×4 + 0,25×4 + 0,20×4 + 0,15×5 + 0,10×3 = 1,20 + 1,00 + 0,80 + 0,75 + 0,30 = **4,05**
- **C** = 0,30×5 + 0,25×2 + 0,20×1 + 0,15×2 + 0,10×5 = 1,50 + 0,50 + 0,20 + 0,30 + 0,50 = **3,00**

Los totales fueron recalculados con un script de Python para descartar errores aritméticos; el script está en
[`diagramas/matriz-ponderada.py`](diagramas/matriz-ponderada.py) y regenera además el gráfico de la Figura 4.

### Fundamento de cada puntaje

| Puntaje | Razonamiento                                                                                                                                                             |
|---------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Modificabilidad A = 2 | Al compartir una única capa de lógica y entidades, dar de alta un distrito obliga a revisar el código de Solicitudes, Rutas y Puntos. **No cumple QA-01**: es el motivo por el que se descarta. |
| Modificabilidad B = 4 | Los límites entre módulos se delimitan por convención (interfaces públicas + un esquema por módulo). No es un 5 porque **con 2 developers la disciplina de límites es más difícil de sostener** que con un equipo grande, y nada obliga técnicamente a respetarla. |
| Modificabilidad C = 5 | Cada módulo se despliega y versiona por separado: el máximo aislamiento. Por eso gana este criterio y aun así pierde la decisión. |
| Simplicidad C = 1 | Un orquestador, N bases de datos, un broker y monitoreo distribuido para 2 personas que nunca han operado eso. Es el mínimo absoluto de la escala. |
| Escalabilidad A = 2 / B = 3 / C = 5 | Escala vertical (una sola instancia) frente a escala por módulo. B puntúa 3 y no 4 porque se puede replicar la aplicación completa, pero no un módulo suelto. |
| Costo A = B = 5 | Los dos caben en un VPS sin costo adicional. C necesita al menos N instancias + N bases de datos + broker + monitoreo dentro del mismo R-03. |

---

## 4. Conclusión

**Elegimos B, el monolito modular (4,05).**

Es la única alternativa que **honra el atributo crítico** (QA-01: ≤ 2 días-persona y 0 archivos modificados
fuera de sus módulos para dar de alta un distrito o una regla de puntos) **sin** exigir al equipo capacidad
operativa que R-01 y R-02 no permiten adquirir en un mes. Los microservicios (3,00) ganan en modificabilidad y
escalabilidad, pero pierden por plazo, costo y complejidad operativa: pagarían un peaje de infraestructura
antes de haber escrito la primera funcionalidad.

**La decisión la tomó el equipo, no la IA.** La IA recomendó microservicios con Kubernetes; el equipo lo
descartó al contrastarlo con R-01, R-02 y R-03. El detalle está en §5.

**La segunda mejor alternativa es A, el monolito en capas (3,80)**, y es la que se diagrama en E5
([`diagramas/alternativa.puml`](diagramas/alternativa.puml)) para dejar constancia de por qué se descartó.

Decisión formalizada en: **[ADR-001 — Estilo arquitectónico](adr/001-estilo-arquitectonico.md)**.

---

## 5. Verificación de la salida de la IA (obligatorio en E2)

La guía exige registrar al menos una afirmación incorrecta, exagerada o que no respete las restricciones, y
**cómo se comprobó**. Registramos tres, todas con fuente oficial consultada el **03/10/2026**.

### 5.1 «Escalabilidad es el criterio que más peso debería tener» → **FALSO para este caso** · decisión: **Corregida**

**Qué propuso la IA:** en el borrador de la matriz ponderada, *Escalabilidad* figuraba entre los criterios de peso
alto, con la justificación genérica de que *"todo sistema debe poder escalar"*.

**Cómo lo verificamos:** se cotejó la matriz contra el enunciado del caso 10 y se encontró que **no existe ningún
driver de escalabilidad**. El caso no declara concurrencia, ni horas pico, ni volumen de sensores comparable al caso
AgroConecta (300 concurrentes) o RutaSIT (300 buses × 10 s). El único atributo con medida numérica es la
**modificabilidad**. Un criterio sin una línea del enunciado detrás es un criterio inventado, y la propia guía lo
advierte en §1.7 al hablar del sesgo de los asistentes hacia la arquitectura de moda.

**Corrección aplicada:** *Escalabilidad* bajó al **peso más bajo (10 %)** y su justificación ahora dice
explícitamente que no hay ningún driver que lo exija, en lugar de una fórmula genérica. Los otros cuatro criterios
sí se pudieron trazar hasta `drivers.md` (QA-01 modificabilidad, R-01 plazo, R-02 equipo, R-03 costo).

### 5.2 «El diagrama Mermaid generado es correcto, solo hay que revisarlo» → **FALSO** · decisión: **Corregida**

**Qué propuso la IA:** un `flowchart` con los 3 actores, los 6 módulos, PostgreSQL y los 2 servicios externos.
SejoursuSin responder si el diagrama *compilaba*: "está bien estructurado, revisa los nombres".

**Cómo lo verificamos:** se intentó **renderizar** el archivo, no solo leerlo. Falló:

```
Error: Parse error on line 1:
%%flowchart TB
```

Se aisló la causa por bisección hasta un caso mínimo de 4 líneas: **una línea de comentario que contiene solo
`%%` rompe el lexer de Mermaid**. Se comprobó el caso contrario (`%%` seguido de texto) y sí compilaba. De paso se
corregieron un módulo sin RF asociado y dos flechas con dirección invertida respecto de la regla de dependencias
del propio diagrama.

**Corrección aplicada:** cada `%%` vacío pasó a ser `%% --- ... ---` y el render generó el PNG sin errores. La
lección quedó registrada en `bitacora-ia.md`: *leer no es verificar, hay que ejecutar la herramienta*.

### 5.3 «La API de WhatsApp se activa al instante con una API key y las plantillas no tienen costo» → **PARCIALMENTE FALSO** · decisión: **Corregida**

**Qué propuso la IA:** integrar WhatsApp Business API *"con solo una cuenta y una API key"*, y tratar el módulo
Notificaciones como **costo operativo cero**, con las plantillas de aviso sin cargo.

**Cómo lo verificamos:** documentación oficial de Meta, *Pricing on the WhatsApp Business Platform*
(<https://developers.facebook.com/documentation/business-messaging/whatsapp/pricing>, consultada el 03/10/2026):

- La API **no se activa al instante**: las plantillas requieren un proceso de aprobación previo, y la cuenta es
  de empresa, con un proveedor de soluciones verificado. El borrador omitía ambos requisitos.
- Desde el **1 de julio de 2025** Meta cobra **por mensaje entregado** y el modelo por conversación quedó
  **deprecado**. Se cobra cuando el mensaje se **entrega**, no cuando se envía.
- Los **mensajes de plantilla (`template`) sí se cobran**, según la categoría de la plantilla y el prefijo
  telefónico del destinatario. El aviso *«tu recojo está programado para mañana»* es una plantilla **utility**:
  su tarifa es menor que la de *marketing*, pero **no es gratis**. Enviar una plantilla fuera de la ventana de
  atención **también se factura**; lo que evita el cobro es mandarla **dentro** de la ventana de 24 h que abre el
  usuario.
- Desde el **1 de octubre de 2026** también se cobran los **mensajes de servicio** (los que no son plantilla), con
  una exención de **1 000 mensajes de servicio gratis al mes por número de teléfono**, que no se acumula.

**Corrección aplicada:** el presupuesto de R-03 incluye una partida por volumen de mensajes, y el aviso se
diseña como plantilla *utility* **dentro** de la ventana de atención, que es el caso más barato. Esto **no cambia
la arquitectura** —el módulo Notificaciones sigue siendo un adaptador aislado detrás de una interfaz— pero sí
obliga a medir el volumen mensual, porque el costo escala con el número de recojos notificados.

### 5.4 «Los servicios de mapas son gratis y sin cuota» → **PARCIALMENTE FALSO** · decisión: **Corregida**

**Qué propuso la IA:** usar un servicio de mapas con *«cuota gratuita ilimitada»* para el módulo Rutas.

**Cómo lo verificamos:**

- Google Maps Platform **no tiene cuota ilimitada**: la Directions API cuesta **USD 5 por 1 000 solicitudes** y la
  Distance Matrix API **USD 10 por 1 000 elementos**, después de un crédito mensual de USD 200. La cuota gratuita
  se aplica **por servicio**, no agrupada.
- Los **datos** de OpenStreetMap son libres bajo licencia ODbL, pero **eso no implica servicios gratuitos**: el
  servidor público de Nominatim tiene una **política de uso** que prohíbe el tráfico de producción. La distinción
  importa: *datos libres* ≠ *infraestructura gratis*.
- **OSRM** (Open Source Routing Machine) es un motor de ruteo **libre, sin costo por petición y auto-hospedable**
  (licencia BSD, implementado en **C++**). Ofrece los servicios `route` y `table` (matriz de distancias), que es
  exactamente lo que necesita el módulo Rutas, y ya es parte del stack declarado del equipo.

**Corrección aplicada:** el módulo Rutas se implementará con un **puerto de ruteo** que hoy apunta a un adaptador
OSRM (gratis, R-03 respetado) y que mañana puede apuntar a un proveedor pago sin tocar la lógica de negocio. Esta
corrección es exactamente lo que hace útil el patrón de adaptador dentro del monolito modular.

---

## 6. Lo que la IA hizo bien (también se registra)

Una bitácora solo con errores es tan poco creíble como una sin ellos. La IA **sí acertó** en:

- los tres estilos propuestos son los que la guía usa como modelo (capas, monolito modular, microservicios),
  y en el orden correcto de comparación;
- el análisis de que un monolito modular **necesita disciplina de límites** y que sin ella degenera en capas:
  ese es el riesgo central de la alternativa elegida y terminó documentado como consecuencia negativa en ADR-001;
- el puntaje de modificabilidad de microservicios como máximo de la escala (5/5), que es correcto y fue lo que
  hizo que la alternativa perdiera por dónde debía;
- la mecánica de **puertos y adaptadores**, que es la razón por la que las correcciones 5.3 y 5.4 pudieron
  cambiar de proveedor externo **sin tocar** la arquitectura;
- la estructura del prompt RCRTF y el criterio de que un estilo arquitectónico debe justificarse contra los
  drivers, que es exactamente el criterio que este equipo usó después para detectar el error de 5.1.

Lo que **no** hizo fue aplicar las restricciones del enunciado al ponderar: por eso el error de 5.1 —dar peso
alto a un criterio sin driver— es el mismo fallo que la guía describe en §1.7, aunque con otro envoltorio: no
se recomendaron Kubernetes, pero se habló de escalabilidad como si el caso la exigiera.
---

## Referencias

- Richards, M. y Ford, N. (2020). *Fundamentals of Software Architecture*. O'Reilly. — estilos arquitectónicos y sus trade-offs.
- Meta for Developers (03/10/2026). *Pricing on the WhatsApp Business Platform*. <https://developers.facebook.com/documentation/business-messaging/whatsapp/pricing>
- Project OSRM. <https://project-osrm.org/> — motor de ruteo libre (BSD, C++), servicios `route` y `table`.
- Guía del Lab 04, secciones 1.4 (estilos), 1.7 (IA como apoyo) y II Paso 3 (verificación humana).