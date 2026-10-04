# ADR-003: Aplicar el apagado seguro en el controlador de campo con temporizador local

- **Estado:** Aceptado
- **Fecha:** 2026-10-04
- **Decisores:** Quenta Ahumada Paulo Estefano, Kevin Joel Callo Ccagiavilca

---

## Contexto

El atributo crítico es la fiabilidad y protección (QA-01): si se pierde la conexión, ninguna válvula debe quedar abierta más del tiempo programado. Las parcelas tienen conexión intermitente (R-04). Las órdenes de apertura vienen de la programación de riego (RF-03) o del control remoto (RF-04).

## Alternativas consideradas

1. **Cierre decidido solo por el servidor:** el servidor envía la orden de cierre al terminar el tiempo.
2. **Temporizador local en el controlador:** cada orden de apertura incluye una duración máxima y el controlador cierra la válvula por sí solo al cumplirse.

## Decisión

**Usaremos el temporizador local en el controlador:** toda orden de apertura incluirá una duración máxima y el controlador cerrará la válvula por sí solo, registrando el evento para informarlo al recuperar la conexión.

## Consecuencias

**Positivas**
- Se cumple QA-01 aunque se pierda la conexión (cierre no depende de la red).
- Diseño simple de explicar y de probar con cortes de red simulados.

**Negativas / riesgos**
- El controlador necesita lógica más compleja y un temporizador confiable.
- Debe probarse comportamiento ante reinicios o cortes de energía del dispositivo.