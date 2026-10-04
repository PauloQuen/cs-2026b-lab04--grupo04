# Matriz de decisión — ChacraSmart Majes

> Lab 04 · E2 · Caso 9 · Grupo 04
> Entradas: este archivo toma **únicamente** los drivers declarados en [`drivers.md`](drivers.md). No se introduce
> ningún criterio que no se pueda rastrear hasta un RF-, QA- o R- de ese documento.

---

## 1. Alternativas consideradas

Las tres alternativas se generaron con un asistente de IA mediante el Prompt 1 (RCRTF), y **se corrigieron
antes de evaluarlas**: la IA propuso microservicios con broker MQTT/operador IoT complejo, que se retiraron por exceder R-01, R-02 y R-03
(ver §5). El prompt completo está en [`bitacora-ia.md`](bitacora-ia.md), anexo A.

- **A. Monolito en capas:** una sola aplicación y un solo despliegue, dividida en Presentación, Lógica de
  negocio y Acceso a datos. **Toda** la lógica del dominio (lecturas, riego, válvulas, alertas, parcelas)
  vive en la misma capa y comparte las mismas entidades.
- **B. Monolito modular:** una sola aplicación y un solo despliegue, dividida en **módulos de dominio**
  (Lecturas de humedad, Programación de riego, Control de válvulas, Alertas, Parcelas y dispositivos) que se comunican
  **solo mediante interfaces públicas**. Cada módulo tiene sus adaptadores externos.
- **C. Arquitectura orientada a eventos:** los dispositivos publican eventos (lecturas, estado) en un broker de mensajes y servicios independientes reaccionan a ellos. Esto añade complejidad operativa frente al monolito.

---

## 2. Criterios y pesos (suman exactamente 100 %)

| Criterio                  | Peso | Justificación (driver relacionado)                                                                                                          |
|---------------------------|------|----------------------------------------------------------------------------------------------------------------------------------------------|
| **Fiabilidad y protección (safety)** | 30 % | **QA-01**, atributo crítico: ninguna válvula debe quedar abierta más del tiempo programado si se pierde la conexión. Mide aislamiento del control de válvulas. |
| **Tiempo de entrega**     | 25 % | **R-01** (MVP en producción en 1 mes) combinado con **R-02** (2 developers). Cada semana configurando infraestructura es una semana sin funcionalidad. |
| **Simplicidad operativa** | 20 % | **R-02**: equipo pequeño sin experiencia en operar infraestructura compleja (brokers, orquestadores). |
| **Costo operativo**       | 15 % | **R-03**: un único VPS. Cada servicio adicional debe justificarse. |
| **Modificabilidad**       | 10 % | **QA-03**: agregar nuevos tipos de sensor sin tocar otros módulos. |
| **Total**                 | **100 %** | — |

> **Por qué el atributo crítico pesa más que el plazo, y no al revés.** Es tentador priorizar "tiempo de
> entrega" (25 %) porque R-01 es un plazo duro y R-02 es un equipo de solo 2 personas. Pero el orden de los
> drivers pone la **fiabilidad y protección primero**: una plataforma que riega de más ante un corte de red
> causa un daño real al cultivo, mientras que un MVP con dos semanas de atraso es un problema del negocio. Por eso
> *Fiabilidad y protección* pesa 30 %, y **modificabilidad baja a 10 %** aunque QA-03 sea real: es un atributo
> deseable, no el que puede dejar una parcela inundada. Aun así, el atributo crítico manda, y la forma de
> honrarlo **sin** pagar la curva de aprendizaje de un orquestador es B, no C.

---

## 3. Matriz de decisión (1 = muy malo … 5 = excelente)

| Criterio (peso)                        | A. Monolito en capas | B. Monolito modular | C. Arquitectura orientada a eventos |
|----------------------------------------|-----------------------|---------------------|-------------------------------------|
| Fiabilidad y protección (30 %)         | 3                     | **4**               | 4                                   |
| Tiempo de entrega (25 %)               | 5                     | **4**               | 2                                   |
| Simplicidad operativa (20 %)           | 5                     | **4**               | 2                                   |
| Costo operativo (15 %)                 | 5                     | **5**               | 3                                   |
| Modificabilidad (10 %)                 | 2                     | **4**               | 5                                   |
| **Total ponderado**                    | **4,10**              | **4,15** ← ganador | **3,05**                            |

### Cálculo (verificable, sin hojas de cálculo ocultas)

Total ponderado = Σ (peso × puntaje).

- **A** = 0,30×3 + 0,25×5 + 0,20×5 + 0,15×5 + 0,10×2 = 0,90 + 1,25 + 1,00 + 0,75 + 0,20 = **4,10**
- **B** = 0,30×4 + 0,25×4 + 0,20×4 + 0,15×5 + 0,10×4 = 1,20 + 1,00 + 0,80 + 0,75 + 0,40 = **4,15**
- **C** = 0,30×4 + 0,25×2 + 0,20×2 + 0,15×3 + 0,10×5 = 1,20 + 0,50 + 0,40 + 0,45 + 0,50 = **3,05**

Los totales fueron recalculados con un script de Python para descartar errores aritméticos; el script está en
[`diagramas/matriz-ponderada.py`](diagramas/matriz-ponderada.py) y regenera además el gráfico de la Figura 4.

### Fundamento de cada puntaje

| Puntaje | Razonamiento                                                                                                                                                             |
|---------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Fiabilidad y protección A = 3 / B = 4 / C = 4 | En A el Control de válvulas comparte la lógica de negocio con el resto, así que un cambio en el riego puede tocar el cierre remoto (RF-04) sin revisión explícita. B aísla ese módulo detrás de una interfaz pública, lo que hace la falla segura verificable. **C no sube a 5**: un broker mejora la entrega del mensaje, no la seguridad de la válvula, que depende del temporizador local del controlador (ADR-003). |
| Modificabilidad A = 2 | Al compartir una única capa de lógica y entidades, dar de alta un tipo nuevo de sensor obliga a revisar Lecturas de humedad, Programación de riego y Alertas. **No cumple QA-03**: es el motivo por el que se descarta. |
| Modificabilidad B = 4 | Los límites entre módulos se delimitan por convención (interfaces públicas + un esquema por módulo). No es un 5 porque **con 2 developers la disciplina de límites es más difícil de sostener** que con un equipo grande, y nada obliga técnicamente a respetarla. |
| Modificabilidad C = 5 | Cada módulo se despliega y versiona por separado: el máximo aislamiento. Por eso gana este criterio y aun así pierde la decisión. |
| Simplicidad operativa C = 2 | Un orquestador, N bases de datos, un broker y monitoreo distribuido para 2 personas que nunca han operado eso (R-02). No es 1 porque el dominio es acotado, pero es inviable en el plazo. |
| Costo A = B = 5 / C = 3 | Los dos caben en un VPS sin costo adicional (R-03). C necesita al menos N instancias + N bases de datos + broker + monitoreo dentro del mismo presupuesto. |

---

## 4. Conclusión

**Elegimos B, el monolito modular (4,15).**

Es la alternativa que **honra el atributo crítico** (QA-01: fiabilidad y protección). Aísla el **Control de válvulas** tras una interfaz pública, lo que hace verificable la falla segura, sin exigir la complejidad operativa de un broker de eventos (R-01, R-02, R-03). El monolito modular ofrece modificabilidad suficiente (4/5) con un único despliegue en 1 mes.

> **La ventaja es de 0,05 puntos.** Conviene decirlo con todas sus letras: B y A quedan casi empatadas, y la
> diferencia real no está en el número sino en **dónde vive la responsabilidad de cerrar la válvula**. B separa
> el control de válvulas detrás de una interfaz pública; A lo mezcla con el resto de la lógica. Como
> **Fiabilidad y protección pesa 30 %**, ese aislamiento es lo que decide. Si el atributo crítico fuera otro,
> la decisión podría cambiar: por eso el análisis se publica completo, con sus puntajes, en vez de solo el resultado.

**La decisión la tomó el equipo, no la IA.** La IA recomendó microservicios y orquestación; el equipo lo descartó al contrastarlo con R-01, R-02, R-03 y R-04 (conectividad intermitente). El detalle está en §5.

**La segunda mejor alternativa es A, el monolito en capas (4,10)**, que se diagrama en E5
([`diagramas/alternativa.puml`](diagramas/alternativa.puml)) para dejar constancia de por qué se descartó (mezcla el control de válvulas con el resto de la lógica, penalizando fiabilidad 3/5 y modificabilidad 2/5).

Decisión formalizada en: **[ADR-001 — Estilo arquitectónico](adr/001-estilo-arquitectonico.md)**.

---

## 5. Verificación de la salida de la IA (obligatorio en E2)

La guía exige registrar al menos una afirmación incorrecta, exagerada o que no respete las restricciones, y
**cómo se comprobó**. Registramos tres, todas con fuente oficial consultada el **03/10/2026**.

### 5.1 «El servidor detecta la desconexión y cierra la válvula» → **FALSO** · decisión: **Corregida**

**Qué propuso la IA:** propuso que, ante la pérdida de conexión con la válvula abierta, *"el servidor detecta la desconexión y envía la orden de cierre"*.

**Cómo lo verificamos:** razonando sobre QA-01 y R-04 (conectividad intermitente). **Sin conexión, no llega ningún comando desde el servidor.** El cierre no puede depender de la red. Por ello la protección debe residir en el **controlador de campo** con un temporizador local (ver ADR-003). Esto es una afirmación lógicamente imposible y representa un error crítico para un atributo de *safety*.

**Corrección aplicada:** el criterio crítico pasó a ser **Fiabilidad y protección (safety)** (30 %), y la matriz/ADR dejan explícito que la falla segura se garantiza en el controlador de campo, no en el servidor.

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

### 5.3 «Se puede confiar en que el servidor detecta desconexión para cerrar válvula» → **FALSO** · decisión: **Corregida**

**Qué propuso la IA:** asumió que la protección opera en el servidor (detección de desconexión). Eso es imposible sin conexión (R-04).

**Cómo lo verificamos:** análisis lógico del caso (fall-safe). La solución correcta es **temporizador local en el controlador** (ADR-003). Cada orden de apertura lleva duración máxima y el controlador cierra por sí solo.

**Corrección aplicada:** ADR-003 documenta explícitamente esta decisión con alternativas (servidor vs temporizador local). El atributo crítico se justifica correctamente.

### 5.4 «Microservicios/Kubernetes son necesarios» → **FALSO** · decisión: **Corregida**

**Qué propuso la IA:** sugería microservicios con broker para "escalabilidad", exagerando complejidad.

**Cómo lo verificamos:** contrastado con R-01 (1 mes), R-02 (2 developers), R-03 (1 VPS). El equipo no tiene capacidad operativa. El monolito modular (B) alcanza QA-01 manteniendo despliegue único.

**Corrección aplicada:** descartamos C (eventos) y priorizamos simplicidad operativa sobre complejidad innecesaria.

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
- Guía del Lab 04, secciones 1.4 (estilos), 1.7 (IA como apoyo) y II Paso 3 (verificación humana).
- Bass, L., Clements, P. y Kazman, R. (2021). *Software Architecture in Practice* (4.ª ed.). Addison-Wesley. — safety/falla segura.