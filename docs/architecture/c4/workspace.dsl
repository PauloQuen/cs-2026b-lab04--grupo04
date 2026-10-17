workspace "ChacraSmart Majes" "Modelo C4 de la plataforma de riego inteligente de Majes" {

    !identifiers hierarchical

    model {
        agricultor = person "Agricultor" "Dueño de la parcela: consulta la humedad, programa riegos, abre y cierra válvulas de forma remota y recibe alertas (RF-02 a RF-05)."
        tecnico = person "Técnico" "Registra parcelas, sensores y válvulas y consulta si cada dispositivo está en línea o fuera de línea (RF-06, RF-07)."

        chacra = softwareSystem "ChacraSmart Majes" "Plataforma de riego inteligente: recibe lecturas de humedad, permite programar riegos y controla las válvulas con falla segura local (QA-01)." {
            pwa = container "PWA" "Interfaz para agricultores y técnicos; ligera para celulares de gama baja y apta para señal intermitente." "HTML / CSS / JavaScript (PWA)" "Web Browser"
            api = container "API ChacraSmart" "Monolito modular: los casos de uso viven en cinco módulos de dominio que se comunican solo por interfaces públicas (ADR-001)." "Python / Django + gunicorn" {
                lecturas = component "Módulo Lecturas" "Recibe y consulta lecturas de humedad del suelo (RF-01, RF-02)." "Django app"
                programacion = component "Módulo Programación" "Crea, ejecuta y finaliza programaciones de riego (RF-03)." "Django app"
                control_valvulas = component "Módulo Control de válvulas" "Órdenes de apertura y cierre con duración máxima; aísla el control crítico (RF-04, QA-01)." "Django app"
                alertas = component "Módulo Alertas" "Genera y encola alertas por falta de agua y por estado del riego (RF-05)." "Django app"
                dispositivos = component "Módulo Dispositivos" "Parcelas, sensores y válvulas y su estado en línea / fuera de línea (RF-06, RF-07)." "Django app"
                compartido = component "Módulo Compartido" "Tipos y utilidades comunes a todos los módulos (etiquetado y reglas del dominio)." "Python"
            }
            worker = container "Worker de tareas" "Ejecuta de forma asíncrona el envío de alertas y sus reintentos." "Celery"
            db = container "Base de datos" "Lecturas, programaciones, válvulas, parcelas y usuarios; un esquema por módulo." "PostgreSQL 16" "Database"
            redis = container "Cola y caché" "Cola de tareas del worker y caché del estado de las válvulas abiertas (QA-01)." "Redis" "Queue"
        }

        controlador = softwareSystem "Controlador de campo" "Dispositivo en la parcela: lee el sensor, acciona la válvula y la cierra solo al cumplirse el tiempo programado aunque se pierda la conexión (ADR-003)." "Externo"
        mensajeria = softwareSystem "Servicio de mensajería" "Envía las alertas por WhatsApp / SMS a los usuarios (R-06)." "Externo"

        # ---------------------------------------------------------------- Nivel 1: contexto
        agricultor -> chacra "Consulta humedad, programa riegos y controla sus válvulas"
        tecnico -> chacra "Registra dispositivos y consulta su estado"
        chacra -> controlador "Envía órdenes de riego y recibe lecturas" "HTTP/JSON (ADR-002)"
        chacra -> mensajeria "Envía alertas de riego" "HTTPS/JSON"

        # ---------------------------------------------------------------- Nivel 2: contenedores
        agricultor -> chacra.pwa "Usa la PWA en su celular" "HTTPS"
        tecnico -> chacra.pwa "Usa la PWA para registrar dispositivos" "HTTPS"
        chacra.pwa -> chacra.api "Llama a la API" "HTTPS/JSON (REST)"
        chacra.api -> chacra.db "Lee y escribe" "SQL/TCP"
        chacra.api -> chacra.redis "Encola alertas y cachea el estado de las válvulas" "Redis protocol"
        chacra.worker -> chacra.redis "Consume las tareas encoladas" "Redis protocol"
        chacra.worker -> mensajeria "Envía las alertas por WhatsApp / SMS" "HTTPS/JSON"
        chacra.api -> controlador "Envía órdenes de apertura y cierre" "HTTP/JSON (ADR-002)"
        controlador -> chacra.api "Envía lecturas, acuses y eventos del temporizador local" "HTTP/JSON (ADR-002)"

        # ---------------------------------------------------------------- Nivel 3: componentes
        # Superficie REST de la PWA por módulo (cada módulo expone sus propios recursos).
        chacra.pwa -> chacra.api.lecturas "Consulta la humedad actual e histórica" "HTTPS/JSON"
        chacra.pwa -> chacra.api.programacion "Programa y consulta riegos" "HTTPS/JSON"
        chacra.pwa -> chacra.api.control_valvulas "Abre y cierra válvulas de forma remota" "HTTPS/JSON"
        chacra.pwa -> chacra.api.dispositivos "Registra parcelas y dispositivos" "HTTPS/JSON"

        # Dependencias entre módulos: idénticas a paquetes.puml (Lab 05), más
        # programacion -> alertas que exige la secuencia (ServicioRiego -> Notificador).
        chacra.api.programacion -> chacra.api.control_valvulas "Usa el puerto ControladorValvula"
        chacra.api.programacion -> chacra.api.lecturas "Evalúa la humedad antes de regar"
        chacra.api.programacion -> chacra.api.alertas "Pide notificar el estado del riego"
        chacra.api.lecturas -> chacra.api.alertas "Usa el puerto Notificador (falta de agua)"
        chacra.api.control_valvulas -> chacra.api.dispositivos "Usa la entidad Valvula"
        chacra.api.alertas -> chacra.api.dispositivos "Usa la entidad Agricultor"

        chacra.api.lecturas -> chacra.api.compartido "Usa tipos comunes (LecturaHumedad)"
        chacra.api.programacion -> chacra.api.compartido "Usa tipos comunes (ProgramacionRiego)"
        chacra.api.control_valvulas -> chacra.api.compartido "Usa tipos comunes (EstadoValvula)"
        chacra.api.alertas -> chacra.api.compartido "Usa tipos comunes (Notificador)"
        chacra.api.dispositivos -> chacra.api.compartido "Usa tipos comunes (Valvula)"

        # Integraciones externas vistas desde los módulos (adaptadores del ADR-001).
        chacra.api.control_valvulas -> controlador "Envía la orden con duración máxima y recibe acuses" "HTTP/JSON (ADR-002)"
        controlador -> chacra.api.lecturas "Envía lecturas de humedad" "HTTP/JSON (ADR-002)"
        controlador -> chacra.api.control_valvulas "Envía acuses y el cierre del temporizador local" "HTTP/JSON (ADR-002)"
        chacra.api.alertas -> chacra.redis "Encola el envío de la alerta" "Redis protocol"

        # Persistencia de los módulos del flujo crítico.
        chacra.api.programacion -> chacra.db "Guarda las programaciones" "SQL/TCP"
        chacra.api.lecturas -> chacra.db "Guarda las lecturas" "SQL/TCP"

        # ---------------------------------------------------------------- Despliegue (E5)
        produccion = deploymentEnvironment "Producción" {
            deploymentNode "Celular del agricultor / PC del técnico" "" "Android · navegador web (gama baja, R-05)" {
                containerInstance chacra.pwa
            }
            deploymentNode "Parcela en Majes" "" "conexión intermitente (R-04)" {
                deploymentNode "Controlador de campo" "" "embebido, sensor + válvula, temporizador local (ADR-003)" {
                    softwareSystemInstance controlador
                }
            }
            deploymentNode "VPS en la nube" "" "Ubuntu 24.04 · 2 vCPU · 4 GB RAM (R-03, un solo VPS)" {
                deploymentNode "Docker Compose" "" "Docker 27" {
                    containerInstance chacra.api
                    containerInstance chacra.worker
                    containerInstance chacra.db
                    containerInstance chacra.redis
                }
            }
        }
    }

    views {
        systemContext chacra "Contexto" "Nivel 1: ChacraSmart Majes y su entorno." {
            include *
            autolayout lr
        }
        container chacra "Contenedores" "Nivel 2: contenedores de ChacraSmart Majes." {
            include *
            autolayout lr
        }
        component chacra.api "Componentes" "Nivel 3: módulos del monolito modular (ADR-001)." {
            include *
            autolayout lr
        }
        dynamic chacra.api "ProgramarRiego" "Dinámico: programar un riego y abrir la válvula de forma remota (flujo crítico del Lab 05)." {
            agricultor -> chacra.pwa "Programa un riego (parcela, hora y duración)"
            chacra.pwa -> chacra.api.programacion "POST /riegos"
            chacra.api.programacion -> chacra.db "guardarProgramacion(p) — estado PENDIENTE"
            chacra.api.programacion -> chacra.api.control_valvulas "abrir(valvulaId, duracionMin) por el puerto ControladorValvula"
            chacra.api.control_valvulas -> controlador "Orden de apertura con duración máxima (ADR-003)"
            controlador -> chacra.api.control_valvulas "Acuse de apertura; al vencer, cierre por temporizador local"
            chacra.api.programacion -> chacra.api.alertas "notificarAlerta(riego iniciado / finalizado)"
            chacra.api.alertas -> chacra.redis "Encola el envío de la alerta"
            chacra.worker -> mensajeria "Envía la alerta por WhatsApp / SMS"
            autolayout lr
        }
        deployment chacra produccion "Despliegue" "Despliegue en producción (MVP, un solo VPS — R-03)." {
            include *
            autolayout lr
        }
        styles {
            element "Person" {
                shape person
                background #08427B
                color #ffffff
            }
            element "Software System" {
                background #1168BD
                color #ffffff
            }
            element "Externo" {
                background #999999
            }
            element "Container" {
                background #438DD5
                color #ffffff
            }
            element "Component" {
                background #85BBF0
                color #000000
            }
            element "Database" {
                shape cylinder
            }
            element "Queue" {
                shape pipe
            }
            element "Web Browser" {
                shape WebBrowser
            }
        }
    }
}
