#!/usr/bin/env python3
"""
Vista de despliegue — EcoRecicla AQP (Lab 04, E6)

Diagram as Code con la libreria `diagrams` (mingrammer) sobre Graphviz.
Todo el sistema vive en UN SOLO VPS (R-03) y en UN SOLO despliegue (ADR-001);
por eso el diagrama tiene un unico Cluster de servidor.

Como ejecutarlo:
    pip install diagrams          # requiere Graphviz instalado en el sistema
    cd docs/architecture/diagramas
    python despliegue.py
Salida:
    img/despliegue.png

Todas las clases importadas fueron verificadas contra la libreria instalada:
un import incorrecto hace fallar el script, y ese fallo es exactamente la
verificacion que pide la guia (E7, interaccion 5).
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.generic.device import Mobile
from diagrams.onprem.client import Users
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
    "EcoRecicla AQP — Vista de despliegue (monolito modular, un solo VPS)",
    filename="img/despliegue",
    show=False,
    direction="LR",
    graph_attr=graph_attr,
    outformat="png",
):

    # ------------------------------------------------------------------ CLIENTES
    usuarios = Users("Vecinos, recicladores\ny municipalidad")
    movil = Mobile("PWA instalada\n(celular de gama baja)\nQA-02 · R-05")

    # --------------------------------------------------- SERVIDOR UNICO (R-03)
    with Cluster("Servidor en la nube — UN SOLO VPS (R-03)"):

        proxy = Nginx("Nginx\nproxy inverso + HTTPS\n(R-04, R-05)")

        with Cluster("Monolito modular — un solo despliegue (ADR-001)"):
            app = Django("Django API\n6 modulos de dominio\nSolicitudes · Rutas · Puntos\nDistritos · Reportes · Notif.")

            worker = Celery("Celery\ntareas asincronas\n(avisos WhatsApp RF-07,\nreporte de toneladas RF-05)")

        cache = Redis("Redis\ncola + cache de rutas\n(QA-03 · fiabilidad)")

        db = PostgreSQL("PostgreSQL\nun esquema por modulo\n(ADR-002)")

        with Cluster("Monitoreo"):
            metricas = Prometheus("Prometheus\nmetricas de la app")
            paneles = Grafana("Grafana\npaneles y alertas")

    # ------------------------------------------------------ SERVICIOS EXTERNOS
    whatsapp = Internet("WhatsApp\nBusiness API\n(servicio externo)")
    ruteo = Internet("Motor de ruteo\nOSRM\n(servicio externo, BSD)")

    # ------------------------------------------------------------------- FLUJOS
    usuarios >> movil
    movil >> Edge(label="HTTPS /api", color="#1565C0") >> proxy
    proxy >> Edge(label="gunicorn :8000", color="#1565C0") >> app

    app >> Edge(label="esquema por modulo", color="#37474F") >> db
    app >> Edge(label="encola tarea", color="#6A1B9A") >> cache
    cache >> Edge(label="consume", color="#6A1B9A") >> worker

    worker >> Edge(label="aviso de recojo (RF-07)", style="dashed", color="#7F7F7F") >> whatsapp
    app >> Edge(label="optimiza ruta (RF-02)", style="dashed", color="#7F7F7F") >> ruteo

    app >> Edge(label="expone /metrics", style="dotted", color="#C0392B") >> metricas
    metricas >> Edge(label="consulta", style="dotted", color="#C0392B") >> paneles