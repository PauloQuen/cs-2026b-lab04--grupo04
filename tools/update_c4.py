#!/usr/bin/env python3
"""Actualiza workspace.dsl con las etiquetas de trazabilidad [QA-xx] (Lab 08, E6)."""

from pathlib import Path

path = Path("docs/architecture/c4/workspace.dsl")
lines = path.read_text(encoding="utf-8").splitlines()

new_lines = []
for line in lines:
    if 'softwareSystem "ChacraSmart Majes"' in line and "(QA-01)" in line:
        line = line.replace("(QA-01).", "[QA-01 a QA-05].")
    elif 'pwa = container "PWA"' in line:
        line = '            pwa = container "PWA" "Interfaz para agricultores y técnicos [QA-02, QA-05]; offline-first y ligera para celulares de gama baja." "HTML / CSS / JavaScript (PWA)" "Web Browser"'
    elif 'api = container "API ChacraSmart"' in line:
        line = '            api = container "API ChacraSmart" "Monolito modular [QA-01, QA-04]: atiende 67 req/s sostenidas y picos de 120 req/s con gunicorn, decoradores y Circuit Breaker (ADR-001, ADR-006, ADR-007)." "Python / Django + gunicorn" {'
    elif 'lecturas = component "Módulo Lecturas"' in line:
        line = '                lecturas = component "Módulo Lecturas" "Recibe y consulta lecturas de humedad con caché Redis y particionado [QA-01] (RF-01, RF-02)." "Django app"'
    elif 'programacion = component "Módulo Programación"' in line:
        line = '                programacion = component "Módulo Programación" "Crea y finaliza programaciones de riego con duración atómica [QA-02] (RF-03)." "Django app"'
    elif 'control_valvulas = component "Módulo Control de válvulas"' in line:
        line = '                control_valvulas = component "Módulo Control de válvulas" "Órdenes de apertura/cierre con duración máxima y Circuit Breaker [QA-02, QA-03] (RF-04, ADR-007)." "Django app"'
    elif 'alertas = component "Módulo Alertas"' in line:
        line = '                alertas = component "Módulo Alertas" "Genera y encola alertas por falta de agua y anomalías en outbox [QA-03, QA-06] (RF-05)." "Django app"'
    elif 'dispositivos = component "Módulo Dispositivos"' in line:
        line = '                dispositivos = component "Módulo Dispositivos" "Parcelas, sensores y válvulas con aislamiento RLS por sector [QA-04, QA-05] (RF-06, RF-07, ADR-008)." "Django app"'
    elif 'worker = container "Worker de tareas"' in line:
        line = '            worker = container "Worker de tareas" "Ejecuta de forma asíncrona el vaciado de tabla outbox de comandos y reintentos de alertas [QA-03]." "Celery"'
    elif 'db = container "Base de datos"' in line:
        line = '            db = container "Base de datos" "Lecturas, programaciones y parcelas [QA-01, QA-04, QA-05]: PostgreSQL 16 con índices compuestos, particionamiento y RLS (ADR-006, ADR-008)." "PostgreSQL 16" "Database"'
    elif 'redis = container "Cola y caché"' in line:
        line = '            redis = container "Cola y caché" "Cola de tareas del worker y caché de telemetría de parcelas con TTL de 60 s [QA-01, QA-03] (ADR-006)." "Redis" "Queue"'
    elif 'controlador = softwareSystem "Controlador de campo"' in line:
        line = '        controlador = softwareSystem "Controlador de campo" "Dispositivo en parcela [QA-02, QA-03]: Controlador embebido (ESP32 + RTC DS3231) con temporizador local autónomo y solenoide NC; falla segura local en <= 5 s (ADR-003, ADR-007)." "Externo"'
    new_lines.append(line)

path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
print("workspace.dsl actualizado con tags [QA-xx]")
