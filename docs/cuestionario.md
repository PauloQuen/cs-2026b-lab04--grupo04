# Cuestionario — Laboratorio 04: Fundamentos de Arquitectura de Software

> **Curso:** Construcción de Software · EPIS-UNSA · Semestre 2026-B  
> **Caso 10:** EcoRecicla AQP  
> **Grupo 04:** Quenta Ahumada Paulo Estefano y Kevin Joel Callo Ccagiavilca  

---

### 1. ¿Por qué se afirma que una decisión arquitectónica es aquella "costosa de cambiar"? Dé un ejemplo de su caso.

**Respuesta:**  
Una decisión arquitectónica es aquella que tiene un impacto estructural transversal en el sistema y condiciona los componentes, interfaces, tecnologías y flujos de trabajo posteriores. Conforme avanza el ciclo de vida del software, el costo de revertir una decisión de este nivel crece exponencialmente (no solo en refactorización de código fuente, sino en migración de datos capturados, reconfiguración de infraestructura de producción, pruebas de regresión y curva de reaprendizaje del equipo).

**Ejemplo en EcoRecicla AQP:**  
La decisión documentada en el [ADR-002](architecture/adr/002-base-de-datos.md) de usar **PostgreSQL con particionamiento de esquemas relacionales por módulo** frente a una base de datos documental (MongoDB). Cambiar a posteriori el motor relacional por uno documental una vez que el sistema esté operando significaría:
1. Reescribir el mapeo de modelos en el ORM de Django en los 6 módulos de dominio.
2. Descartar las transacciones ACID nativas del motor que aseguran que al registrar un recojo (RF-03) se acrediten los puntos (RF-04) exactamente una vez, obligando a implementar patrones complejos de consistencia eventual o transacciones distribuidas en la aplicación.
3. Migrar esquemas estructurados de recojos y tonelajes a colecciones de documentos JSON sin soporte nativo de agregaciones SQL optimizadas (`GROUP BY`, `SUM`).

---

### 2. ¿Cuál es la diferencia entre un requisito funcional y un atributo de calidad? ¿Por qué los atributos de calidad influyen más en la arquitectura?

**Respuesta:**  
- **Requisito Funcional (RF):** Define **qué** debe hacer el sistema: las capacidades, comportamientos, entradas y salidas específicas que satisfacen las necesidades de negocio del usuario (ejemplo en nuestro caso: RF-01, *"El vecino solicita el recojo indicando dirección y tipo de residuo"*).
- **Atributo de Calidad (QA):** Define **cómo de bien** debe comportarse el sistema con respecto a propiedades observables en ejecución o desarrollo (rendimiento, fiabilidad, modificabilidad, seguridad, etc., según ISO/IEC 25010:2023).

**Por qué los atributos de calidad influyen más en la arquitectura:**  
Casi cualquier funcionalidad de negocio puede implementarse en cualquier estilo arquitectónico (sea un script monolítico de un solo archivo, una aplicación en capas o una red de microservicios). Sin embargo, son los **atributos de calidad y las restricciones** los que determinan qué estructuras organizativas son viables y cuáles no:
- El requisito funcional RF-06 (administrar distritos) funciona igual en un monolito en capas que en uno modular; pero el atributo de calidad crítico **QA-01 (Modificabilidad: dar de alta un distrito en $\le 2$ días-persona y con 0 archivos tocados fuera de su módulo)** descarta de raíz el monolito en capas y obliga a adoptar límites estrictos de dominio (monolito modular o microservicios).

---

### 3. Reescriba el requisito "el sistema debe ser seguro" como un escenario de atributo de calidad de seis partes.

**Respuesta:**  
Siguiendo la plantilla formal de seis partes de Bass, Clements y Kazman (2021), el requerimiento vago de seguridad se formula para nuestro caso (conforme a QA-04 en [`drivers.md`](architecture/drivers.md)):

| Parte | Definición | Valor en el Escenario (QA-04) |
|---|---|---|
| **Fuente del estímulo** | ¿Quién o qué genera el evento? | Un usuario anónimo o un vecino no autenticado en la red pública. |
| **Estímulo** | ¿Qué evento o acción ocurre? | Intenta acceder directamente a los endpoints de la API (`/api/solicitudes/` y `/api/puntos/`) enviando peticiones con el identificador de otro vecino para extraer direcciones domiciliarias y saldos. |
| **Artefacto** | ¿Qué elemento del sistema recibe el estímulo? | La capa de presentación / Gateway de la API REST del módulo Solicitudes y Puntos. |
| **Entorno** | ¿En qué condiciones operativas ocurre? | Operación normal en producción, comunicación bajo HTTPS. |
| **Respuesta** | ¿Qué hace el sistema ante el estímulo? | El middleware de autenticación y autorización intercepta las peticiones, rechaza el acceso con códigos de estado HTTP 401/403, no expone datos protegidos por la Ley 29733 y registra un evento de auditoría con IP, timestamp e ID solicitado. |
| **Medida de respuesta** | ¿Cómo se mide objetivamente el resultado? | **100 % de 200 intentos simulados de acceso no autorizado son bloqueados** y el 100 % de los intentos fallidos queda registrado en la bitácora de seguridad sin fuga de datos personales. |

---

### 4. Compare el monolito modular y los microservicios en términos de costo, modificabilidad y complejidad operativa. ¿En qué momento convendría migrar de uno a otro?

**Respuesta:**  

| Criterio | Monolito Modular (Alternativa elegida) | Microservicios (Alternativa descartada) |
|---|---|---|
| **Costo económico** | **Bajo:** Se despliega en un único VPS modesto (R-03). Comparte memoria de proceso, una sola base de datos (con esquemas lógicos) y un proxy inverso Nginx. | **Alto:** Requiere múltiples máquinas virtuales o clusters de contenedores (Kubernetes), bases de datos independientes por servicio, redes virtuales privadas y almacenamiento segregado. |
| **Modificabilidad** | **Alta dentro del código:** Cada módulo tiene interfaces públicas delimitadas. Agregar un módulo o modificar uno existente no afecta al resto si se respetan las fronteras lógicas. | **Máxima e independiente:** Despliegue, versionado y ciclo de vida de cada servicio desacoplado al 100 %, permitiendo que distintos equipos trabajen y desplieguen sin coordinar lanzamientos globales. |
| **Complejidad operativa** | **Baja:** Un solo binario/proceso, un único pipeline de integración/despliegue continuo (CI/CD), logging centralizado local y monitoreo sencillo. | **Extrema:** Requiere orquestación de contenedores, API Gateways, Service Mesh, brokers de mensajería (RabbitMQ/Kafka), monitoreo distribuido (trazabilidad con Jaeger/Zipkin) y gestión de fallos parciales en red. |

**¿En qué momento convendría migrar de un monolito modular a microservicios?**  
La migración se justificaría únicamente cuando se alcancen al menos dos de los siguientes hitos:
1. **Crecimiento drástico del equipo:** Si la organización pasa de 2 developers (R-02) a más de 3 o 4 equipos autónomos independientes que sufren cuellos de botella al desplegar en un repositorio común.
2. **Asimetría extrema de carga/escalabilidad:** Si un módulo específico (por ejemplo, el tracking GPS de recojo o ingesta masiva de solicitudes) requiere escalar horizontalmente a decenas de instancias, mientras que los módulos de *Distritos y Reglas* o *Reportes* apenas reciben unas pocas peticiones al día.
3. **Requerimientos tecnológicos heterogéneos:** Si un servicio específico necesita implementarse en un stack especializado (ej. Rust/Go para cálculo geoespacial intensivo) incompatible con el runtime principal de Django.

---

### 5. ¿Qué ventajas ofrece Diagram as Code frente a herramientas de dibujo como PowerPoint? Mencione al menos tres.

**Respuesta:**  
1. **Versionabilidad y trazabilidad en Git:** Al estar escrito en texto plano (`.mmd`, `.puml`, `.py`), cada cambio en la arquitectura se documenta mediante commits, se revisa en Pull Requests y permite visualizar diferencias línea por línea (`git diff`), a diferencia de los archivos binarios de PowerPoint donde no hay diff legible.
2. **Mantenibilidad y regeneración automatizada:** Modificar un componente o agregar una conexión solo requiere editar una línea de texto; la herramienta recalcula el layout automáticamente sin necesidad de reacomodar cuadros y flechas manualmente. Además, se integra en flujos automatizados de CI/CD (GitHub Actions).
3. **Sinergia nativa con Modelos de Lenguaje (IA):** Los asistentes de IA pueden generar, auditar, refactorizar y corregir diagramas estructurados en texto rápidamente, posibilitando flujos de trabajo ágiles y reproducibles entre personas y herramientas automáticas.

---

### 6. ¿Qué elementos debe contener un ADR y por qué es importante registrar también las alternativas descartadas?

**Respuesta:**  
Siguiendo el estándar de Michael Nygard (2011), un ADR debe contener:
1. **Título y Metadatos:** Identificador numérico, estado (*Propuesto*, *Aceptado*, *Rechazado*, *Superado*), fecha y decisores.
2. **Contexto:** El problema técnico o de negocio que motiva la decisión, citando explícitamente los drivers que lo condicionan (requisitos funcionales, atributos de calidad y restricciones).
3. **Alternativas consideradas:** Las opciones viables evaluadas junto a sus pros y contras.
4. **Decisión:** La solución elegida redactada en voz activa (*"Usaremos..."* o *"Decidimos..."*).
5. **Consecuencias:** Impacto positivo (ganancias) y negativo (riesgos, costos o deudas técnicas asumidas).

**Por qué es importante registrar las alternativas descartadas:**  
Registrar las opciones descartadas evita el fenómeno de la "amnesia arquitectónica": cuando nuevos desarrolladores se incorporan al proyecto o se presentan dificultades, es común que sugieran soluciones alternativas que parecen lógicas a primera vista (por ejemplo, *"¿por qué no usamos microservicios?"*). El ADR deja constancia explícita de por qué esa opción fue evaluada y rechazada frente a las restricciones del caso (R-01 de 1 mes y R-03 de presupuesto), impidiendo discusiones cíclicas y decisiones impulsivas.

---

### 7. Describa un caso de esta práctica en el que la IA haya generado una propuesta incorrecta o sesgada. ¿Cómo lo detectaron?

**Respuesta:**  
En la **Interacción 1** del diseño arquitectónico ([`bitacora-ia.md`](architecture/bitacora-ia.md) y [`matriz-decision.md`](architecture/matriz-decision.md) §5.1), la IA generó una matriz de decisión donde le asignó un peso elevado a **"Escalabilidad"**, argumentando de forma genérica que *"todo sistema moderno debe estar preparado para escalar"*, lo cual favorecía artificialmente la opción de microservicios con Kubernetes.

**Cómo lo detectamos:**  
El equipo contrastó de forma sistemática cada criterio propuesto contra los drivers del Caso 10 de la guía. Se constató que el enunciado de *EcoRecicla AQP* **no declara ningún pico de concurrencia, ni tráfico de miles de usuarios simultáneos, ni ingesta masiva de sensores** (a diferencia de otros casos como *AgroConecta* o *RutaSIT*).  
El único atributo de calidad con medida numérica obligatoria en el enunciado es la **Modificabilidad (QA-01)**. Introducir un criterio con peso alto sin sustento en el enunciado evidenció el típico sesgo de los LLM hacia tecnologías de moda (*hype-driven architecture*). Se corrigió bajando su peso al 10% y condicionando la elección a las restricciones reales: 2 developers (R-02) y 1 mes de plazo (R-01).

---

### 8. ¿Qué riesgos éticos y de confidencialidad existen al usar asistentes de IA para diseñar la arquitectura de un sistema real?

**Respuesta:**  
1. **Fuga de información confidencial y datos personales:** Al enviar prompts a proveedores de LLMs externos, se corre el riesgo de filtrar secretos comerciales, topologías internas de red, credenciales o datos protegidos (como domicilios de ciudadanos bajo la Ley 29733). Para mitigar esto, ningún prompt debe contener datos reales de producción ni información privada.
2. **Delegación acrítica de responsabilidad (riesgo ético y profesional):** Si un equipo asume ciegamente las sugerencias de la IA sin verificación formal, traslada la toma de decisiones arquitectónicas a un modelo probabilístico. En sistemas reales (por ejemplo, sector salud o infraestructura crítica), las fallas derivadas de alucinaciones o supuestos erróneos de la IA son responsabilidad legal y ética exclusiva de los ingenieros firmantes, no del asistente.
3. **Dependencia tecnológica y sesgos de entrenamiento:** Los modelos tienden a favorecer tecnologías promovidas masivamente en repositorios públicos anglosajones (nubes hiper-escaladas como AWS, stacks complejos), penalizando alternativas locales, abiertas o de bajo costo (como VPS sencillos, OSRM libre o monolitos bien estructurados) que son las más éticas y viables para proyectos con recursos públicos o comunitarios limitados.
