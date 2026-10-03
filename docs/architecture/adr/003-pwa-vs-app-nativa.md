# ADR-003: Entregar una PWA en lugar de una aplicación nativa

- **Estado:** Aceptado
- **Fecha:** 2026-10-03
- **Decisores:** Quenta Ahumada Paulo Estefano, Kevin Joel Callo Ccagiavilca

---

## Contexto

EcoRecicla AQP se usa **en el campo y en el teléfono**, no frente a una computadora. Los actores son el
vecino (RF-01, RF-04), el reciclador (RF-02, RF-03) y la municipalidad (RF-05, RF-06), y los dos primeros
están en movimiento.

Las restricciones que dominan esta decisión:

- **R-05 — Tecnología:** debe funcionar en **celulares de gama baja con conexión móvil limitada (3G)**. No
  todos los usuarios tienen un teléfono Android reciente ni almacenamiento disponible.
- **R-01 — Plazo:** MVP en producción en **1 mes**.
- **R-02 — Equipo:** **2 developers**. Publicar en dos tiendas de aplicaciones y mantener dos bases de código
  consume tiempo que el equipo no tiene.
- **R-03 — Presupuesto:** un solo VPS.
- **QA-02 (Capacidad de interacción):** la solicitud de recojo debe completarse en **≤ 4 toques y ≤ 60 s**,
  con señal 3G y pantalla pequeña.
- **R-06 — Integración:** los avisos al vecino llegan por **WhatsApp** (RF-07), no por notificaciones push.

La misma aplicación debe servir a tres perfiles con permisos distintos (vecino, reciclador, municipalidad), y
el perfil de municipalidad es de escritorio-oficina, no de campo.

## Alternativas consideradas

1. **PWA (aplicación web instalable).** Una sola base de código servida por el propio monolito modular
   ([ADR-001](001-estilo-arquitectonico.md)), instalable en la pantalla de inicio y capaz de funcionar con
   caché en el dispositivo. Sin tienda de aplicaciones.
2. **App nativa Android (Kotlin o Java).** Máximo acceso a hardware y notificaciones, mejor rendimiento en
   equipos muy modestos. Exige compilar, firma, publicar en Google Play y esperar revisión; el Android Studio
   y el SDK añaden peso al proyecto.
3. **App híbrida (Capacitor, React Native o Flutter).** Comparte código con la web y añade un contenedor
   nativo. Exige además Node, además del stack de Python, y un segundo proceso de build.

## Decisión

**Usaremos una PWA (aplicación web instalable)**, servida por el mismo proceso Django del monolito modular y
cacheada por el service worker para el uso en campo.

Concretamente:

- Un **único proyecto web** (Django + plantilla) que entrega la interfaz de los tres perfiles.
- **Manifiesto web instalable** (`manifest.json`) e **service worker** para instalar en la pantalla de inicio
  y servir una versión en caché cuando hay señal débil.
- **Los avisos de RF-07 se envían por WhatsApp**, no por push del navegador. Esta decisión es deliberada y
  resuelve el mayor riesgo técnico de una PWA: las notificaciones push en iOS solo funcionan si la PWA está
  instalada, y tienen restricciones adicionales. Como el usuario ya usa WhatsApp a diario, el canal es más
  familiar y más confiable que una notificación del navegador.
- **HTTPS obligatorio**, condición de funcionamiento de las PWA (service worker) y de la Ley 29733 para tratar
  datos de vecinos (R-04). Ya está contemplado en el proxy Nginx del despliegue
  ([`../diagramas/despliegue.py`](../diagramas/despliegue.py)).

## Consecuencias

**Positivas**

- **Una sola base de código para los tres perfiles**, servida por el mismo despliegue. Con 2 developers (R-02)
  esto no es una preferencia técnica: es la diferencia entre entregar y no entregar en 1 mes (R-01).
- **Sin publicación en tiendas:** no hay revisión, ni versioning de APK, ni actualizaciones que el usuario
  tiene que instalar. Una corrección en el servidor llega a todos en el siguiente arranque.
- **Instalación opcional:** quien no instale la PWA puede usar la web directamente; el vecino no tiene que
  pasar por una tienda para empezar a usar el servicio.
- **Presupuesto:** sin costos de publicación ni de infraestructura adicional (R-03).
- **Base sólida para QA-02:** con un service worker se puede servir la interfaz desde caché, de modo que la
  pantalla de solicitud se abre sin red y solo la confirmación requiere conexión.
- **Coherente con ADR-001:** la PWA es otro cliente del monolito modular; no introduce una segunda
  tecnología de despliegue.

**Negativas / riesgos**

- **Acceso limitado a funciones nativas del dispositivo:** sin cámara para evidencia fotográfica del residuo,
  sin GPS en segundo plano y sin acceso a la libreta de contactos. Si el caso lo exigiera, sería un motivo
  para reabrir esta decisión.
- **Rendimiento en equipos muy modestos:** en gama baja la interfaz se siente algo más lenta que una app
  nativa. Se mitiga con caché de la interfaz y payloads mínimos.
- **Compatibilidad de iOS:** las PWA en Safari tienen menos capacidades que en Chrome (notificaciones
  sujetas a que la app esté instalada, sin instalación automática). Es un riesgo real para una parte de los
  vecinos, y refuerza la decisión de usar WhatsApp como canal de avisos.
- **Depende de un tercero para las notificaciones:** si la Meta rechaza la cuenta o cambia el precio, los
  avisos de RF-07 se pierden. Riesgo aceptado y documentado en
  [`../matriz-decision.md`](../matriz-decision.md) §5.1, con un plan de contingencia: notificación in-app y
  correo.
- **Riesgo de origen único:** al no existir una tienda, una versión defectuosa llega a todos los usuarios a la
  vez. Se controla con despliegue progresivo y verificación de QA-02 en emulación de gama baja.

## Cuándo reabrir esta decisión

Si el caso sumara un requisito que la PWA no puede cumplir —por ejemplo, **registro fotográfico obligatorio de
la evidencia del residuo** o **geolocalización en segundo plano para el recorrido del reciclador**— entonces
esta decisión debe revisarse y migrar a una aplicación híbrida. Ninguno de esos requisitos está en el alcance
actual del MVP.