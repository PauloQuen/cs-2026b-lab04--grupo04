# Detección de Olores de Código y Selección de Patrones (E1)

**Proyecto:** ChacraSmart Majes — Construcción de Software 2026-B  
**Módulo:** `valvulas_riego` · **Caso 9:** Riego Inteligente y Válvula con Falla Segura  
**Equipo:** Grupo 04 (Quenta Ahumada Paulo Estefano & Kevin Joel Callo Ccagiavilca)  

---

## 1. Salida de Métricas Iniciales (radon cc) sobre `src/valvulas_riego/antes/servicio.py`

```text
src/valvulas_riego/antes/servicio.py
    M 47:4 ServicioRiego.ejecutar_orden_riego - D (25)
    M 143:4 ServicioRiego.cerrar_valvula - C (15)
    C 29:0 ServicioRiego - C (13)
    M 32:4 ServicioRiego.__init__ - B (6)
    C 20:0 Valvula - A (1)
    M 190:4 ServicioRiego.explicar_recomendacion_ia - A (1)

6 blocks (classes, functions, methods) analyzed.
Average complexity: C (10.16)
SLOC: 159 líneas de código
```

---

## 2. Matriz de Olores Detectados y Propuesta de Patrones (Prompt IA 1)

A continuación se detallan los 6 olores principales detectados en la versión monolítica, la evaluación del principio SOLID violentado y la deliberación crítica del equipo de desarrollo:

| # | Olor de código detectado (Fowler / Kerievsky) | Ubicación en el código | Principio SOLID comprometido | Patrón propuesto por la IA | Decisión del equipo | Justificación técnica de la decisión |
|---|-----------------------------------------------|------------------------|------------------------------|----------------------------|---------------------|---------------------------------------|
| **1** | **Switch Statements / Long Method:** Escalera `if/elif` por marca de actuador (`RAINBIRD`, `HUNTER`, `TUYA`) que crece con cada nuevo fabricante de hardware. | `ejecutar_orden_riego()` y `cerrar_valvula()` | **O — Abierto/Cerrado (OCP)** y **D — Inversión de Dependencias (DIP)** | **Adapter + Factory** | **ACEPTADO** | Se define el puerto `ControladorValvula` (interfaz común) y adaptadores para cada SDK específico (traduciendo unidades como segundos vs minutos y diccionarios a objetos de dominio). La fábrica desacopla la instanciación. |
| **2** | **Algoritmos condicionales entrelazados:** Cálculo de tiempo y dosis de agua según el tipo de riego (`GOTEO`, `ASPERSION`, `DEFICITARIO`) codificado en bloques `if/elif` dentro del servicio. | `ejecutar_orden_riego()` líneas 67–77 | **O — Abierto/Cerrado (OCP)** y **S — Responsabilidad Única (SRP)** | **Strategy** | **ACEPTADO** | Permite encapsular cada cálculo agronómico en una clase de estrategia (`PoliticaRiego`). Agregar un nuevo tipo de riego (ej. *Microaspersión Majes*) no modificará el servicio. |
| **3** | **Duplicated Code (Código duplicado):** Bloques de bucle con reintentos (`for intento in range(3): try... except TimeoutError`) replicados de forma idéntica para RainBird, Hunter y Tuya. | `ejecutar_orden_riego()` y `cerrar_valvula()` | **S — Responsabilidad Única (SRP)** y principio DRY | **Decorator** (`ConReintentos`) | **ACEPTADO** | La resiliencia ante timeouts es una responsabilidad transversal del canal de comunicación, no del controlador ni del servicio de negocio. Un decorador envuelve cualquier actuador sin duplicar código. |
| **4** | **Primitive Obsession & State Machine in Conditional:** El ciclo de vida de la válvula se gestiona mediante cadenas de texto (`"CERRADA"`, `"ABIERTA"`, `"FALLA"`) con validaciones y transiciones dispersas en sentencias `if`. | `Valvula` y `ServicioRiego` | **S — Responsabilidad Única (SRP)** y **L — Sustitución de Liskov (LSP)** | **State** | **ACEPTADO** | Implementa directamente la máquina de estados formal del Laboratorio 05 (`estados-valvula.mmd`). Cada estado prohíbe transiciones inválidas y garantiza la falla segura (QA-01 / ADR-003). |
| **5** | **Tight Coupling en Notificaciones:** Inserción manual de cadenas en listas de eventos (`self.eventos.append(...)`) y acoplamiento directo a `ServicioSMSPeru`. | Final de ejecución de órdenes y cierres | **O — Abierto/Cerrado (OCP)** y **D — Inversión de Dependencias (DIP)** | **Observer** (`PublicadorEventos`) | **ACEPTADO** | Desacopla la lógica de riego de los consumidores de eventos (SMS al agricultor, auditoría en base de datos, telemetría IoT). Nuevos suscriptores se agregan dinámicamente. |
| **6** | **Falta de encapsulamiento de invocaciones:** La orden de riego y cierre se ejecuta de forma síncrona y directa sin posibilidad de cola, historial ni reversión segura. | Invocaciones directas en `ejecutar_orden_riego()` | **S — Responsabilidad Única (SRP)** | **Command** | **ACEPTADO** | Modela la orden de riego como un objeto ejecutable con parámetros, hora y duración, facilitando auditoría y control de fallas en campo. |
| **7** | **Acceso global al controlador de campo:** La IA sugirió aplicar un **Singleton** para el gestor de hardware con el argumento de *"evitar que dos hilos abran la misma válvula"*. | Inicialización del servicio | **D — Inversión de Dependencias (DIP)** | **Singleton** | **RECHAZADO** | **Justificación:** El patrón Singleton introduce acoplamiento global oculto, destruye la testabilidad con mocks/fakes en pruebas paralelas y viola las directrices de la guía (Regla 2: *"no introduzcas Singleton ni estado global"*). La concurrencia se controla a nivel de base de datos o cola de mensajes. |
| **8** | **Validación no determinista de IA mediante otro LLM ("LLM-as-a-judge"):** Para el componente de IA (E5), la IA propuso enviar la salida a un segundo modelo para evaluar si la recomendación hídrica era segura. | `explicar_recomendacion_ia()` | Principio de Robustez y Determinismo | **Proxy con LLM Evaluador** | **RECHAZADO** | **Justificación:** Usar un LLM para evaluar a otro LLM duplica el costo y la latencia, y mantiene la falta de determinismo. Para un MVP de producción en 1 mes que controla agua física, la seguridad se garantiza mediante una cadena determinista de reglas (`Chain of Responsibility` con guardrails numéricos basados en `apertura_maxima_min` y rangos agronómicos de Majes). |

---

## 3. Resumen de Decisiones de Arquitectura de Diseño

1. **Patrones Aceptados:**
   - **E2:** `Strategy` (políticas agronómicas) + `Adapter` (controladores físicos de válvulas) + `Factory` (resolución desacoplada).
   - **E3:** `State` (ciclo de vida de la válvula con preservación de falla segura).
   - **E4:** `Observer` (publicador/suscriptor de eventos de campo) + `Decorator` (reintentos ante timeouts y caché de IA) + `Command` (órdenes de riego auditables).
   - **E5:** `Strategy/Adapter` + `Decorator` (Caché) + `Chain of Responsibility` (Guardrails deterministas de seguridad hídrica).
2. **Patrones Rechazados con Justificación:**
   - **Singleton:** Rechazado por acoplamiento global y degradación de pruebas unitarias.
   - **LLM-as-a-judge / Proxy Complejo:** Rechazado por costo, latencia y falta de determinismo en el atributo de calidad crítico de fiabilidad/seguridad física (QA-01).
