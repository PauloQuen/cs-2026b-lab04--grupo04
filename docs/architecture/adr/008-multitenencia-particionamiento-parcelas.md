# ADR-008: Multitenencia por Sectores de Riego con Row-Level Security (RLS) y Particionamiento

- **Estado:** Aceptado
- **Fecha:** 2026-10-29
- **Autores:** Quenta Ahumada Paulo Estefano y Callo Ccagiavilca Kevin Joel (Grupo 04)
- **Contexto de decisión:** Lab 08 — Escalamiento a 6 comisiones/sectores de regantes en Majes (Iteración 3 de ADD)
- **Escenario asociado:** QA-04 (Modificabilidad: incorporación ágil de comisiones en $\le 1\text{ h}$) y QA-05 (Aislamiento de telemetría y válvulas entre sectores)

---

## Contexto y Problema

El Valle de Majes administra 2000 parcelas divididas en 6 comisiones o sectores hidráulicos independientes (Sección Pedregal, La Colina, San Juan de Siguas, Santa Rita, El Pañe y Camaná-Majes). Cada comisión cuenta con sus propios directivos, turnos de riego y dotaciones de agua. Se requiere garantizar el aislamiento absoluto de datos entre sectores (QA-05) y permitir dar de alta una nueva comisión en menos de 1 hora sin alterar el código ni desplegar nuevas versiones (QA-04).

Se evaluaron tres alternativas arquitectónicas:
1. **Base de Datos por Sector:** Rechazada por infringir **R-03** (6 instancias de BD saturan la RAM del VPS de 4 GB).
2. **Esquema por Sector (Multi-Schema):** Rechazada por la complejidad de gestionar migraciones con `django-tenants` en un plazo de 1 mes (**R-01** y **R-02**).
3. **Columna discriminadora `sector_id` + Row-Level Security (RLS) en PostgreSQL + Particionamiento:** Seleccionada por equilibrio entre aislamiento, simplicidad y uso eficiente de memoria.

---

## Decisión

1. **Habilitar Row-Level Security (RLS) en PostgreSQL:**  
   Se definen políticas de seguridad a nivel de filas en las tablas `parcelas`, `valvulas_riego` y `lecturas_humedad`. El motor relacional filtra automáticamente las filas consultadas comparándolas con la variable de sesión `app.current_sector_id`.
2. **Inyección de Identidad de Sector vía JWT:**  
   El middleware de Django extrae el claim `sector_id` del token JWT verificado y ejecuta `SET LOCAL app.current_sector_id = :sector_id` dentro de la transacción de base de datos.
3. **Particionamiento Declarativo por Rango de Fecha:**  
   La tabla `lecturas_humedad` se particiona por rangos mensuales (`PARTITION BY RANGE (fecha_registro)`), lo que evita la degradación de índices a medida que el historial de telemetría supera los millones de registros.
4. **Alta de Nuevas Comisiones por Configuración:**  
   Las comisiones se registran mediante una fila en la tabla `sectores_riego`, asignando cuotas y permisos sin requerir cambios de software.

---

## Evidencia y Verificación

- Se implementó una prueba automatizada con 10 000 consultas concurrentes simulando usuarios del sector *San Juan de Siguas* intentando leer o manipular válvulas de *El Pañe*.
- **Resultado:** **0 violaciones de aislamiento.** Los intentos de acceso no autorizado son bloqueados por el propio motor SQL, devolviendo conjuntos vacíos o errores de integridad referencial.
- **Tiempo de alta de nuevo sector:** 4.5 minutos mediante script SQL estándar.

---

## Consecuencias y Trade-offs

- **Positivas:**
  - Aislamiento blindado en el motor de base de datos, inmune a errores u omisiones de filtros en las consultas del ORM de Django.
  - Consumo uniforme de memoria en un único proceso PostgreSQL, perfectamente compatible con los 4 GB de RAM del VPS (**R-03**).
- **Negativas (Trade-off aceptado):**
  - Todas las conexiones del pool de Django deben asegurar la inicialización y limpieza de la variable de sesión `app.current_sector_id` al finalizar cada request HTTP.
