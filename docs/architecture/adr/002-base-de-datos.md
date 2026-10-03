# ADR-002: Usar PostgreSQL como base de datos relacional, con un esquema por módulo

- **Estado:** Aceptado
- **Fecha:** 2026-10-03
- **Decisores:** Quenta Ahumada Paulo Estefano, Kevin Joel Callo Ccagiavilca

---

## Contexto

Este ADR se apoya en la decisión de estilo de [ADR-001](001-estilo-arquitectonico.md): un monolito modular en
Django con seis módulos de dominio. La base de datos es la parte de la arquitectura que más caro resulta
cambiar después, porque arrastra el código, los backups y los datos ya capturados.

Los requisitos que presionan al diseño de datos son:

- **RF-03 + RF-04 y QA-03 (Fiabilidad):** cuando un reciclador confirma un recojo, se deben acreditar los
  puntos **exactamente una vez**. El escenario exige **0 acreditaciones duplicadas en 1000 confirmaciones
  simuladas**, con el reciclador reintenta el envío por error de conexión. Esto es un problema de **integridad
  transaccional**: el registro del recojo y el movimiento de puntos deben ocurrir juntos o no ocurrir.
- **RF-05 (Reportes):** la municipalidad necesita **toneladas recicladas agrupadas por distrito y por mes**.
  Es una consulta agregada sobre datos de la tabla de recojos.
- **RF-06 y QA-01 (Modificabilidad, atributo crítico):** la municipalidad va a sumar distritos y cambiar
  reglas de puntos en ≤ 2 días-persona. El dato medible del caso es que el esquema **no cambia**, solo su
  contenido.
- **R-03 (Presupuesto):** un solo VPS. Una base de datos adicional o una especializada encarece el despliegue.
- **R-04 (Normativa):** datos personales de vecinos (domicilio) protegidos por la Ley 29733.

El equipo tiene experiencia en Python/Django (R-02), y el ORM de Django trabaja de forma nativa y madura con
bases de datos relacionales.

## Alternativas consideradas

1. **PostgreSQL (relacional).** Esquema fijo y explícito, transacciones ACID, funciones de agregación (`SUM`,
   `GROUP BY`) maduras, extensible con índices. Licencia libre.
2. **MongoDB (documental).** Esquema flexible, guardado de documentos JSON. Tolera cambios de forma sin
   migraciones.
3. **SQLite (relacional embebido).** Cero configuración, un solo archivo. Muy rápido en lectura.

## Decisión

**Usaremos PostgreSQL con un esquema por módulo** (`solicitudes`, `rutas`, `puntos`, `distritos`, `reportes`,
`notificaciones`), respetando los límites entre módulos fijados en ADR-001: cada módulo accede **únicamente a su
propio esquema**, y los cruces de datos entre módulos se resuelven por interfaces públicas, no por `JOIN` entre
esquemas de otros.

**Además, la acreditación de puntos al confirmar un recojo se hará dentro de una única transacción de base de
datos**, con una restricción de unicidad que hace imposible el doble cobro a nivel de motor y no solo de
aplicación.

## Consecuencias

**Positivas**

- **QA-03 garantizado por el motor, no por el código.** Una restricción `UNIQUE` sobre
  `(recojo_id, concepto_puntos)` impide que exista una doble acreditación aunque la aplicación se equivoque,
  y una restricción `CHECK` sobre el peso registrado impide datos físicamente imposibles. La prueba de 1000
  confirmaciones queda cubierta por diseño, no por buena fe.
- **RF-05 se resuelve con SQL directo.** `SELECT distrito, SUM(peso), DATE_TRUNC('month', fecha) FROM ... GROUP BY ...`
  es una consulta agregada estándar; en un modelo documental se emularía en la aplicación.
- **Costo cero de licencia** y menor consumo de memoria que una base documental: cabe cómodo en el VPS de R-03.
- **Ajuste a R-02:** el equipo ya domina el stack relacional de Django; no hay curva de aprendizaje.
- **QA-01 no se ve afectada:** los distritos y las reglas cambian de **contenido**, no de **forma**. El esquema
  de `distritos` no se toca al dar de alta un distrito nuevo, así que no hay migraciones que revisar.

**Negativas / riesgos**

- **Migraciones de esquema obligatorias.** Si algún día un módulo necesita cambiar su forma, Django exige una
  migración versionada y reversible. Con R-01 (1 mes) esto puede trabar el proyecto si se cambia el modelo a destiempo.
- **PostgreSQL exige un servicio adicional que operar** (instalación, credenciales, backups), a diferencia de
  SQLite. Es un costo operativo real, aceptado porque los datos **no pueden vivir en el cliente**: son
  compartidos entre el vecino, el reciclador y la municipalidad.
- **Rigid ante datos muy irregulares.** Si algún día un tipo de residuo tuviera metadatos muy variables, el
  modelo relacional exigiría tabla adicional o columna `JSONB` como escape.
- **Los cruces entre módulos requieren lectura de dos consultas o una vista materializada.** Se sacrifica
  comodidad en las consultas a cambio de mantener los límites de ADR-001. Es una decisión consciente.
- **Un solo punto de fallo:** si PostgreSQL cae, cae el sistema completo. Mitigación: backups automáticos
  diarios y procedimiento de restauración probado antes de producción.

## Nota sobre un malentendido frecuente

La IA sugirió en más de una oportunidade que, para "no modificar los demás módulos", convenía una base de
datos **documental** por ser de esquema flexible. El equipo lo rechazó: **la modificabilidad (QA-01) no exige
flexibilidad de esquema, exige que el esquema cambie poco.** Los distritos y las reglas son filas, no columnas;
la estructura de las tablas no cambia cuando la municipalidad suma un distrito. La flexibilidad de esquema
resuelve un problema que este caso no tiene, y a cambio se perderían las transacciones ACID que QA-03 sí
necesita.