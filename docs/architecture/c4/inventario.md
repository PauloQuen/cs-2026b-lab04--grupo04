# Inventario del modelo C4 — ChacraSmart Majes (E1)

> Lab 06 · Modelo C4 · Construcción de Software · EPIS-UNSA · 2026-B · Grupo 04
>
> Cada elemento del `workspace.dsl` aparece aquí con su **tipo C4**, su descripción y **de dónde sale**.
> Nada se modela "porque quedaba bien": todo tiene insumo en los entregables del Lab 04 y del Lab 05.

## 1. Nivel 1 — Contexto

| Elemento            | Tipo C4         | Descripción                                                                                         | Fuente                     |
|---------------------|-----------------|-----------------------------------------------------------------------------------------------------|----------------------------|
| Agricultor          | Person          | Consulta humedad, programa riegos, abre/cierra válvulas y recibe alertas (RF-02 … RF-05)             | `drivers.md` §1, caso 9    |
| Técnico             | Person          | Registra parcelas, sensores y válvulas y consulta su estado en línea / fuera de línea (RF-06, RF-07) | `drivers.md` §1            |
| **ChacraSmart Majes** | Software System | Plataforma de riego inteligente: recibe lecturas, permite programar riegos y controla válvulas con falla segura local | ADR-001, README "Caso"     |
| Controlador de campo | Software System **Externo** | Dispositivo en la parcela: lee el sensor, acciona la válvula y cierra sola al vencer el tiempo programado (ADR-003) | **ADR-001** ("integraciones externas: controlador de campo…"), ADR-002, ADR-003 |
| Servicio de mensajería | Software System **Externo** | Envía las alertas por WhatsApp / SMS a los usuarios                                                  | **ADR-001** ("…y servicio de mensajería"), R-06, `despliegue.py` |

**Por qué el controlador es externo y no contenedor:** el ADR-001 lo nombra textualmente como una de las dos
**integraciones externas** que se implementan como adaptadores detrás de puertos, corre en hardware embebido
(nuestro stack declarado en R-02 es Python/Django) y es justo la frontera que el ADR-002 cruza con HTTP.
Además, el README del Lab 04 ya lo dibuja con estilo `externo`. Modelarlo como contenedor interno contradeciría
el propio ADR-001. Ambos externos cumplen la regla E1 de "2+ sistemas externos con etiqueta `Externo`".

## 2. Nivel 2 — Contenedores (del sistema)

| Contenedor                  | Descripción                                                                            | Tecnología                     | Fuente (`despliegue.py`, ADR-001) | Estilo C4     |
|-----------------------------|----------------------------------------------------------------------------------------|--------------------------------|-----------------------------------|---------------|
| PWA                         | Interfaz de agricultor y técnico; ligera para gama baja y señal intermitente            | HTML / CSS / JavaScript (PWA)  | `despliegue.py` (Mobile), R-05    | Web Browser   |
| API ChacraSmart             | Monolito modular: los casos de uso viven en 5 módulos que solo se comunican por interfaces públicas | Python / Django + gunicorn     | ADR-001, `despliegue.py` (Django)  | Container     |
| Worker de tareas            | Ejecuta de forma asíncrona el envío de alertas y reintentos                            | Celery                         | `despliegue.py` (Celery)          | Container     |
| Base de datos                | Lecturas, programaciones, válvulas, parcelas y usuarios (un esquema por módulo)         | PostgreSQL 16                  | `despliegue.py` (PostgreSQL)       | **Database**  |
| Cola y caché                | Cola de tareas del worker y caché del estado de válvulas abiertas (QA-01)               | Redis                          | `despliegue.py` (Redis)            | **Queue**     |

**Alcance (decisión documentada):** Nginx, Prometheus y Grafana de `despliegue.py` **no** son contenedores
del nivel 2: son infraestructura de operación, no implementan casos de uso del MVP. Se anota en
[`revision-c4.md`](revision-c4.md) §Alcance para que la omisión sea una decisión explícita y no un olvido.

## 3. Nivel 3 — Componentes (dentro de la API)

| Componente                  | Responsabilidad (RF)                                          | Fuente                       |
|-----------------------------|---------------------------------------------------------------|------------------------------|
| Módulo Lecturas             | Recibe y consulta lecturas de humedad (RF-01, RF-02)          | ADR-001, `paquetes.puml` (`lecturas`) |
| Módulo Programación         | Crea y ejecuta programaciones de riego (RF-03)                | ADR-001, `paquetes.puml` (`programacion`) |
| Módulo Control de válvulas  | Órdenes de apertura/cierre con duración máxima; aísla el control crítico (RF-04, QA-01) | ADR-001, `paquetes.puml` (`control_valvulas`) |
| Módulo Alertas              | Genera y encola alertas por falta de agua y estado del riego (RF-05) | ADR-001, `paquetes.puml` (`alertas`) |
| Módulo Dispositivos         | Parcelas, sensores y válvulas y su estado en línea (RF-06, RF-07) | ADR-001, `paquetes.puml` (`dispositivos`) |
| Módulo Compartido           | Tipos y utilidades comunes de uso compartido                  | `paquetes.puml` (`compartido`) |

Los 6 componentes son **idénticos a los paquetes de `paquetes.puml`** (Lab 05, E5). El grafo de dependencias
es el mismo DAG verificado en `consistencia.md` (C4, algoritmo de Kahn), **más** la arista
`programacion → alertas`: la secuencia del Lab 05 muestra a `ServicioRiego` invocando `notificarAlerta()`
(`secuencia-programar-riego.puml`, actos I y III), y esa arista ya era transitiva (`programacion → lecturas → alertas`),
así que **no crea ciclos**. Detalle en [`comparacion.md`](comparacion.md).

## 4. Vista dinámica

| Vista            | Flujo                                                        | Fuente                          |
|------------------|--------------------------------------------------------------|---------------------------------|
| `ProgramarRiego` | 9 pasos: programar → guardar → orden de apertura → acuse → cierre por temporizador local → alerta | `secuencia-programar-riego.puml` (Lab 05, E2) |

Cada paso de la vista dinámica corresponde a una relación (par origen → destino) ya definida en el modelo.

## 5. Vista de despliegue

| Nodo                              | Contenido                                | Fuente                                     |
|-----------------------------------|------------------------------------------|--------------------------------------------|
| Celular / PC del usuario          | instancia de la PWA                      | `despliegue.py` (Mobile), R-05             |
| Parcela en Majes                  | instancia del controlador de campo       | ADR-003, `despliegue.py` (cluster "campo") |
| VPS (Ubuntu 24.04, 2 vCPU, 4 GB)  | instancia de **cada** contenedor del servidor bajo Docker Compose | R-03 (un solo VPS), `despliegue.py` |
