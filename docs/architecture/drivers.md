# Drivers arquitectónicos — ChacraSmart Majes

> Lab 04 · Construcción de Software · EPIS-UNSA · 2026-B
> Caso 9 de la guía. Este documento define **qué** debe guiar la arquitectura, **antes** de elegir cómo construirla.

Los drivers arquitectónicos son los tres tipos de factores que condicionan las decisiones (Bass, Clements y
Kazman, 2021, cap. 1; ISO/IEC/IEEE 42010:2022): **requisitos funcionales** clave, **atributos de calidad** y
**restricciones** del proyecto. De aquí salen las decisiones arquitectónicas, que se documentan en
[ADR-001](adr/001-estilo-arquitectonico.md).

---

## 1. Requisitos funcionales clave

Parten de la columna "Funcionalidades del MVP" del caso 9 (riego inteligente con sensores de humedad y válvulas en parcelas de Majes).

| ID    | Requisito funcional                                                                           | Actor     | Prioridad | Módulo                   |
|-------|-----------------------------------------------------------------------------------------------|-----------|-----------|--------------------------|
| RF-01 | El sensor envía lecturas de humedad del suelo                                                 | Sensor    | Alta      | Lecturas de humedad      |
| RF-02 | El agricultor consulta la humedad actual y el histórico de su parcela                         | Agricultor| Media     | Lecturas de humedad      |
| RF-03 | El agricultor programa un riego (parcela, hora y duración)                                    | Agricultor| Alta      | Programación de riego    |
| RF-04 | El agricultor abre o cierra una válvula de forma remota                                       | Agricultor| Alta      | Control de válvulas      |
| RF-05 | El agricultor recibe una alerta por falta de agua                                             | Agricultor| Alta      | Alertas                  |
| RF-06 | El técnico registra parcelas, sensores y válvulas                                             | Técnico   | Media     | Parcelas y dispositivos  |
| RF-07 | El técnico ve el estado de los dispositivos (en línea / fuera de línea)                       | Técnico   | Media     | Parcelas y dispositivos  |

**Nota de cobertura:** Todos los módulos cubren al menos un RF. El módulo **Control de válvulas** es el que materializa el atributo crítico QA-01 (falla segura).

---

## 2. Atributos de calidad (ordenados por prioridad)

El orden es deliberado: el atributo crítico del caso es el **1.º** y es el que pesa más en la matriz de decisión (E2, 30 %).

| # | Atributo                | Por qué importa en este caso                                                                                                                                                     | Fuente |
|---|-------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------|
| 1 | **Fiabilidad y protección (safety)** | **Atributo crítico.** Si se pierde la conexión, ninguna válvula debe quedar abierta más del tiempo programado. La protección debe vivir en el controlador de campo, no en el servidor. | Dato medible del caso 9 (falla segura) |
| 2 | **Capacidad de interacción** | Agricultores con poca experiencia digital y celulares de gama baja.                                                                                                                | Contexto del caso |
| 3 | **Modificabilidad**      | Se prevé agregar nuevos tipos de sensores y reglas de riego, limitando el impacto a los módulos correspondientes.                                                                  | Caso 9 |
| 4 | **Rendimiento**          | Las órdenes de apertura/cierre deben confirmarse rápido para que el control remoto sea útil.                                                                                       | RF-03, RF-04 |

---

## 3. Restricciones

R-01 y R-02 son **obligatorias** por la guía. Las demás se derivan del enunciado del caso 9.

| ID   | Tipo         | Restricción                                                                                              | Implicación arquitectónica                                      |
|------|--------------|----------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------|
| R-01 | Plazo        | El MVP debe estar **en producción en 1 mes**                                                            | Obliga a un estilo simple y a un despliegue único               |
| R-02 | Equipo       | **2 developers**: Quenta Ahumada Paulo Estefano y Kevin Joel Callo Ccagiavilca. Dominan **Python / Django** (stack principal) y cuentan con C++, Java, Node y Angular | Favorece Django; descarta stacks que exigen mayor curva         |
| R-03 | Presupuesto  | Presupuesto bajo: **un solo VPS**. Todo servicio de pago debe justificarse explícitamente                | Un solo servidor, despliegue único                             |
| R-04 | Conectividad | Las parcelas de Majes tienen **conexión intermitente**; el sistema no puede depender de que siempre haya red | Requiere lógica de continuidad local (temporizador en controlador) |
| R-05 | Tecnología   | Debe funcionar en **celulares de gama baja**                                                            | Interfaz ligera (PWA)                                           |
| R-06 | Integración  | Integración con servicio de mensajería (WhatsApp/SMS) para las alertas (RF-05)                          | Adaptador externo aislado                                       |
| R-07 | Normativa    | **Ley 29733** de protección de datos personales: los cultivos, parcelas y teléfonos de los agricultores son datos personales | Minimizar datos almacenados, cifrar en tránsito, informar al agricultor |

> **R-01, R-02, R-03 y R-04 son las restricciones que más condicionan la arquitectura.** Con solo 2 developers, 1 mes, 1 VPS y conectividad intermitente, cualquier estilo que exija operar varios despliegues queda descartado de entrada.

> **Recomendación de hardware (no es una restricción del enunciado).** Si el diseño lo permite, conviene usar
> válvulas **normalmente cerradas**, que se cierran solas al cortar la energía: sería una segunda capa de
> protección *además* del temporizador local de [ADR-003](adr/003-apagado-seguro-en-controlador.md).
> Se deja anotada como recomendación y **no** como requisito, porque el enunciado no lo impone. La diferencia
> importa: un requisito que el equipo se inventa no se puede defender en la sustentación.

---

## 4. Escenarios de atributos de calidad

Formato de seis partes de Bass et al. (2021). Tres atributos distintos; el primero es el crítico.

| ID    | Atributo                  | Fuente                               | Estímulo                                                   | Entorno                       | Artefacto                        | Respuesta                                                                                                       | Medida                                                                                   |
|-------|---------------------------|--------------------------------------|------------------------------------------------------------|-------------------------------|----------------------------------|-----------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------|
| QA-01 | Fiabilidad y protección  | Falla de red entre campo y servidor  | Se pierde la conexión con la válvula abierta               | Riego en curso, parcela rural | Controlador de campo (válvula)   | El controlador cierra la válvula por sí solo al cumplirse el tiempo programado y registra el evento            | **0 válvulas abiertas más de 5 s** sobre el tiempo programado en **100 cortes de red simulados** |
| QA-02 | Capacidad de interacción | Agricultor con poca experiencia digital | Programa un riego                                        | Celular de gama baja, señal 3G | PWA                             | La app permite programar el riego con pocos pasos                                                               | Riego programado en **≤ 4 toques** y **≤ 60 s**                                           |
| QA-03 | Modificabilidad          | Técnico / cooperativa               | Pide agregar un nuevo tipo de sensor                       | Desarrollo                    | Módulos Lecturas y Dispositivos | Se agrega el tipo de sensor sin modificar los demás módulos                                                    | **≤ 3 días-persona** y **0 archivos modificados** fuera de esos módulos                    |

### Cómo se verifica cada uno

| ID    | Procedimiento de verificación                                                                                 |
|-------|--------------------------------------------------------------------------------------------------------------|
| QA-01 | Simulación de 100 cortes de red con válvula abierta: medir tiempo de cierre efectivo vs tiempo programado.     |
| QA-02 | Medición de toques y tiempo en emulación 3G, CPU ralentizada.                                                  |
| QA-03 | En rama de prueba se agrega un tipo de sensor; se cuentan archivos modificados y tiempo invertido.             |

---

## 5. Referencias

- Bass, L., Clements, P. y Kazman, R. (2021). *Software Architecture in Practice* (4.ª ed.). Addison-Wesley.
- ISO/IEC/IEEE 42010:2022 — descripción de arquitectura.
- ISO/IEC 25010:2023 — modelo de calidad del producto (características: fiabilidad, usabilidad, mantenibilidad).
- Nygard, M. (2011). *Documenting Architecture Decisions*. — ADR.