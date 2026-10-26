# ADR-005: Patrones de diseño en el módulo de válvulas y riego

- Estado: Aceptado
- Fecha: 2026-10-24
- Decisores: Quenta Ahumada Paulo Estefano, Kevin Joel Callo Ccagiavilca

## Contexto
El flujo crítico `ejecutar_orden_riego()` y `cerrar_valvula()` presentaba una complejidad ciclomática de 25 y 15 respectivamente (rango D y C en radon), violando el principio de responsabilidad única (SRP), abierto/cerrado (OCP) e inversión de dependencias (DIP). Cada nuevo actuador de válvula físico (RainBird, Hunter, Tuya) u algoritmo agronómico (goteo, aspersión, deficitario) exigía modificar el código existente mediante escaleras `if/elif` con bucles de reintento duplicados. Asimismo, el ciclo de vida de la válvula se controlaba con cadenas primitivas susceptibles a transiciones ilegales, y la salida del componente de IA generativa no estaba aislada, arriesgando sugerencias de sobre-riego que violarían la seguridad física y protección de recursos hídricos en Majes (QA-01 / ADR-003).

## Alternativas consideradas
1. **Alternativa A (Monolito condicional mantenido):** Conservar los métodos con sentencias `if/elif` y refactorizar únicamente extrayendo funciones auxiliares privadas.
   * *Desventaja:* Mantiene el acoplamiento estricto, no resuelve la extensibilidad (OCP) y obliga a recompilar/redesplegar el servicio ante cualquier nuevo hardware.
2. **Alternativa B (Sobrediseño exhaustivo / "Patternitis"):** Aplicar todos los patrones GoF disponibles (Abstract Factory, Singleton, Visitor, Memento, Interpreter y evaluación con LLM-as-a-judge).
   * *Desventaja:* Multiplica la complejidad accidental y las líneas de código innecesariamente para un MVP de 1 mes de plazo.
3. **Alternativa C (Patrones GoF específicos guiados por olores y pruebas - Seleccionada):** Aplicar únicamente los patrones que resuelven olores medibles con radon y demostrables mediante pruebas automatizadas.

## Decisión
Usaremos la siguiente arquitectura basada en patrones GoF y principios SOLID:
1. **Strategy + Adapter + Factory para Actuadores y Políticas:**
   - Se crea el puerto `ControladorValvula` con adaptadores específicos (`AdaptadorRainBird`, `AdaptadorHunter`, `AdaptadorTuya`) y la fábrica dinámica `FabricaControladores`.
   - Se encapsulan los algoritmos agronómicos en `PoliticaRiego` (`PoliticaGoteo`, `PoliticaAspersion`, `PoliticaDeficitarioMajes`) resueltos por `FabricaPoliticas`.
2. **State para el Ciclo de Vida de la Válvula:**
   - Se implementa `EstadoValvulaBase` con subclases concretas (`EstadoCerrada`, `EstadoAbriendo`, `EstadoAbierta`, `EstadoCerrando`, `EstadoFalla`). Se prohíben todas las transiciones inválidas y se garantiza el estado terminal de falla segura (QA-01 / ADR-003).
3. **Observer para Eventos de Campo:**
   - Se implementa `PublicadorEventos` con suscriptores independientes (`NotificadorAgricultorSMS`, `MonitorAuditoriaIoT`, `MonitorTelemetria`), eliminando cadenas de texto manuales en el servicio.
4. **Decorator para Responsabilidades Transversales:**
   - `ConReintentos` envuelve transparentemente cualquier actuador para reintentar hasta 3 veces ante `TimeoutError`.
   - `ConCache` envuelve al proveedor de IA para evitar pagar dos veces por el mismo prompt.
5. **Command para Órdenes de Riego:**
   - `ComandoAbrirValvula` y `ComandoCerrarValvula` ejecutados a través de `InvocadorRiego`, preservando el historial de órdenes para auditoría.
6. **Chain of Responsibility para Guardrails de IA:**
   - Cadena determinista de 3 guardrails (`GuardrailMaximoRiego`, `GuardrailConsistenciaHumedad`, `GuardrailLenguajeCampesino`) para filtrar las respuestas del LLM antes de enviarlas al agricultor.

Se rechazan explícitamente:
- **Singleton:** Rechazado para el controlador de campo por introducir estado global y acoplamiento oculto.
- **LLM-as-a-judge:** Rechazado por costo, latencia y falta de determinismo en un sistema de control físico.
- **Abstract Factory:** Rechazado por sobreingeniería innecesaria en el alcance del MVP.

## Consecuencias
- **Positivas:**
  - Reducción drástica de la complejidad ciclomática máxima de 25 a 5 y promedio de 10.16 a 2.16 (100% en Rango A de Radon).
  - Cumplimiento total del Principio Abierto/Cerrado (OCP): se demostró agregar el actuador `ESP32_MAJES` y la política `MICROASPERSION` sin modificar una sola línea de `ServicioRiego`.
  - Seguridad crítica (QA-01) garantizada tanto en el hardware (State fail-closed y reintentos) como en la IA (guardrails deterministas).
  - Cobertura total de pruebas: 33 pruebas unitarias y de caracterización pasando en 0.12s.
- **Negativas / riesgos asumidos:**
  - Crecimiento del código fuente de 159 a 561 SLOC y división en 7 módulos, lo que incrementa el número de clases y la indirección mental para nuevos desarrolladores.
  - El equipo debe mantener disciplina en el registro de nuevas estrategias en las fábricas en lugar de reintroducir bloques `if/elif`.
