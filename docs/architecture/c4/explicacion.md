# Explicación para público no técnico (E7)

**Prompt IA 3 (adaptado al caso)**: Explica el diagrama de contexto de ChacraSmart Majes al dueño de una
asociación de agricultores de Majes, que no es técnico, en máximo 120 palabras: qué hace el sistema, quién lo
usa y de qué servicios externos depende. Evita la jerga técnica. [vista de contexto exportada]

## Texto revisado por el equipo

ChacraSmart Majes es una aplicación que los agricultores y los técnicos de Majes usan desde su celular. El
agricultor ve qué tan húmeda está su parcela, programa cuándo y cuánto tiempo quiere regar, abre o cierra la
válvula desde donde esté y recibe un aviso cuando falta el agua o el riego falla. El técnico registra parcelas,
sensores y válvulas y revisa que cada uno esté funcionando. Depende de dos servicios externos: un controlador
que vive en la parcela y habla con los sensores y las válvulas —cierra la válvula solo, aunque se caiga la
señal—, y un servicio de mensajería que entrega las alertas por WhatsApp o SMS.

## Verificación de cada afirmación contra `workspace.dsl`

| Afirmación | Evidencia en el modelo |
|---|---|
| "usan desde su celular" | Relación PWA→persona "Usa la PWA en su celular" (vista de contenedores) y nodo "Celular del agricultor / PC del técnico" (vista de despliegue) |
| Agricultor: humedad, programar, abrir/cierra válvulas | Descripción de la persona: "consulta la humedad, programa riegos, abre y cierra válvulas de forma remota… (RF-02 a RF-05)" |
| Aviso cuando falta el agua o el riego falla | Módulo Alertas: "Genera y encola alertas por falta de agua y por estado del riego (RF-05)" |
| Técnico: registra dispositivos y revisa su estado | Descripción de la persona: "Registra parcelas, sensores y válvulas y consulta si cada dispositivo está en línea o fuera de línea (RF-06, RF-07)" |
| Dos servicios externos | `controlador` y `mensajeria` con tag `"Externo"` (`workspace.dsl:24-25`) |
| Controlador en la parcela que cierra la válvula solo con la señal caída | ADR-003 ("temporizador local") y descripción del externo: "…la cierra solo al cumplirse el tiempo programado aunque se pierda la conexión" |
| Alertas por WhatsApp o SMS | Descripción del mensajero: "Envía las alertas por WhatsApp / SMS a los usuarios (R-06)" |

**Contador de palabras**: `wc -w` sobre el texto → **109 ≤ 120** (verificado en la sesión, 17/10/2026).

Nota de corrección: el primer borrador decía "recibe un aviso si algo falla"; se acotó a "cuando falta el agua
o el riego no sale como esperaba" porque las alertas del modelo son por falta de agua y por estado del riego
(RF-05), no genéricas.
