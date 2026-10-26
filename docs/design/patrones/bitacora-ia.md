# Bitácora de Asistencia y Co-diseño con Inteligencia Artificial (E7)

**Proyecto:** ChacraSmart Majes — Construcción de Software 2026-B  
**Módulo:** `valvulas_riego` · **Caso 9:** Riego Inteligente y Válvula con Falla Segura  
**Equipo:** Grupo 04 (Quenta Ahumada Paulo Estefano & Kevin Joel Callo Ccagiavilca)  

---

## Directrices de Uso de IA en el Proyecto

Siguiendo el marco metodológico del curso (Sección 1.6 de la guía), se aplicaron los siguientes principios:
1. **La IA propone, el equipo decide y verifica:** Ninguna sugerencia generativa se integró sin revisión manual contra las pruebas y métricas.
2. **Sin secretos en prompts ni repositorios:** Todas las pruebas operan sobre clientes simulados (`ClienteLLMSimulado`, `RainBirdControllerSDK`), sin exponer claves API reales.
3. **Verificación automatizada:** Toda refactorización fue sometida a la red de pruebas de caracterización (`pytest`) y al análisis estático de complejidad ciclomática (`radon`).

---

## Registro de Interacciones

### Interacción 1: Detección Inicial de Olores de Código y Selección de Patrones
* **Fecha:** 21/10/2026
* **Prompt del equipo:**
  > *"Actúa como revisor de código experto en refactorización (Fowler) y patrones GoF. Contexto: analiza `src/valvulas_riego/antes/servicio.py` y la salida de `radon cc -s -a` (complejidad 25 en `ejecutar_orden_riego`). Lista los olores de código detectados, qué patrón GoF resuelve cada olor, el principio SOLID asociado y sugiere qué patrones aplicar."*
* **Propuesta de la IA:**
  La IA identificó 8 olores. Propuso:
  1. *Switch Statements por hardware* → `Adapter` + `Factory`.
  2. *Algoritmos de riego condicionales* → `Strategy`.
  3. *Reintentos duplicados* → `Decorator`.
  4. *Cadenas de texto para estados* → `State`.
  5. *Acoplamiento en avisos SMS* → `Observer`.
  6. *Instanciación y acceso concurrente al hardware* → `Singleton` global.
  7. *Invocación directa de órdenes* → `Command`.
  8. *Validación de salida de IA* → `Proxy` con segundo modelo LLM juez ("LLM-as-a-judge").
* **Verificación del equipo:**
  Se revisaron las 8 propuestas contra las restricciones del proyecto (MVP en 1 mes, fiabilidad crítica QA-01 / ADR-003 y directrices de la guía).
* **Decisión:**
  **6 Aceptadas, 2 Rechazadas.**
  * *Rechazo 1 (Singleton):* Viola la regla 2 de la guía (*"no introduzcas Singleton ni estado global"*), destruye la testabilidad paralela y crea dependencia oculta.
  * *Rechazo 2 (LLM-as-a-judge):* No determinista, costoso y con alta latencia para un sistema que abre electroválvulas reales en campo. Se reemplazó por guardrails deterministas (`Chain of Responsibility`).

---

### Interacción 2: Refactorización de Actuadores y Reintentos (Strategy + Adapter + Decorator)
* **Fecha:** 22/10/2026
* **Prompt del equipo (Prompt IA 2):**
  > *"Aplica ÚNICAMENTE el patrón Strategy + Adapter + Factory al control de actuadores de válvulas en `src/valvulas_riego/actuadores.py`. Convierte los SDKs de RainBird (minutos/JSON), Hunter (segundos/tupla) y Tuya (HTTP) a una interfaz común `ControladorValvula`. No cambies el comportamiento observable; las pruebas de caracterización deben seguir pasando."*
* **Propuesta de la IA:**
  Generó los adaptadores `AdaptadorRainBird`, `AdaptadorHunter`, `AdaptadorTuya` y el decorador `ConReintentos`. Sin embargo, dentro de `AdaptadorHunter.abrir()`, la IA asumió que Hunter recibía minutos y pasó directamente `duracion_min` al método `execute_irrigation()`.
* **Verificación y Detección de Falla con Pruebas:**
  Al ejecutar `pytest tests/test_comportamiento.py`, la prueba `test_riego_hunter_exitoso_con_conversion` falló: el simulador de Hunter esperaba segundos (`duracion_min * 60`).
* **Decisión y Corrección:**
  **Propuesta corregida por el equipo.** Se ajustó la línea dentro del adaptador: `duracion_segundos = duracion_min * 60`. Las pruebas pasaron inmediatamente a verde. La conversión de unidades quedó correctamente encapsulada en el adaptador sin contaminar el dominio.

---

### Interacción 3: Implementación del Patrón State para la Entidad Valvula
* **Fecha:** 22/10/2026
* **Prompt del equipo:**
  > *"Genera la jerarquía del patrón State para la entidad Valvula en `src/valvulas_riego/estados.py` basada exactamente en la máquina de estados de `docs/design/estados-valvula.mmd`: estados CERRADA, ABRIENDO, ABIERTA, CERRANDO, FALLA. La clase base `EstadoValvulaBase` debe prohibir todas las transiciones con `TransicionEstadoInvalida`. Cada subclase debe redefinir solo las transiciones permitidas. Asegura que el estado FALLA sea seguro e irreversible (QA-01 / ADR-003)."*
* **Propuesta de la IA:**
  La IA implementó las 5 clases de estado heredando de `EstadoValvulaBase`. Propuso que `Valvula` delegara sus métodos `abrir()`, `confirmar_apertura()`, `cerrar()`, `confirmar_cierre()` y `fallar_cierre_seguro()`.
* **Verificación del equipo:**
  Se verificó con `tests/test_patrones.py::test_state_impide_transiciones_invalidas` y `test_state_falla_segura_es_terminal`. Se detectó que la IA había omitido el soporte del constructor por string `estado="CERRADA"`, lo que rompía la compatibilidad polimórfica con las pruebas de caracterización del antes.
* **Decisión:**
  **Aceptada con adición:** Se agregó en el `__init__` de `Valvula` un mapeo de inicialización flexible que acepta tanto objetos de estado como cadenas descriptivas, garantizando interoperabilidad del 100%.

---

### Interacción 4: Desacoplamiento de Eventos con Observer y Órdenes con Command
* **Fecha:** 23/10/2026
* **Prompt del equipo:**
  > *"Genera `src/valvulas_riego/eventos.py` con el patrón Observer (`PublicadorEventos` y suscriptores concretos para SMS del agricultor, auditoría IoT y telemetría). Genera también `src/valvulas_riego/comandos.py` con el patrón Command (`ComandoAbrirValvula`, `ComandoCerrarValvula` e `InvocadorRiego`)."*
* **Propuesta de la IA:**
  La IA propuso una arquitectura limpia de eventos y comandos. Incluyó callbacks desacoplados `actualizar(evento, datos)` y un historial de comandos auditables en `InvocadorRiego`.
* **Verificación del equipo:**
  Se verificó que los eventos emitidos coincidieran de forma estricta con los esperados por las pruebas de caracterización (`sms:959123456:Riego iniciado...`, `auditoria:V-01:APERTURA_EXITOSA`).
* **Decisión:**
  **Aceptada.** Se confirmó que agregar nuevos canales de supervisión (como dashboards web) no requirió ninguna modificación en el servicio de aplicación.

---

### Interacción 5: Aislamiento del Componente de IA con Guardrails Deterministas
* **Fecha:** 23/10/2026
* **Prompt del equipo:**
  > *"Diseña `src/valvulas_riego/ia.py` para aislar la función de recomendación de riego al agricultor (columna 4 de la Tabla 7). Aplica Strategy + Adapter (`ProveedorLLM`), Decorator (`ConCache` con diccionario en memoria) y Chain of Responsibility para los guardrails. Los guardrails deben bloquear: (1) recomendaciones de sobre-riego > límite de la válvula (QA-01), (2) porcentajes de humedad imposibles (< 0% o > 100%), (3) lenguaje fraudulento ('garantizado al 100%'). Escribe las pruebas con `ClienteLLMSimulado`."*
* **Propuesta de la IA:**
  La IA implementó `ProveedorLLM`, `ConCache` y la cadena `Guardrail` con los tres eslabones concretos: `GuardrailMaximoRiego`, `GuardrailConsistenciaHumedad` y `GuardrailLenguajeCampesino`.
* **Verificación del equipo:**
  Se probaron prompts con inyecciones adversarias en `tests/test_patrones.py`:
  - Intento de recomendación de 95 min con límite de 60 min -> bloqueado con `ValueError`.
  - Intento con "-15.4%" de humedad -> bloqueado con `ValueError`.
  - Intento con "cero riesgo hídrico garantizado" -> bloqueado con `ValueError`.
  - Intento válido -> respuesta aprobada y cacheada (segunda llamada física omitida).
* **Decisión:**
  **Aceptada.** Se confirmó que el componente de IA es completamente determinista y seguro para la operación agrícola en Majes.

---

### Interacción 6: Generación de Diagramas PlantUML como Código
* **Fecha:** 24/10/2026
* **Prompt del equipo:**
  > *"Genera los diagramas de clases PlantUML con estereotipos de rol (<<Strategy>>, <<Adapter>>, <<Factory>>, <<State>>, <<Decorator>>, <<Observer>>, <<Command>>, <<Chain of Responsibility>>) para cada uno de los patrones aplicados en `docs/design/patrones/`. Asegúrate de que los nombres de métodos y atributos coincidan exactamente con la implementación en Python."*
* **Propuesta de la IA:**
  Generó los 4 archivos `.puml` y el diagrama general `clases.puml` actualizado.
* **Verificación del equipo:**
  Se compararon los nombres de las clases y métodos contra el código real y la salida de `radon`. Se corrigieron discrepancias menores en los parámetros de `ejecutar_orden_riego` y se renderizaron las imágenes a PNG mediante el servicio PlantUML.
* **Decisión:**
  **Aceptada.** Todos los diagramas coinciden al 100% con la base de código verificada.
