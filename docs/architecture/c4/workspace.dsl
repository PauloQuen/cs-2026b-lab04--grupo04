workspace "ChacraSmart Majes" "Modelo C4 de la plataforma de riego inteligente de Majes" {

    !identifiers hierarchical

    model {
        agricultor = person "Agricultor" "Dueño de la parcela: consulta la humedad, programa riegos, abre y cierra válvulas de forma remota y recibe alertas (RF-02 a RF-05)."
        tecnico = person "Técnico" "Registra parcelas, sensores y válvulas y consulta si cada dispositivo está en línea o fuera de línea (RF-06, RF-07)."

        chacra = softwareSystem "ChacraSmart Majes" "Plataforma de riego inteligente: recibe lecturas de humedad, permite programar riegos y controla las válvulas con falla segura local (QA-01)."
        controlador = softwareSystem "Controlador de campo" "Dispositivo en la parcela: lee el sensor, acciona la válvula y la cierra solo al cumplirse el tiempo programado aunque se pierda la conexión (ADR-003)." "Externo"
        mensajeria = softwareSystem "Servicio de mensajería" "Envía las alertas por WhatsApp / SMS a los usuarios (R-06)." "Externo"

        # ---------------------------------------------------------------- Nivel 1: contexto
        agricultor -> chacra "Consulta humedad, programa riegos y controla sus válvulas"
        tecnico -> chacra "Registra dispositivos y consulta su estado"
        chacra -> controlador "Envía órdenes de riego y recibe lecturas" "HTTP/JSON (ADR-002)"
        chacra -> mensajeria "Envía alertas de riego" "HTTPS/JSON"

    }

    views {
        systemContext chacra "Contexto" "Nivel 1: ChacraSmart Majes y su entorno." {
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
