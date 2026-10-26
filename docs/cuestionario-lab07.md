# Cuestionario Oficial — Laboratorio 07: Refactorizar hacia Patrones de Diseño con IA

> **Asignatura:** Construcción de Software · EPIS-UNSA · Semestre 2026-B  
> **Caso 09:** ChacraSmart Majes (Riego Inteligente con Falla Segura)  
> **Grupo 04:** Quenta Ahumada Paulo Estefano y Kevin Joel Callo Ccagiavilca  
> **Fecha:** 24 de Octubre de 2026  

---

### 1. ¿Qué diferencia hay entre un patrón arquitectónico (Laboratorio 04) y un patrón de diseño? Dé un ejemplo de cada uno en su caso.

**Respuesta:**  
- **Diferencia de escala y nivel de abstracción:** Un **patrón arquitectónico** (Lab 04) define la estructura global del sistema: organiza subsistemas de alto nivel, capas, contenedores de despliegue y protocolos de comunicación física entre ellos, determinando atributos de calidad a gran escala (seguridad de hardware, tolerancia a fallos de red y disponibilidad). Por el contrario, un **patrón de diseño** (Lab 07 / GoF) opera a nivel microestructural dentro de un subsistema o módulo: resuelve problemas recurrentes de acoplamiento entre clases, instanciación de objetos, variación de algoritmos y adherencia a los principios SOLID sin alterar la topología de la arquitectura.
- **Ejemplo de Patrón Arquitectónico en ChacraSmart (Lab 04):** *Arquitectura Hexagonal (Puertos y Adaptadores, ADR-001)* combinada con *Broker de Mensajería MQTT (ADR-002)* y *Falla Segura en Controlador de Campo (ADR-003)*. Esta arquitectura a nivel de sistema desacopla el núcleo de dominio de la infraestructura de telecomunicaciones y garantiza que, ante la pérdida total de conexión con el servidor en la nube, el temporizador local del controlador cierre físicamente la válvula de forma autónoma.
- **Ejemplo de Patrón de Diseño en ChacraSmart (Lab 07):** *Patrón State* en la entidad `Valvula` (`estados.py`) y *Strategy* en `PoliticaRiego` (`politicas.py`). Ambos operan internamente dentro del proceso Python de `valvulas_riego`: State sustituye sentencias condicionales dispersas por objetos polimórficos de estado, y Strategy encapsula fórmulas agronómicas sin afectar la arquitectura de contenedores ni el despliegue del sistema.

---

### 2. Explique con su código cómo Strategy materializa el principio abierto/cerrado. ¿Qué tuvo que modificar para agregar una variante nueva?

**Respuesta:**  
- **Materialización de OCP:** El principio Abierto/Cerrado establece que una entidad debe estar abierta a la extensión pero cerrada a la modificación. En la versión "antes" (`src/valvulas_riego/antes/servicio.py`), cada nueva política de riego exigía abrir y modificar el método `ejecutar_orden_riego()` agregando ramas `if/elif` (`politica == 'GOTEO'`, `'ASPERSION'`, etc.), elevando la complejidad ciclomática a 25. Con Strategy (`politicas.py`), se definió la interfaz abstracta `PoliticaRiego` con el método `calcular_duracion(duracion_min, humedad)`. El servicio `ServicioRiego` ahora depende únicamente de esta abstracción.
- **¿Qué se tuvo que modificar para agregar una variante nueva?** **Absolutamente NADA en el código existente de `ServicioRiego`**. Como se demostró formalmente en la prueba `test_open_closed_nueva_politica_riego_sin_modificar_servicio` en `tests/test_patrones.py`, para incorporar la nueva variante `MICROASPERSION` únicamente se requirió:

```python
# 1. Extender la abstracción creando la nueva clase (sin tocar ServicioRiego)
class PoliticaMicroaspersion(PoliticaRiego):
    nombre = "MICROASPERSION"
    def calcular_duracion(self, duracion_solicitada_min: int, humedad_suelo: float) -> int:
        return int(duracion_solicitada_min * 0.7)

# 2. Registrar la nueva estrategia en la fábrica en tiempo de ejecución
fabrica_pol.registrar("MICROASPERSION", PoliticaMicroaspersion)

# 3. El servicio la consume inmediatamente:
servicio.ejecutar_orden_riego(valvula, "RAINBIRD", 30, politica_tipo="MICROASPERSION")
```

---

### 3. ¿En qué se diferencian Adapter y Decorator si ambos "envuelven" un objeto?

**Respuesta:**  
Aunque ambos patrones utilizan composición para envolver a un objeto interno, difieren completamente en su propósito y en las interfaces que exponen al cliente:
1. **Patrón Adapter (Intención: compatibilidad de interfaces incompatibles):** El objeto envuelto (*Adaptee*) posee una interfaz externa y tipos de datos incompatibles con los del sistema. El Adapter implementa la interfaz esperada por el cliente (*Target*) y traduce las llamadas hacia el Adaptee. Cambia la interfaz para que dos sistemas dispares puedan interoperar.
2. **Patrón Decorator (Intención: adición transparente de responsabilidades):** El decorador implementa exactamente la **MISMA** interfaz que el objeto que envuelve (*Component*). No traduce ni altera firmas; su propósito es inyectar dinámicamente un comportamiento transversal (reintentos, caché, auditoría, control de tiempos) de forma transparente para el cliente.
- **Ejemplificación en ChacraSmart Majes:**
  - *Adapter (`AdaptadorHunter`):* Envuelve a `HunterProC_SDK`. El SDK opera en **segundos** y devuelve tuplas `(bool, "ACK")`; el adaptador traduce y expone la interfaz `ControladorValvula` que opera en **minutos** y retorna objetos `ResultadoOperacion`.
  - *Decorator (`ConReintentos`):* Envuelve a cualquier `ControladorValvula` e implementa `ControladorValvula`. No modifica unidades; intercepta `TimeoutError` y reintenta la llamada hasta 3 veces de forma transparente.

---

### 4. ¿Por qué el patrón State es la implementación natural de un diagrama de máquina de estados? ¿Qué ganó frente a usar condicionales?

**Respuesta:**  
- **Correspondencia isomórfica con el modelo formal UML:** Un diagrama de máquina de estados (`estados-valvula.mmd`) modela formalmente nodos de estado y transiciones dirigidas activadas por eventos. El patrón State materializa esta definición de forma uno a uno: cada estado del diagrama se convierte en una clase concreta (`EstadoCerrada`, `EstadoAbriendo`, `EstadoAbierta`, `EstadoCerrando`, `EstadoFalla`) y cada transición se modela como un método polimórfico (`abrir`, `confirmar_apertura`, `cerrar`, `confirmar_cierre`, `fallar_cierre_seguro`). La flecha de transición se implementa mediante `valvula.cambiar_a(NuevoEstado())`.
- **Ganancias directas frente al uso de condicionales (if/elif):**
  1. *Principio Fail-Closed y Robustez:* La clase base `EstadoValvulaBase` prohíbe todas las transiciones lanzando `TransicionEstadoInvalida`. Cada subclase solo habilita explícitamente las transiciones seguras. Cualquier combinación no modelada es bloqueada por diseño.
  2. *Eliminación de Primitive Obsession:* Se erradicaron las cadenas primitivas dispersas (`"CERRADA"`, `"ABIERTA"`) que provocaban bugs tipográficos o estados intermedios inconsistentes.
  3. *Blindaje de Falla Segura (QA-01 / ADR-003):* En la clase `EstadoFalla`, todas las operaciones de apertura o cierre son rechazadas, garantizando que una electroválvula bloqueada en campo permanezca estanca hasta la revisión presencial del técnico.
  4. *Reducción de Complejidad:* El método `ejecutar_orden_riego` pasó de complejidad ciclomática 25 a 3 al transferir la validación de transiciones al objeto de estado.

---

### 5. ¿Por qué son indispensables las pruebas de caracterización antes de refactorizar? Describa un error que sus pruebas detectaron.

**Respuesta:**  
- **Indispensabilidad de las pruebas de caracterización (Feathers / Fowler):** Las pruebas de caracterización no juzgan si el diseño actual es elegante; describen de manera empírica y reproducible el comportamiento observable del sistema existente (casos de éxito, conversiones, excepciones y eventos de salida). Constituyen una red de seguridad indispensable porque, al ejecutarse simultáneamente sobre la versión "antes" y la versión "después" con un fixture parametrizado (`m`), garantizan matemáticamente que el refactor preserva intacto el comportamiento del negocio sin introducir regresiones silenciosas.
- **Error real detectado por las pruebas en nuestro proyecto:** Durante la refactorización de actuadores asistida por IA (Interacción 2 de la Bitácora), la IA generó el `AdaptadorHunter` asumiendo que todos los fabricantes de hardware operaban en minutos, enviando `duracion_min` de forma directa al SDK.  
Al ejecutar `pytest tests/test_comportamiento.py`, la prueba de caracterización `test_riego_hunter_exitoso_con_conversion` **falló inmediatamente en rojo**: el simulador `HunterProC_SDK` requería obligatoriamente la duración en **segundos**. Gracias a la prueba previa, el equipo detectó la discrepancia de inmediato y corrigió el adaptador incorporando la conversión encapsulada `duracion_segundos = duracion_min * 60`. Sin esta prueba, una válvula Hunter real en Majes habría regado únicamente 20 segundos en vez de 20 minutos (1/60 del agua necesaria), arruinando los cultivos.

---

### 6. ¿Qué patrón propuso la IA que ustedes rechazaron y por qué? ¿Qué es la "patternitis"?

**Respuesta:**  
- **Patrones propuestos por la IA rechazados por el equipo:**
  1. *Rechazo de Singleton para el Controlador de Válvulas:* La IA propuso implementar `ControladorValvula` como Singleton para *"evitar colisiones de hardware"*. Se rechazó porque introduce acoplamiento global oculto, viola la regla de oro de la guía (*"no introduzcas Singleton ni estado global"*) y destruye la testabilidad paralela al impedir inyectar mocks/fakes con fallas programadas (`fallas=2`). Se reemplazó por Inyección de Dependencias gestionada por `FabricaControladores`.
  2. *Rechazo de LLM-as-a-judge:* La IA propuso auditar la salida del LLM con un segundo LLM. Se rechazó por duplicar costos, agregar más de 2 segundos de latencia y carecer de determinismo. Se adoptó una cadena determinista de Guardrails (`Chain of Responsibility`).
- **¿Qué es la 'patternitis'?** La *patternitis* (o sobrediseño compulsivo por patrones) es el antipatrón de diseño consistente en sobrecargar una solución introduciendo la mayor cantidad posible de patrones GoF (Visitor, Memento, Interpreter, Abstract Factory, etc.) sin que existan olores de código reales ni variaciones de negocio que los justifiquen. Produce una sobreingeniería nociva (*"accidental complexity"*): multiplica exponencialmente las líneas de código (en nuestra kata adversaria aumentó a 1,240 SLOC), divide la lógica en decenas de clases microscópicas y eleva la carga cognitiva para el equipo. Los patrones deben ser la respuesta a un olor demostrado, no un fin en sí mismos.

---

### 7. ¿Por qué se debe tratar la salida de un LLM como dato no confiable? Describa los guardrails de su caso y qué protegen.

**Respuesta:**  
- **Tratamiento de la IA como dato no confiable (Zero-Trust Output):** Los Modelos de Lenguaje (LLMs) son componentes estocásticos y no deterministas: ante prompts idénticos o variaciones contextuales pueden alucinar datos falsos con alta convicción, equivocarse en magnitudes numéricas, omitir restricciones de seguridad o ser vulnerables a inyecciones de prompt. En un sistema ciberfísico como ChacraSmart Majes, donde las recomendaciones conllevan la apertura física de electroválvulas en parcelas agrícolas, un error del LLM puede provocar anegamiento de cultivos, marchitamiento por estrés hídrico o sobrecostos energéticos en Majes (QA-01). Por ello, la salida de la IA debe tratarse con la misma desconfianza que una entrada de red no autenticada.
- **Guardrails implementados en nuestro caso (`Chain of Responsibility` en `ia.py`):**
  1. `GuardrailMaximoRiego` *(Seguridad Física QA-01 / ADR-003):* Analiza la respuesta generada buscando recomendaciones de tiempo (ej. *"95 minutos"*). Si el valor supera la `apertura_maxima_min` de la válvula (ej. 60 min), bloquea la salida y lanza `ValueError` impidiendo el sobre-riego físico.
  2. `GuardrailConsistenciaHumedad` *(Integridad de Datos):* Detecta valores de humedad imposibles generados por alucinación (porcentajes negativos como *"-15%"* o superiores al 100%), garantizando consistencia con la telemetría LoRaWAN.
  3. `GuardrailLenguajeCampesino` *(Ética y Veracidad):* Filtra y bloquea promesas comerciales no auditadas o fraudulentas (*"garantizado al 100%"*, *"cero riesgo hídrico"*, *"agua infinita"*), protegiendo la confianza del agricultor.

---

### 8. Según sus métricas, ¿valió la pena el refactor? Argumente con la complejidad ciclomática, las líneas de código y los cambios previstos.

**Respuesta:**  
- **Balance cuantitativo de complejidad y volumen de código:**
  - *Complejidad Ciclomática (`radon cc`):* El método principal `ejecutar_orden_riego` se redujo drásticamente de complejidad **25 (Rango D - Alerta Crítica)** a complejidad **3 (Rango A - Excelente)**, lo que representa una reducción del **88.0%**. El método `cerrar_valvula` se redujo de **15 (Rango C)** a **2 (Rango A)**. La complejidad promedio global de todo el módulo disminuyó de **10.16 (Rango C)** a **2.16 (Rango A)**.
  - *Volumen de Código (`radon raw`):* El servicio orquestador principal redujo su volumen de 159 a 108 SLOC (-32.1%). A nivel global del sistema, el código creció de 159 a 561 SLOC (+252.8%) distribuidos en 7 módulos altamente cohesivos con Responsabilidad Única.
- **Argumentación respecto a los cambios previstos:** El refactor **VALIÓ ABSOLUTAMENTE LA PENA**. Si ChacraSmart Majes fuese un script descartable para una sola parcela con un único actuador que jamás cambiaría, la versión "antes" habría sido suficiente. Sin embargo, en el escenario real de producción agrícola en Majes, se prevé la incorporación continua de hardware de distintos fabricantes (Hunter, RainBird, Tuya, ESP32) y políticas agronómicas variadas (goteo, aspersión, deficitario). Gracias a `Adapter + Factory + Strategy`, agregar una nueva variante se probó que requiere **CERO modificaciones en el servicio**. Además, el patrón `State` blindó la falla segura obligatoria (ADR-003) y la cadena de guardrails garantizó la inocuidad física del componente de IA. El costo en líneas de código e indirección queda plenamente justificado por la robustez, extensibilidad y mantenibilidad demostradas.
