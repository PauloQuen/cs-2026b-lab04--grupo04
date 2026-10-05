# Cuestionario — Laboratorio 04: Fundamentos de Arquitectura de Software

> **Curso:** Construcción de Software · EPIS-UNSA · Semestre 2026-B  
> **Caso 09:** ChacraSmart Majes  
> **Grupo 04:** Quenta Ahumada Paulo Estefano y Kevin Joel Callo Ccagiavilca  

---

### 1. ¿Por qué se afirma que una decisión arquitectónica es aquella "costosa de cambiar"? Dé un ejemplo de su caso.

**Respuesta:**  
Una decisión arquitectónica es aquella que define las estructuras fundamentales del sistema, sus componentes clave y los principios que guían su diseño e interconexión (Bass et al., 2021; ISO/IEC/IEEE 42010). Se dice que es "costosa de cambiar" porque una vez implementada y puesta en producción, revertirla tiene un costo exponencial que trasciende la simple modificación de líneas de código: involucra rediseño de protocolos, migración de infraestructura, cambios físicos en dispositivos periféricos y tiempo no planificado.

**Ejemplo en ChacraSmart Majes:**  
La decisión documentada en el [ADR-003](architecture/adr/003-apagado-seguro-en-controlador.md) sobre **dónde reside la lógica de falla segura (safety)**: en un temporizador autónomo en el controlador de campo frente a delegarla en el servidor en la nube.  
Si inicialmente se hubiera construido asumiendo que el servidor envía la orden de cierre al expirar el tiempo de riego, y en producción se descubriera que los cortes frecuentes de red 3G en las parcelas dejan válvulas abiertas inundando cultivos, el cambio exigiría:
1. Reprogramar y volver a flashear el firmware de todos los controladores físicos distribuidos en las parcelas de Majes.
2. Rediseñar el contrato de la API y el payload de apertura para incluir la duración máxima obligatoria.
3. Reconfigurar los circuitos de watchdog y persistencia local de hardware para tolerar reinicios imprevistos.

---

### 2. ¿Cuál es la diferencia entre un requisito funcional y un atributo de calidad? ¿Por qué los atributos de calidad influyen más en la arquitectura?

**Respuesta:**  
- **Requisito Funcional (RF):** Expresa **qué** servicios o funciones debe proporcionar el sistema al usuario o actor (ejemplo en nuestro caso: RF-03, *"El agricultor programa un riego indicando parcela, hora y duración"* y RF-04, *"El agricultor abre o cierra una válvula de forma remota"*).
- **Atributo de Calidad (QA):** Describe **cómo de bien** el sistema debe satisfacer esas funciones respecto a propiedades medibles como rendimiento, fiabilidad, mantenibilidad o seguridad (ISO/IEC 25010:2023).

**Por qué los atributos de calidad influyen más en la arquitectura:**  
Cualquier funcionalidad básica (abrir una válvula o recibir datos de un sensor) puede codificarse en prácticamente cualquier lenguaje o estilo arquitectónico. Sin embargo, son los **atributos de calidad y las restricciones** los que imponen la estructura:
- En *ChacraSmart Majes*, el atributo crítico **QA-01 (Fiabilidad y protección / safety: si se pierde la conexión, ninguna válvula queda abierta más del tiempo programado)** es el que obliga a desacoplar el módulo de *Control de válvulas* y a trasladar la garantía de cierre al hardware local ([ADR-003](architecture/adr/003-apagado-seguro-en-controlador.md)). Un monolito en capas tradicional (Alternativa A) puede cumplir la función de riego, pero mezcla el control de válvulas con el resto de la lógica compartida, poniendo en riesgo la criticidad de la protección.

---

### 3. Reescriba el requisito "el sistema debe ser seguro" como un escenario de atributo de calidad de seis partes.

**Respuesta:**  
Aplicando la plantilla formal de seis partes de Bass, Clements y Kazman (2021), el enunciado vago "el sistema debe ser seguro" se especifica para *ChacraSmart Majes* protegiendo los datos de agricultores y el acceso a los actuadores físicos:

| Parte | Definición | Valor en el Escenario |
|---|---|---|
| **Fuente del estímulo** | ¿Quién o qué genera el evento? | Un usuario externo o no autenticado a través de internet. |
| **Estímulo** | ¿Qué evento o acción ocurre? | Intenta enviar una petición maliciosa al endpoint de accionamiento remoto (`POST /api/valvulas/abrir`) o extraer información de parcelas y teléfonos protegidos por la Ley 29733 (R-07). |
| **Artefacto** | ¿Qué parte del sistema lo recibe? | El proxy inverso Nginx y el middleware de autenticación/autorización de la API Django. |
| **Entorno** | ¿En qué condiciones operativas ocurre? | Operación normal en producción, tráfico cifrado bajo HTTPS/TLS. |
| **Respuesta** | ¿Qué debe hacer el sistema? | El sistema rechaza inmediatamente la petición con código HTTP 401/403, no ejecuta ningún comando en los controladores físicos de campo y registra el intento con IP, timestamp y cabeceras en el registro de auditoría. |
| **Medida de respuesta** | ¿Cómo se verifica objetivamente? | **100 % de 200 intentos de acceso o accionamiento no autorizados son bloqueados** sin accionar ninguna válvula física y el 100 % queda registrado en auditoría. |

---

### 4. Compare el monolito modular y los microservicios en términos de costo, modificabilidad y complejidad operativa. ¿En qué momento convendría migrar de uno a otro?

**Respuesta:**  

| Criterio | Monolito Modular (Alternativa elegida, 4,15) | Microservicios / Eventos (Alternativa descartada, 3,05) |
|---|---|---|
| **Costo económico** | **Bajo:** Se aloja completamente en un único VPS modesto (R-03). Comparte recursos de CPU/RAM, un solo motor PostgreSQL y un proxy Nginx. | **Alto:** Requiere múltiples contenedores o VMs, base de datos dedicada por servicio, brokers de mensajería (RabbitMQ/Kafka) e infraestructura de observabilidad distribuida. |
| **Modificabilidad** | **Alta dentro del monolito:** Módulos de dominio (*Lecturas*, *Riego*, *Válvulas*, *Alertas*, *Dispositivos*) delimitados con interfaces públicas explícitas. Permite añadir nuevos sensores sin alterar otros módulos. | **Máxima e independiente:** Despliegue y ciclo de vida segregado por servicio, permitiendo versionar de forma independiente cada servicio en producción. |
| **Complejidad operativa** | **Baja:** Un solo proceso, un único repositorio, despliegue simple y pruebas directas; compatible con un equipo de 2 developers (R-02) y plazo de 1 mes (R-01). | **Muy alta:** Requiere gestión de redes distribuidas, service discovery, tolerancia a particiones de red y monitoreo distribuido, excediendo la capacidad operativa del equipo. |

**¿En qué momento convendría migrar a microservicios?**  
La migración solo se justificaría si:
1. El número de parcelas y sensores escala a cientos de miles, provocando que la ingesta de telemetría de humedad requiera un escalado horizontal asimétrico independiente de los módulos administrativos.
2. El equipo de desarrollo crece y se divide en múltiples escuadrones autónomos donde la coordinación en un único repositorio se vuelve un cuello de botella organizativo.

---

### 5. ¿Qué ventajas ofrece Diagram as Code frente a herramientas de dibujo como PowerPoint? Mencione al menos tres.

**Respuesta:**  
1. **Versionabilidad y trazabilidad en Git:** Cada modificación del diagrama queda registrada en commits, permitiendo revisiones en Pull Requests y comparativas visuales de diferencias (`git diff`) línea por línea en texto claro.
2. **Mantenibilidad y regeneración sin redibujar:** Modificar un nodo, conector o estilo solo requiere editar una línea de texto (`.mmd`, `.puml`, `.py`); el motor de layout reorganiza automáticamente los elementos sin necesidad de alinear manualmente cajas y flechas.
3. **Automatización en CI/CD y sinergia con IA:** Permite automatizar la compilación a imágenes PNG/SVG mediante pipelines (como GitHub Actions) y facilita que los asistentes de IA propongan, revisen o refactoricen arquitecturas directamente en código ejecutable.

---

### 6. ¿Qué elementos debe contener un ADR y por qué es importante registrar también las alternativas descartadas?

**Respuesta:**  
Siguiendo el estándar de Michael Nygard (2011), un Architecture Decision Record debe contener:
- **Título y Metadatos:** Identificador numérico, estado (*Aceptado*, *Propuesto*, etc.), fecha y autores/decisores.
- **Contexto:** Motivación y drivers que condicionan la decisión (citando RF-, QA- y R-).
- **Alternativas consideradas:** Las opciones viables evaluadas con sus pros y contras.
- **Decisión:** La elección adoptada formulada en voz activa (*"Usaremos..."*).
- **Consecuencias:** Impacto positivo y negativo (riesgos y trade-offs asumidos).

**Importancia de registrar alternativas descartadas:**  
Evita la "amnesia arquitectónica". Si no se registran las razones por las cuales se rechazó una opción (por ejemplo, por qué no se usó MQTT o por qué no se cerraba la válvula desde la nube), futuros ingenieros podrían volver a proponer esas mismas ideas sin conocer las restricciones reales (intermitencia de red R-04 o presupuesto R-03) que ya las invalidaron.

---

### 7. Describa un caso de esta práctica en el que la IA haya generado una propuesta incorrecta o sesgada. ¿Cómo lo detectaron?

**Respuesta:**  
En la propuesta inicial para el caso *ChacraSmart Majes* ([`matriz-decision.md`](architecture/matriz-decision.md) §5.1 y §5.3), la IA propuso que ante la pérdida de conexión a internet mientras una válvula está regando, *"el servidor en la nube detecta la desconexión y envía la orden de cierre a la válvula"*.

**Cómo lo detectamos:**  
El equipo analizó lógicamente la propuesta contra las restricciones del caso: la restricción R-04 establece que en las parcelas de Majes la **conexión es intermitente**. Si se cae la red celular o el enlace satelital, **ningún paquete o comando puede viajar desde el servidor hacia la válvula física**. Asumir que el servidor puede cerrar la válvula sin conexión es una imposibilidad física y un fallo crítico contra el atributo de *safety* (QA-01).  
Se corrigió definiendo en el [ADR-003](architecture/adr/003-apagado-seguro-en-controlador.md) que cada orden de riego debe viajar con un parámetro obligatorio de duración máxima, de modo que el **controlador de campo ejecuta el cierre autónomamente mediante un temporizador local**, garantizando la falla segura sin depender de la conectividad.

---

### 8. ¿Qué riesgos éticos y de confidencialidad existen al usar asistentes de IA para diseñar la arquitectura de un sistema real?

**Respuesta:**  
1. **Fuga de datos confidenciales y normativos:** Subir detalles sobre ubicaciones de predios, teléfonos de productores o esquemas internos de red a modelos comerciales externos vulnera la privacidad y normativas como la Ley 29733 de Protección de Datos Personales. En esta práctica, los prompts se anonimizaron estrictamente sin incluir datos privados.
2. **Responsabilidad profesional no delegable en sistemas críticos (*safety*):** En sistemas con impacto en el mundo físico (como el control de válvulas agrícolas donde un error puede arruinar cultivos por inundación o sequía), la IA no asume responsabilidad legal ni ética. Los ingenieros deben verificar críticamente y probar mediante código cada supuesto generado.
3. **Sesgo hacia arquitecturas sobredimensionadas (*hype*):** Los modelos tienden a sugerir microservicios, brokers complejos o servicios en la nube costosos. En proyectos reales con presupuesto limitado, adoptar estas propuestas acríticamente encarece los costos y puede llevar el proyecto al fracaso operativo.
