workspace "ChacraSmart Majes" "Modelo C4 de la plataforma de riego inteligente de Majes" {

    !identifiers hierarchical

    model {
        agricultor = person "Agricultor" "Dueño de la parcela: consulta la humedad, programa riegos, abre y cierra válvulas de forma remota y recibe alertas (RF-02 a RF-05)."
        tecnico = person "Técnico" "Registra parcelas, sensores y válvulas y consulta si cada dispositivo está en línea o fuera de línea (RF-06, RF-07)."

        chacra = softwareSystem "ChacraSmart Majes" "Plataforma de riego inteligente: recibe lecturas de humedad, permite programar riegos y controla las válvulas con falla segura local (QA-01)." {
            pwa = container "PWA" "Interfaz para agricultores y técnicos; ligera para celulares de gama baja y apta para señal intermitente." "HTML / CSS / JavaScript (PWA)" "Web Browser"
            api = container "API ChacraSmart" "Monolito modular: los casos de uso viven en cinco módulos de dominio que se comunican solo por interfaces públicas (ADR-001)." "Python / Django + gunicorn"
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
