# ADR-002: Usar HTTP para la comunicación entre el controlador de campo y el servidor

- **Estado:** Aceptado
- **Fecha:** 2026-10-04
- **Decisores:** Quenta Ahumada Paulo Estefano, Kevin Joel Callo Ccagiavilca

---

## Contexto

Los controladores de campo envían lecturas de humedad (RF-01) y reciben órdenes de riego (RF-03, RF-04) en parcelas con conexión intermitente (R-04). El equipo es de 2 developers con experiencia en Python/Django (R-02), el plazo es de 1 mes (R-01) y el presupuesto es de un solo VPS (R-03). El atributo crítico es fiabilidad/protección (QA-01) — la protección de válvulas **no depende** de este protocolo, sino del temporizador local (ADR-003).

## Alternativas consideradas

1. **HTTP (REST):** el controlador envía lecturas con POST y consulta órdenes pendientes periódicamente. No requiere componentes adicionales.
2. **MQTT con broker:** envío de órdenes con menor latencia; requiere instalar, operar y asegurar un broker adicional.

## Decisión

**Usaremos HTTP:** el controlador envía sus lecturas y consulta periódicamente las órdenes pendientes. Guarda las lecturas localmente si no hay conexión y las envía al recuperarla.

## Consecuencias

**Positivas**
- Sin componentes extra; coherente con monolito modular y experiencia del equipo (R-01, R-02, R-03).
- Simple de probar y depurar.
- Funcionamiento predecible con conectividad intermitente (R-04).

**Negativas / riesgos**
- Órdenes llegan con retraso igual al intervalo de consulta.
- Mayor consumo de datos vs MQTT.  
  La seguridad de las válvulas **no depende** de este retraso (ADR-003).