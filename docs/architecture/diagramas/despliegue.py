#!/usr/bin/env python3
"""
Vista de despliegue — ChacraSmart Majes (Lab 04, E6)

Diagram as Code con la libreria `diagrams` (mingrammer) sobre Graphviz.
El servidor vive en UN SOLO VPS (R-03) y en UN SOLO despliegue (ADR-001);
por eso el diagrama tiene un unico Cluster de servidor.
El controlador de campo esta en otro Cluster, porque corre en la parcela (ADR-003).

Como ejecutarlo:
    pip install diagrams          # requiere Graphviz instalado en el sistema
    cd docs/architecture/diagramas
    python despliegue.py
Salida:
    img/despliegue.png

Todas las clases importadas fueron verificadas contra la libreria instalada:
un import incorrecto hace fallar el script, y ese fallo es exactamente la
verificacion que pide la guia (E7).
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.generic.device import Mobile
from diagrams.onprem.client import Users
from diagrams.onprem.compute import Server
from diagrams.onprem.database import PostgreSQL
from diagrams.onprem.inmemory import Redis
from diagrams.onprem.monitoring import Grafana, Prometheus
from diagrams.onprem.network import Internet, Nginx
from diagrams.onprem.queue import Celery
from diagrams.programming.framework import Django

graph_attr = {
    "fontsize": "20",
    "bgcolor": "white",
    "pad": "0.3",
    "nodesep": "0.45",
    "ranksep": "0.55",
    "splines": "ortho",
}

FUENTE = "docs/architecture/drivers.md"

with Diagram(
    "ChacraSmart Majes — Vista de despliegue (monolito modular, un solo VPS)",
    filename="img/despliegue",
    show=False,
    direction="LR",
    graph_attr=graph_attr,
    outformat="png",
):

    # ------------------------------------------------------------------ CLIENTES
    usuarios = Users("Agricultores\ny tecnicos")
    movil = Mobile("PWA en celular\nde gama baja\nQA-02")

    # --------------------------------------------------- SERVIDOR UNICO (R-03)
    with Cluster("Servidor en la nube — UN SOLO VPS (R-03)"):

        proxy = Nginx("Nginx\nproxy inverso + HTTPS")

        with Cluster("Monolito modular — un solo despliegue (ADR-001)"):
            app = Django("Django API\n5 modulos de dominio\nLecturas · Programacion\nValvulas · Alertas · Dispositivos")

            worker = Celery("Celery\ntareas asincronas\n(alertas RF-05,\nreportes de humedad)")

        cache = Redis("Redis\ncola + estado de\nvalvulas abiertas\n(QA-01 · safety)")

        db = PostgreSQL("PostgreSQL\nun esquema por modulo")

        with Cluster("Monitoreo"):
            metricas = Prometheus("Prometheus\nmetricas de la app")
            paneles = Grafana("Grafana\npaneles y alertas")

    # -------------------------------------------- CAMPO: controlador de campo
    with Cluster("Parcela en Majes — campo (R-03, R-04)"):
        controlador = Server("Controlador de campo\nsensor + valvula\ntemporizador local (ADR-003)")

    # ------------------------------------------------------ SERVICIOS EXTERNOS
    mensajeria = Internet("Servicio de mensajeria\n(WhatsApp / SMS)\nservicio externo")

    # ------------------------------------------------------------------- FLUJOS
    usuarios >> movil
    movil >> Edge(label="HTTPS /api", color="#1565C0") >> proxy
    proxy >> Edge(label="gunicorn :8000", color="#1565C0") >> app

    app >> Edge(label="esquema por modulo", color="#37474F") >> db
    app >> Edge(label="encola tarea", color="#6A1B9A") >> cache
    cache >> Edge(label="consume", color="#6A1B9A") >> worker

    worker >> Edge(label="alerta de falta de agua (RF-05)", style="dashed", color="#7F7F7F") >> mensajeria

    app >> Edge(label="expone /metrics", style="dotted", color="#C0392B") >> metricas
    metricas >> Edge(label="consulta", style="dotted", color="#C0392B") >> paneles

    controlador >> Edge(label="HTTP lecturas\ny ordenes (ADR-002)", color="#C0392B") >> proxy