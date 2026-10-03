# Drivers arquitectónicos — EcoRecicla AQP

> Lab 04 · Construcción de Software · EPIS-UNSA · 2026-B
> Caso 10 de la guía. Este documento define **qué** debe guiar la arquitectura, **antes** de elegir cómo construirla.

Los drivers arquitectónicos son los tres tipos de factores que condicionan las decisiones (Bass, Clements y
Kazman, 2021, cap. 1; ISO/IEC/IEEE 42010:2022): **requisitos funcionales** clave, **atributos de calidad** y
**restricciones** del proyecto. De aquí salen las decisiones arquitectónicas, que se documentan en
[ADR-001](adr/001-estilo-arquitectonico.md).

---

## 1. Requisitos funcionales clave

Parten de la columna "Funcionalidades del MVP" del caso 10 y se completan con los que el enunciado implica
para que el sistema sea coherente (p. ej. sin *registro de peso* no hay *reporte de toneladas*).

| ID    | Requisito funcional                                                                              | Actor         | Prioridad | Módulo        |
|-------|--------------------------------------------------------------------------------------------------|---------------|-----------|---------------|
| RF-01 | El vecino **solicita** el recojo de residuos reciclables indicando su dirección y tipo de residuo | Vecino        | Alta      | Solicitudes   |
| RF-02 | El reciclador **consulta su ruta del día** por distrito y orden de atención                     | Reciclador    | Alta      | Rutas         |
| RF-03 | El reciclador **confirma el recojo y registra el peso** de los residuos recolectados            | Reciclador    | Alta      | Solicitudes   |
| RF-04 | El vecino **acumula y canjea puntos** por sus recojos según las reglas vigentes                | Vecino        | Media     | Puntos/Canjes |
| RF-05 | La municipalidad **consulta el reporte de toneladas recicladas** por distrito y por mes        | Municipalidad   | Alta      | Reportes      |
| RF-06 | La municipalidad **administra distritos y reglas de puntos** (alta, edición y vigencia)        | Municipalidad   | Alta      | Distritos/Reglas |
| RF-07 | El vecino **recibe aviso por WhatsApp** del recojo programado y del recojo confirmado           | Vecino        | Media     | Notificaciones|

**Nota de cobertura:** RF-03 es la fuente de verdad de RF-05; RF-06 es el módulo que materializa el atributo
crítico (QA-01). Los siete requisitos se reparten entre seis módulos en el diagrama E3, donde **cada módulo
cubre al menos un RF** (requisito de la lista de verificación de E3).

---

## 2. Atributos de calidad (ordenados por prioridad)

El orden es deliberado: el atributo crítico del caso es el **1.º** y es el que pesa más en la matriz de
decisión (E2, 30 %).

| # | Atributo              | Por qué importa en este caso                                                                                                                                   | Fuente |
|---|-----------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------|
| 1 | **Modificabilidad**   | **Atributo crítico.** La municipalidad va a *sumar distritos* y *cambiar reglas de puntos* con frecuencia (RF-06). Con solo 2 developers no hay personal para re-integrar módulos ajenos, así que cada cambio debe quedar contenido en el módulo que lo origina. | Dato medible del caso 10 |
| 2 | **Capacidad de interacción** | Vecinos y recicladores usan celulares de gama baja y tienen poca experiencia digital; también los recicladores trabajan de pie, al sol, con una mano ocupada.                  | Contexto del caso |
| 3 | **Fiabilidad**        | Los puntos se acreditan al confirmar un recojo (RF-03 → RF-04). Un punto acreditado dos veces o perdido **destruye la confianza** de los vecinos y el programa deja de funcionar.    | RF-03, RF-04 |
| 4 | **Rendimiento**       | La ruta del día (RF-02) y el reporte de toneladas (RF-05) se consultan a diario en campo y en oficina; una espera larga hace que el reciclador abandone el uso.                  | RF-02, RF-05 |
| 5 | **Seguridad**         | Se almacenan datos personales de los vecinos (dirección de domicilio, Ley 29733, R-04). Un vecino no debe poder ver ni los recojos ni los puntos de otro.                   | R-04, RF-01 |

---

## 3. Restricciones

R-01 y R-02 son **obligatorias** por la guía. Las demás se derivan del enunciado del caso y de las
"condiciones comunes" (plazo de 1 mes, equipo de hasta 3 developers con las tecnologías que ya dominan,
presupuesto bajo con servicios de pago justificados).

| ID   | Tipo        | Restricción                                                                                              | Implicación arquitectónica                                    |
|------|-------------|----------------------------------------------------------------------------------------------------------|---------------------------------------------------------------|
| R-01 | Plazo       | El MVP debe estar **en producción en 1 mes**                                                            | Obliga a un estilo simple y a un despliegue único             |
| R-02 | Equipo      | **2 developers**: Quenta Ahumada Paulo Estefano y Kevin Joel Callo Ccagiavilca. Dominan **Python / Django** (stack principal) y cuentan con C++, Java, Node y Angular | Descarta stacks que el equipo no domina; favorece Django |
| R-03 | Presupuesto | Presupuesto bajo: **un solo VPS**. Todo servicio de pago debe justificarse explícitamente                   | Un solo servidor y una sola base de datos                     |
| R-04 | Normativa   | **Ley 29733** de protección de datos personales (domicilios de los vecinos)                              | Autorización y minimización de datos personales               |
| R-05 | Tecnología  | Debe funcionar en **celulares de gama baja con conexión móvil limitada (3G)**                              | Favorece una PWA ligera; descarta apps nativas pesadas        |
| R-06 | Integración | La integración con **WhatsApp Business API** es obligatoria para los avisos (RF-07) y **depende de un tercero** | Requiere un adaptador aislado, con reintentos y degradación   |

> **R-01, R-02 y R-03 son las restricciones que más condicionan la arquitectura.** Con solo 2 developers, el
> plazo de 1 mes y un único VPS, la capacidad operativa del equipo es el factor más restrictivo del caso:
> cualquier estilo que exija operar varios despliegues queda descartado de entrada, sin importar cuán bueno
> sea en modificabilidad.

---

## 4. Escenarios de atributos de calidad

Formato de seis partes de Bass et al. (2021). Los tres primeros atributos son **distintos entre sí** y el
primero es el crítico, como exige E1. QA-04 es un refuerzo del escenario de seguridad pedido en el
cuestionario IV.3.

| ID    | Atributo                   | Fuente                              | Estímulo                                                                 | Entorno                              | Artefacto                          | Respuesta                                                                                | Medida                                                              |
|-------|----------------------------|-------------------------------------|--------------------------------------------------------------------------|--------------------------------------|------------------------------------|------------------------------------------------------------------------------------------|---------------------------------------------------------------------|
| QA-01 | **Modificabilidad**        | Municipalidad                         | Solicita **dar de alta un distrito nuevo** y una **regla de puntos** nueva | Fase de desarrollo                   | Módulos Distritos/Reglas y Puntos    | El distrito y la regla se incorporan **sin editar ningún módulo ajeno**; los demás módulos siguen funcionando sin cambios | **≤ 2 días-persona** y **0 archivos modificados** fuera de Distritos/Reglas y Puntos |
| QA-02 | Capacidad de interacción   | Vecino con celular de gama baja     | Solicita un recojo                                                       | Señal 3G intermitente, pantalla de 5" | PWA (interfaz de Solicitudes)       | El sistema registra la solicitud con el mínimo de pasos y confirma con un mensaje explícito | Solicitud completa en **≤ 4 toques** y **≤ 60 s**                                  |
| QA-03 | Fiabilidad                 | Reciclador                          | Confirma un recojo y **pulsa dos veces** por error de conexión            | Operación normal                     | Módulo Puntos y Canjes              | Los puntos del recojo se acreditan **exactamente una vez**                                  | **0 acreditaciones duplicadas** en **1000 confirmaciones** simuladas                  |
| QA-04 | Seguridad                  | Usuario **no autenticado**          | Intenta consultar la lista de recojos y el saldo de puntos de otro vecino | Operación normal                     | API del módulo Solicitudes y Puntos | Se **rechaza** la respuesta y se **registra** el intento con usuario, IP y fecha              | **100 % de 200 intentos** de acceso no autorizado **rechazados y registrados**        |

### Cómo se verifica cada uno (para que un escenario sea comprobable, no declarativo)

| ID    | Procedimiento de verificación                                                                                    |
|-------|---------------------------------------------------------------------------------------------------------------------|
| QA-01 | En una rama de prueba se agrega un distrito y una regla de puntos; se cuenta tiempo elapsed y se ejecuta `import-linter`/revisión de PR para listar los archivos tocados fuera de sus módulos. |
| QA-02 | Prueba instrumentada: se registra el número de toques hasta la confirmación y el tiempo hasta la respuesta del servidor, con la PWA en emulación de red 3G y CPU ralentizada.              |
| QA-03 | Script de prueba que confirma 1000 recojos con doble envío y verifica que la suma de puntos acreditados sea exactamente igual a la de los 1000 recojos registrados.                        |
| QA-04 | Script que intenta 200 accesos con el ID de otro vecino y comprueba respuesta 403/404 en el 100 % de los casos y la existencia de la fila de auditoría correspondiente.          |

---

## 5. Referencias

- Bass, L., Clements, P. y Kazman, R. (2021). *Software Architecture in Practice* (4.ª ed.). Addison-Wesley. — drivers, escenarios de seis partes.
- ISO/IEC/IEEE 42010:2022 — descripción de arquitectura.
- ISO/IEC 25010:2023 — modelo de calidad del producto (características: eficiencia de desempeño, capacidad de interacción, fiabilidad, seguridad, mantenibilidad/flexibilidad).
- Nygard, M. (2011). *Documenting Architecture Decisions*. — ADR.
- Meta for Developers — *Pricing on the WhatsApp Business Platform* (verificado el 03/10/2026): https://developers.facebook.com/documentation/business-messaging/whatsapp/pricing — base de R-06 y de la corrección documentada en [matriz-decision.md](matriz-decision.md).