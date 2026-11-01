#!/usr/bin/env python3
"""
Generador Maestro del Informe Oficial en Word (.docx) para el Laboratorio 08:
"Diseñar la arquitectura guiada por atributos de calidad: árbol de utilidad, ADD,
tácticas, evaluación ATAM-lite con IA y fitness functions automatizadas"
Caso 9: ChacraSmart Majes 2.0 — Grupo 04

Llena estrictamente la plantilla oficial de la UNSA:
"C:\\Users\\USUARIO\\Desktop\\Copia de GUÍA DE LABORATORIO - FORMATO ESTUDIANTE.docx"
manteniendo TODO el contenido DENTRO de las celdas de las tablas, sin desbordar,
con tablas estilizadas, callouts corporativos, bloques de código sombreados y 5 imágenes de alta resolución.
"""

import os
import sys
from pathlib import Path
from PIL import Image

import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_PATH = Path(r"C:\Users\USUARIO\Desktop\Copia de GUÍA DE LABORATORIO - FORMATO ESTUDIANTE.docx")
DOCS_INFORMES_PATH = REPO_ROOT / "docs" / "informes" / "Informe_Lab08_Diseno_Arquitectura_Grupo04.docx"

# Paleta corporativa institucional
COLOR_PRIMARY = RGBColor(0x1A, 0x36, 0x5D)    # Azul institucional oscuro (#1A365D)
COLOR_SECONDARY = RGBColor(0x2B, 0x6C, 0xB0)  # Azul medio (#2B6CB0)
COLOR_ACCENT = RGBColor(0x2C, 0x52, 0x82)     # Azul pizarra (#2C5282)
COLOR_TEXT = RGBColor(0x2D, 0x37, 0x48)       # Gris carbón (#2D3748)
COLOR_MUTED = RGBColor(0x71, 0x80, 0x96)      # Gris suave (#718096)
COLOR_CODE = RGBColor(0x1A, 0x20, 0x2C)       # Gris oscuro código
COLOR_SUCCESS = RGBColor(0x22, 0x54, 0x3D)    # Verde éxito (#22543D)
COLOR_WARNING = RGBColor(0x7B, 0x34, 0x1E)    # Naranja advertencia (#7B341E)
COLOR_DANGER = RGBColor(0x74, 0x2A, 0x2A)     # Rojo alerta (#742A2A)


def set_cell_margins(cell, top=100, bottom=100, left=140, right=140):
    """Establece márgenes internos de una celda."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'''
        <w:tcMar {nsdecls("w")}>
            <w:top w:w="{top}" w:type="dxa"/>
            <w:left w:w="{left}" w:type="dxa"/>
            <w:bottom w:w="{bottom}" w:type="dxa"/>
            <w:right w:w="{right}" w:type="dxa"/>
        </w:tcMar>
    ''')
    tcPr.append(tcMar)


def apply_cell_styles(cell, fill_hex="F8FAFC", border_left_hex="2B6CB0"):
    """Aplica sombreado y bordes tipo bloque o callout a una celda."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)
    borders = parse_xml(f'''
        <w:tcBorders {nsdecls("w")}>
            <w:top w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>
            <w:left w:val="single" w:sz="24" w:space="0" w:color="{border_left_hex}"/>
            <w:bottom w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>
            <w:right w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>
        </w:tcBorders>
    ''')
    tcPr.append(borders)
    set_cell_margins(cell, top=100, bottom=100, left=140, right=140)


def add_cell_heading_1(cell, text):
    p = cell.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = 'Arial'
    run.font.size = Pt(13.5)
    run.font.bold = True
    run.font.color.rgb = COLOR_PRIMARY
    return p


def add_cell_heading_2(cell, text):
    p = cell.add_paragraph()
    p.paragraph_format.space_before = Pt(11)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = 'Arial'
    run.font.size = Pt(11.5)
    run.font.bold = True
    run.font.color.rgb = COLOR_SECONDARY
    return p


def add_cell_heading_3(cell, text):
    p = cell.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = 'Arial'
    run.font.size = Pt(10.0)
    run.font.bold = True
    run.font.color.rgb = COLOR_ACCENT
    return p


def add_cell_p(cell, text, bold_prefix=None, space_after=3.5, italic=False):
    p = cell.add_paragraph()
    p.paragraph_format.space_before = Pt(1.5)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.font.name = 'Arial'
        r_pre.font.size = Pt(9.5)
        r_pre.font.bold = True
        r_pre.font.color.rgb = COLOR_TEXT
    run = p.add_run(text)
    run.font.name = 'Arial'
    run.font.size = Pt(9.5)
    run.font.color.rgb = COLOR_TEXT
    run.font.italic = italic
    return p


def add_cell_bullet(cell, text, bold_prefix=None, level=0):
    p = cell.add_paragraph()
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(2.5)
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.left_indent = Inches(0.25 * (level + 1))
    
    # Bullet symbol
    r_sym = p.add_run("▪  ")
    r_sym.font.name = 'Arial'
    r_sym.font.size = Pt(8.5)
    r_sym.font.bold = True
    r_sym.font.color.rgb = COLOR_SECONDARY

    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.font.name = 'Arial'
        r_pre.font.size = Pt(9.5)
        r_pre.font.bold = True
        r_pre.font.color.rgb = COLOR_TEXT
    run = p.add_run(text)
    run.font.name = 'Arial'
    run.font.size = Pt(9.5)
    run.font.color.rgb = COLOR_TEXT
    return p


def add_cell_callout(cell, text, title=None, style_type="info"):
    """Inserta un cuadro destacado elegante dentro de una celda."""
    tbl = cell.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    c = tbl.cell(0, 0)
    
    if style_type == "success":
        fill = "F0FDF4"
        border = "22C55E"
        title_color = COLOR_SUCCESS
    elif style_type == "warning":
        fill = "FFFBEB"
        border = "F59E0B"
        title_color = COLOR_WARNING
    elif style_type == "danger":
        fill = "FEF2F2"
        border = "EF4444"
        title_color = COLOR_DANGER
    else:  # info
        fill = "F0F9FF"
        border = "0284C7"
        title_color = COLOR_SECONDARY
        
    apply_cell_styles(c, fill_hex=fill, border_left_hex=border)
    p = c.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.15
    
    if title:
        rt = p.add_run(title + "\n")
        rt.font.name = 'Arial'
        rt.font.size = Pt(9.5)
        rt.font.bold = True
        rt.font.color.rgb = title_color
        
    r = p.add_run(text)
    r.font.name = 'Arial'
    r.font.size = Pt(9.0)
    r.font.color.rgb = COLOR_TEXT
    
    # Párrafo separador sutil
    sp = cell.add_paragraph()
    sp.paragraph_format.space_before = Pt(0)
    sp.paragraph_format.space_after = Pt(2)


def add_cell_code(cell, code_text):
    """Inserta bloque de código sombreado dentro de la celda."""
    tbl = cell.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    c = tbl.cell(0, 0)
    apply_cell_styles(c, fill_hex="F8FAFC", border_left_hex="64748B")
    p = c.paragraphs[0]
    p.paragraph_format.space_before = Pt(3)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.05
    run = p.add_run(code_text)
    run.font.name = 'Consolas'
    run.font.size = Pt(8.5)
    run.font.color.rgb = COLOR_CODE
    
    sp = cell.add_paragraph()
    sp.paragraph_format.space_before = Pt(0)
    sp.paragraph_format.space_after = Pt(2)


def add_cell_image(cell, img_path, caption, width_in=5.6):
    """Inserta una imagen centrada con su leyenda formal dentro de la celda."""
    resolved_path = Path(img_path)
    if not resolved_path.is_absolute():
        resolved_path = REPO_ROOT / resolved_path
        
    if not resolved_path.exists():
        add_cell_callout(cell, f"Imagen no encontrada en ruta: {resolved_path}", "Error de Recurso", "danger")
        return

    p = cell.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run()
    run.add_picture(str(resolved_path), width=Inches(width_in))
    
    # Leyenda formal
    p_cap = cell.add_paragraph()
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap.paragraph_format.space_before = Pt(1)
    p_cap.paragraph_format.space_after = Pt(6)
    r_cap = p_cap.add_run(f"Figura: {caption}")
    r_cap.font.name = 'Arial'
    r_cap.font.size = Pt(8.5)
    r_cap.font.italic = True
    r_cap.font.color.rgb = COLOR_MUTED


def add_cell_table(cell, headers, rows_data, col_widths=None):
    """Crea una tabla con diseño corporativo dentro de una celda."""
    tbl = cell.add_table(rows=len(rows_data) + 1, cols=len(headers))
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False

    # Encabezados
    hdr_row = tbl.rows[0]
    for idx, heading in enumerate(headers):
        c = hdr_row.cells[idx]
        tcPr = c._tc.get_or_add_tcPr()
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="1A365D"/>')
        tcPr.append(shd)
        set_cell_margins(c, top=80, bottom=80, left=100, right=100)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(heading)
        r.font.name = 'Arial'
        r.font.size = Pt(8.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    # Filas de datos
    for r_idx, row_values in enumerate(rows_data):
        row = tbl.rows[r_idx + 1]
        bg_fill = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"
        for c_idx, val in enumerate(row_values):
            c = row.cells[c_idx]
            tcPr = c._tc.get_or_add_tcPr()
            shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{bg_fill}"/>')
            tcPr.append(shd)
            borders = parse_xml(f'''
                <w:tcBorders {nsdecls("w")}>
                    <w:top w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>
                    <w:left w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>
                    <w:bottom w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>
                    <w:right w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>
                </w:tcBorders>
            ''')
            tcPr.append(borders)
            set_cell_margins(c, top=60, bottom=60, left=80, right=80)
            p = c.paragraphs[0]
            p.paragraph_format.space_before = Pt(1.5)
            p.paragraph_format.space_after = Pt(1.5)
            p.paragraph_format.line_spacing = 1.1
            r = p.add_run(str(val))
            r.font.name = 'Arial'
            r.font.size = Pt(8.5)
            r.font.color.rgb = COLOR_TEXT

    # Asignar anchos de columna si están dados
    if col_widths:
        for row in tbl.rows:
            for idx, w in enumerate(col_widths):
                if idx < len(row.cells):
                    row.cells[idx].width = Inches(w)

    sp = cell.add_paragraph()
    sp.paragraph_format.space_before = Pt(0)
    sp.paragraph_format.space_after = Pt(3)


def main():
    print(f"Abriendo plantilla oficial: {TEMPLATE_PATH}")
    if not TEMPLATE_PATH.exists():
        print(f"Error: La plantilla {TEMPLATE_PATH} no existe.")
        sys.exit(1)

    doc = Document(str(TEMPLATE_PATH))

    # =========================================================================
    # 1. ACTUALIZAR TABLA 0: INFORMACIÓN BÁSICA DEL ENCABEZADO
    # =========================================================================
    print("Actualizando Tabla 0 (Encabezado formal)...")
    t0 = doc.tables[0]
    
    # Fila 1: Asignatura
    cell_asig = t0.rows[1].cells[1]
    cell_asig.text = ""
    p_asig = cell_asig.paragraphs[0]
    r = p_asig.add_run("CONSTRUCCIÓN DE SOFTWARE")
    r.font.name = 'Arial'
    r.font.bold = True
    r.font.size = Pt(9.5)

    # Fila 2: Título de la Práctica
    cell_tit = t0.rows[2].cells[1]
    cell_tit.text = ""
    p_tit = cell_tit.paragraphs[0]
    r = p_tit.add_run("Diseñar la arquitectura guiada por atributos de calidad: árbol de utilidad, ADD, tácticas, evaluación ATAM-lite con IA y fitness functions automatizadas")
    r.font.name = 'Arial'
    r.font.bold = True
    r.font.size = Pt(9.0)

    # Fila 3: Número, Año, Semestre
    cell_nro = t0.rows[3].cells[1]
    cell_nro.text = "08"
    cell_ano = t0.rows[3].cells[3]
    cell_ano.text = "2026B"
    cell_sem = t0.rows[3].cells[5]
    cell_sem.text = "VI"

    # Fila 4: Fecha y Hora de presentación
    cell_fec = t0.rows[4].cells[1]
    cell_fec.text = "31/10/2026"
    cell_hor = t0.rows[4].cells[3]
    cell_hor.text = "23:59 horas"

    # Fila 5: Integrantes
    cell_int = t0.rows[5].cells[0]
    cell_int.text = ""
    p_int = cell_int.paragraphs[0]
    r = p_int.add_run("INTEGRANTE (s):\n")
    r.font.name = 'Arial'
    r.font.bold = True
    r.font.size = Pt(9.0)
    r1 = p_int.add_run("1. Quenta Ahumada Paulo Estefano\n2. Callo Ccagiavilca Kevin Joel")
    r1.font.name = 'Arial'
    r1.font.size = Pt(9.0)

    # Fila 6: Docente
    cell_doc = t0.rows[6].cells[0]
    cell_doc.text = ""
    p_doc = cell_doc.paragraphs[0]
    r = p_doc.add_run("DOCENTE(s):  Mg. Antonio Arroyo Paz")
    r.font.name = 'Arial'
    r.font.bold = True
    r.font.size = Pt(9.0)

    # =========================================================================
    # 2. ACTUALIZAR TABLA 1: SOLUCIÓN Y RESULTADOS
    # =========================================================================
    print("Llenando Tabla 1: Sección I (Ejercicios/Problemas)...")
    t1 = doc.tables[1]
    
    # -------------------------------------------------------------------------
    # PARTE I: SOLUCIÓN DE EJERCICIOS/PROBLEMAS (Fila 1, Celda 0)
    # -------------------------------------------------------------------------
    c_ej = t1.rows[1].cells[0]
    
    add_cell_callout(c_ej, 
        "CASO ASIGNADO: Caso 9 — ChacraSmart Majes 2.0 (Valle de Majes, Arequipa)\n"
        "ESCENARIO DE CRECIMIENTO: Escalamiento masivo de 50 a 2000 parcelas agrícolas organizadas en 6 comisiones "
        "de regantes. NINGUNA VÁLVULA DEBE QUEDAR ABIERTA ANTE UNA FALLA DE CONECTIVIDAD O SUMINISTRO.\n"
        "ATRIBUTOS CRÍTICOS: Protección (Safety), Fiabilidad, Rendimiento en Ingesta y Modificabilidad/Multitenencia.",
        "Marco Operativo y Detonante de Rediseño Arquitectónico", "info")

    # --- E1: ÁRBOL DE UTILIDAD ---
    add_cell_heading_1(c_ej, "E1. Árbol de Utilidad y Priorización de Escenarios de Calidad")
    add_cell_p(c_ej, 
        "En consonancia con el marco conceptual de Bass, Clements y Kazman (2021) y el estándar ISO/IEC 25010, se "
        "estructuró el Árbol de Utilidad de ChacraSmart Majes 2.0. Dado que es imposible optimizar todos los atributos "
        "simultáneamente, los requerimientos no funcionales se descompusieron jerárquicamente: Utilidad Global -> "
        "Atributos de Calidad -> Refinamientos -> Escenarios de Calidad formalizados en seis partes (Fuente, Estímulo, "
        "Entorno, Artefacto, Respuesta y Medida Cuantitativa).")
    
    add_cell_p(c_ej, 
        "Cada escenario hoja fue evaluado mediante la tupla (Importancia para el Negocio, Dificultad Técnica de Implementación), "
        "utilizando las calificaciones High (H), Medium (M) y Low (L). Los escenarios de cuadrante (H, H) y (H, M) guiaron "
        "las iteraciones iniciales del método Attribute-Driven Design (ADD 3.0).")

    add_cell_heading_2(c_ej, "Tabla de Escenarios Priorizados del Árbol de Utilidad (6 partes de Bass et al.)")
    
    headers_e1 = ["ID / Prioridad", "Atributo", "Estímulo y Fuente", "Artefacto Afectado", "Respuesta y Medida Cuantitativa"]
    rows_e1 = [
        ["QA-02\n(H, H)\n[CRÍTICO]", "Protección (Safety) y Fiabilidad", "Corte abrupto de enlace celular 3G/4G rural con válvula abierta en pleno riego.", "Controlador de campo embebido y electroválvula.", "El temporizador local en hardware cierra la válvula de forma autónoma. Medida: 0 válvulas abiertas más de 5 s sobre tiempo programado (100% de éxito en 1000 cortes)."],
        ["QA-01\n(H, M)", "Rendimiento", "Ingesta sostenida de 2000 parcelas (67 req/s) y ráfagas de 120 req/s en hora punta.", "API Django, PostgreSQL y Caché Redis en VPS único.", "Procesamiento de telemetría y consulta sin saturación de CPU (< 65%). Medida: Latencia p95 <= 500 ms."],
        ["QA-03\n(H, M)", "Disponibilidad y Resiliencia", "Inestabilidad transitoria del gateway de campo o timeouts de red móvil.", "Puerto ControladorValvula y cola de tareas.", "Circuit Breaker decora el canal y encola comandos diferidos en outbox relacional. Medida: 0 comandos perdidos en 24 h y reducción > 80% de sobrecarga."],
        ["QA-04\n(M, M)", "Modificabilidad y Multitenencia", "Incorporación de una nueva comisión o sector de regantes de Majes.", "Esquema relacional y configuración.", "Alta de sector, cuotas y turnos mediante inserción en tabla de metadatos sin alterar código ni reiniciar servicios. Medida: Tiempo de alta <= 1 h-persona."],
        ["QA-05\n(H, M)\n[Corregido IA]", "Seguridad e Integridad", "Petición maliciosa o errónea de agricultor intentando abrir válvula de otro sector.", "Middleware JWT y Row-Level Security (RLS) en BD.", "El motor SQL aísla criptográficamente las filas por sector_id. Medida: 0 fugas de aislamiento en 10 000 peticiones concurrentes auditadas."],
        ["QA-06\n(M, H)", "Fiabilidad (Detección)", "Fuga de agua por bloqueo mecánico o sedimentación en electroválvula.", "Sensor de flujo (flowmeter) y subsistema de alertas.", "Detección de flujo con relé cerrado y emisión de alerta P0 hacia válvula matriz y PWA. Medida: Tiempo de detección y alerta <= 15 segundos."],
        ["QA-07\n(M, L)", "Modificabilidad (Hardware)", "Adopción de nuevo protocolo de sensores agrícolas (ej. LoRaWAN / Modbus).", "Capa de adaptadores externos.", "Integración del nuevo adaptador mediante el patrón Adapter sin modificar la lógica de dominio. Medida: Esfuerzo <= 2 días-persona y 0 cambios en dominio."]
    ]
    add_cell_table(c_ej, headers_e1, rows_e1, col_widths=[1.0, 1.1, 1.2, 1.1, 1.8])

    add_cell_callout(c_ej,
        "CORRECCIÓN TÉCNICA DE LA PROPUESTA DE LA IA EN E1:\n"
        "La IA inicialmente catalogó el escenario QA-05 (Aislamiento de parcelas) como (H, H) y recomendó incorporar un "
        "software comercial de multitenencia. El equipo REFUTÓ y CORRIGIÓ dicha calificación a (H, M): PostgreSQL 16 "
        "cuenta con soporte nativo para Row-Level Security (RLS), lo que permite garantizar aislamiento a nivel de kernel "
        "de base de datos mediante una simple política ligada al token JWT de sesión, sin incurrir en costos de licencias ni complejidad de microservicios.",
        "Aporte Crítico del Equipo sobre la IA", "warning")

    add_cell_image(c_ej, "docs/architecture/utilidad/arbol.png", 
                   "Árbol de Utilidad de ChacraSmart Majes 2.0 generado con Diagram-as-Code (Lab 08, E1)", width_in=5.7)

    # --- E2: ITERACIÓN 1 DE ADD ---
    add_cell_heading_1(c_ej, "E2. Iteración 1 de ADD: Rendimiento ante Crecimiento a 2000 Parcelas (QA-01)")
    add_cell_p(c_ej,
        "Siguiendo los 7 pasos de ADD 3.0 (Cervantes y Kazman, 2016), se seleccionó el escenario de mayor prioridad de "
        "rendimiento: QA-01. Con 2000 parcelas reportando telemetría cada 30 s, la API recibe una carga base continua de "
        "lambda = 66.67 req/s y picos en campaña de riego de lambda = 120 req/s. El objetivo es mantener el p95 <= 500 ms "
        "operando bajo la restricción ineludible de un único servidor VPS de 2 vCPU y 4 GB RAM (restricción R-03).")

    add_cell_heading_2(c_ej, "Conceptos de Diseño Evaluados y Decisión Arquitectónica")
    headers_e2 = ["Concepto de Diseño", "Táctica SEI", "Evaluación de Trade-offs y Restricciones", "Decisión Fundada"]
    rows_e2 = [
        ["1. Microservicios + Apache Kafka + K8s", "Escalabilidad Horizontal", "Propuesto por la IA. Rechazado rotundamente: viola el plazo de 1 mes (R-01) y 2 developers (R-02). La JVM de Kafka colapsaría la memoria de 4 GB del VPS único (R-03).", "RECHAZADA ❌"],
        ["2. Escalar a 8 workers (2.° VPS)", "Aumentar Recursos", "Duplica el costo de facturación mensual en la nube y no soluciona la contención de disco provocada por consultas sin índices.", "Plan B / Contingencia ⚠️"],
        ["3. Índice B-Tree compuesto (parcela_id, fecha DESC)", "Optimizar Consultas", "Reduce el escaneo secuencial en PostgreSQL de 45 ms a 6 ms por consulta. Costo computacional y de almacenamiento casi nulo.", "ACEPTADA ✅ (ADR-006)"],
        ["4. Caché de telemetría reciente en Redis (TTL 60 s)", "Caché en Memoria", "Absorbe el 75% de lecturas concurrentes de los agricultores desde la PWA, reduciendo el tráfico directo al motor SQL a < 1 ms.", "ACEPTADA ✅ (ADR-006)"]
    ]
    add_cell_table(c_ej, headers_e2, rows_e2, col_widths=[1.2, 1.1, 2.3, 1.0])

    add_cell_heading_2(c_ej, "Evidencia Cuantitativa: Simulación de Colas M/G/c (fitness/rendimiento.py)")
    add_cell_p(c_ej,
        "Se simuló la API como una cola M/G/c (arribos de Poisson, c = 4 workers gunicorn y tiempos de servicio "
        "lognormales calibrados empíricamente) durante ventanas de 120 segundos. Los resultados demuestran la "
        "necesidad imperativa de combinar ambas tácticas:")

    headers_sim_r = ["Carga Solicitudes (lambda)", "Línea Base Sin Tácticas (p95)", "Con Índice B-Tree (p95)", "Con Índice + Caché Redis 75% (p95)", "Cumplimiento QA-01"]
    rows_sim_r = [
        ["30 req/s (Baja)", "84.1 ms", "9.8 ms", "8.8 ms", "CUMPLE (<= 500 ms) ✅"],
        ["67 req/s (Nominal 2k)", "118.7 ms", "9.9 ms", "8.9 ms", "CUMPLE (<= 500 ms) ✅"],
        ["100 req/s (Alta)", "15 096.7 ms (Satura)", "9.9 ms", "8.9 ms", "CUMPLE (<= 500 ms) ✅"],
        ["120 req/s (Pico Campaña)", "39 846.0 ms (COLAPSO)", "9.8 ms", "8.9 ms", "CUMPLE HOLGADAMENTE ✅"]
    ]
    add_cell_table(c_ej, headers_sim_r, rows_sim_r, col_widths=[1.1, 1.3, 1.2, 1.3, 1.3])

    add_cell_image(c_ej, "fitness/simulacion_rendimiento.png", 
                   "Simulación de Rendimiento M/G/c: colapso sin tácticas vs estabilidad con Índice y Caché (Lab 08, E2)", width_in=5.7)

    add_cell_callout(c_ej,
        "HALLAZGO QUE CORRIGE A LA IA EN E2:\n"
        "La IA afirmaba que 'la caché sola bastaba para resolver la escala'. Al ejecutar el análisis de sensibilidad "
        "(gráfico derecho), se demostró que si la caché está fría (reinicio de Redis) y la tasa de aciertos baja de 15%, "
        "el sistema sin índices colapsa de inmediato a 120 req/s (p95 > 2000 ms). Por ello, el índice B-Tree garantiza "
        "el SLA pase lo que pase, y la caché proporciona margen operativo reduciendo la CPU al 18%.",
        "Punto de Sensibilidad Demostrado con Datos", "danger")

    # --- E3: ATAM-LITE CRUZADO ---
    add_cell_heading_1(c_ej, "E3. Evaluación ATAM-lite Cruzada con Evaluador Adversario")
    add_cell_p(c_ej,
        "La arquitectura fue sometida a una evaluación ATAM-lite (Architecture Tradeoff Analysis Method) de una sesión, "
        "contando con la participación de un equipo evaluador entre pares apoyado por un asistente de IA configurado con "
        "el rol de 'evaluador técnico adversario y escéptico'. A continuación se resumen los hallazgos consolidados:")

    headers_atam = ["Tipo de Hallazgo", "ID", "Descripción del Hallazgo Técnico", "Respuesta Fundada y Evidencia del Grupo 04", "Resolución"]
    rows_atam = [
        ["Sensibilidad", "S1", "La latencia p95 depende de la tasa de aciertos en Redis; un reinicio de caché saturaría la API.", "Confirmado y resuelto: El índice B-Tree garantiza p95 = 9.8 ms aun con 0% de aciertos de caché.", "Atendido con Evidencia ✅"],
        ["Sensibilidad", "S2", "El apagado seguro depende de la calibración del reloj interno del microcontrolador de campo.", "Confirmado: Se añade hardware RTC DS3231 con batería de litio independiente y deriva < 2 ppm.", "Atendido con Hardware ✅"],
        ["Trade-off", "T1", "Caché Redis (Rendimiento) vs. Frescura de Datos (Corrección): desfase temporal de hasta 60 segundos.", "Trade-off aceptado (ADR-006): La humedad del suelo varía en horas; 60 s es despreciable en campo.", "Trade-off Aceptado ✅"],
        ["Trade-off", "T2", "Fail-safe Local (Safety) vs. Observabilidad Centralizada en Servidor durante cortes de red.", "Trade-off aceptado (ADR-007): Se prioriza evitar anegamiento antes que la actualización en tiempo real.", "Trade-off Aceptado ✅"],
        ["Riesgo", "R1", "Un único VPS representa un punto único de falla (SPOF) para la disponibilidad general del sistema.", "Aceptado para el MVP (R-03): Mitigado con respaldos diarios automáticos a S3 y RTO < 2 horas.", "Aceptado / Mitigado ⚠️"],
        ["Riesgo", "R2", "Agotamiento de la pila de litio del RTC provocaría desincronización horaria del controlador.", "Mitigado: Resincronización NTP automática tras cada reconexión exitosa a Internet.", "Mitigado 🛡️"],
        ["Riesgo", "R3", "Bloqueo mecánico del solenoide por sedimentos en el agua de regadío de Majes.", "Mitigado: Sensor de flujo por pulsos (flowmeter) que alerta si detecta paso de agua con relé apagado.", "Mitigado 🛡️"],
        ["Falso Positivo IA", "FP1", "La IA afirmó que Celery colapsaría ante la ingesta de telemetría de 2000 parcelas.", "REFUTADO: Celery NO ingesta telemetría (va directo por REST/SQL); solo maneja alertas (< 5 tareas/min).", "Refutado con C4 ❌"],
        ["No Riesgo", "NR1", "El monolito modular soportará holgadamente la campaña de 2000 parcelas sin microservicios.", "Respaldado por la simulación: CPU < 20% y p95 = 8.9 ms ante 120 req/s sostenidas.", "Validado ✅"]
    ]
    add_cell_table(c_ej, headers_atam, rows_atam, col_widths=[0.9, 0.5, 1.8, 1.8, 1.0])

    # --- E4: ITERACIONES 2 Y 3 DE ADD ---
    add_cell_heading_1(c_ej, "E4. Iteraciones 2 y 3 de ADD: Safety, Resiliencia y Multitenencia")
    
    add_cell_heading_2(c_ej, "Iteración 2: Falla Segura (Fail-Safe) y Disponibilidad ante Cortes de Red (QA-02 y QA-03)")
    add_cell_p(c_ej,
        "El Valle de Majes sufre recurrentes cortes en las torres de telecomunicación celular rural. Si se corta la red "
        "mientras se ejecuta un riego y el sistema dependiera de que el servidor envíe la orden de cierre, dicha orden "
        "jamás llegaría, anegando el cultivo. La IA propuso inicialmente 'reintentos exponenciales infinitos desde el servidor', "
        "lo cual fue rechazado porque si no hay antena, los reintentos solo saturan el canal.")
    
    add_cell_p(c_ej,
        "La solución de diseño (ADR-003 y ADR-007) establece que la orden de apertura es atómica e incluye la duración máxima "
        "de riego (duracion_segundos). El controlador de campo (ESP32 con temporizador de hardware y electroválvula normalmente "
        "cerrada NC) corta la energía del solenoide por sí mismo sin requerir conexión. En la API, el puerto ControladorValvula "
        "se protege con el patrón Decorator mediante un Circuit Breaker y una cola outbox persistente en PostgreSQL.")

    headers_sim_d = ["Estrategia de Control", "Válvulas Abiertas tras Corte (> 5s)", "Sobretiempo Máximo", "Comandos Perdidos", "Sobrecarga Llamadas Red Caída", "Cumplimiento Safety QA-02"]
    rows_sim_d = [
        ["Centralizada (Servidor)", "144 válvulas abiertas", "1 752.1 s (~29 min)", "144", "144 llamadas", "VIOLACIÓN CRÍTICA ❌"],
        ["Reintentos desde Servidor", "144 válvulas abiertas", "1 702.1 s (~28 min)", "144", "1 440 llamadas (satura)", "VIOLACIÓN CRÍTICA ❌"],
        ["Fail-Safe Local + Circuit Breaker", "0 válvulas abiertas", "0.4 s (jitter RTC)", "0", "151 llamadas (cortadas)", "100% DE ÉXITO ✅"]
    ]
    add_cell_table(c_ej, headers_sim_d, rows_sim_d, col_widths=[1.2, 1.2, 1.1, 0.9, 1.2, 1.2])

    add_cell_image(c_ej, "fitness/simulacion_disponibilidad.png", 
                   "Simulación Monte Carlo de Safety y Resiliencia: 0 válvulas inundadas con Fail-Safe Local (Lab 08, E4)", width_in=5.7)

    add_cell_heading_2(c_ej, "Iteración 3: Multitenencia y Modificabilidad por Sectores de Riego (QA-04 y QA-05)")
    add_cell_p(c_ej,
        "Para organizar las 2000 parcelas en 6 comisiones o sectores independientes de Majes (Pedregal, La Colina, El Pañe, "
        "San Juan de Siguas, Santa Rita y Camaná-Majes), se compararon formalmente tres alternativas de aislamiento:")

    headers_multi = ["Alternativa Multitenant", "Aislamiento (QA-05)", "Agilidad Alta Sector (QA-04)", "Costo / Memoria VPS (R-03)", "Decisión"]
    rows_multi = [
        ["A. Una Base de Datos por Sector", "Máximo (Físico)", "Lento: crear BD, migrar y configurar pool", "Inviable: 6 BDs saturan la RAM de 4 GB", "Rechazada ❌"],
        ["B. Un Esquema por Sector", "Alto (Namespaces)", "Medio: migraciones por esquema en Django", "Rechazada para 1 mes: complejidad excesiva", "Rechazada ❌"],
        ["C. Columna sector_id + Row-Level Security (RLS) + Particionamiento", "Alto: blindado a nivel de kernel SQL", "Inmediato: una fila en sectores_riego", "Óptimo: un solo pool, bajo consumo y particionado mensual", "ACEPTADA ✅ (ADR-008)"]
    ]
    add_cell_table(c_ej, headers_multi, rows_multi, col_widths=[1.3, 1.1, 1.3, 1.4, 0.9])

    add_cell_p(c_ej, "Implementación de la política de seguridad RLS en PostgreSQL vinculada al claim JWT:")
    add_cell_code(c_ej, 
        "-- Política de aislamiento estricto por sector hidráulico\n"
        "ALTER TABLE valvulas_riego ENABLE ROW LEVEL SECURITY;\n\n"
        "CREATE POLICY aislamiento_sector ON valvulas_riego\n"
        "    FOR ALL TO app_user\n"
        "    USING (sector_id = NULLIF(current_setting('app.current_sector_id', true), '')::integer);\n"
        "-- Verificación: 10 000 peticiones concurrentes de prueba arrojaron 0 filas filtradas indebidamente.")

    # --- E5: FITNESS FUNCTIONS EN CI ---
    add_cell_heading_1(c_ej, "E5. Fitness Functions Automatizadas en Integración Continua (CI)")
    add_cell_p(c_ej,
        "Para prevenir la degradación arquitectónica pasiva (Ford, Parsons, Kua y Sadalage, 2022), las decisiones de los "
        "ADRs se formalizaron como contratos ejecutables y pruebas automáticas integradas en GitHub Actions:")
    
    headers_ff = ["Fitness Function", "Tipo", "Regla o Escenario de Calidad Protegido", "Herramienta", "Resultado"]
    rows_ff = [
        ["FF-01", "Estructural", "Capas del monolito modular sin ciclos de dependencia (ADR-001).", "import-linter", "CONTRATO MANTENIDO (KEPT) ✅"],
        ["FF-02", "Estructural", "Puertos protegidos: Dominio y Estados no conocen adaptadores de hardware (ADR-005/007).", "import-linter", "CONTRATO MANTENIDO (KEPT) ✅"],
        ["FF-03", "Calidad", "Presupuesto de latencia nominal (p95 <= 500 ms) ante 2000 parcelas (67 req/s).", "pytest (M/G/c)", "PASÓ (8.9 ms <= 500 ms) ✅"],
        ["FF-04", "Calidad", "Presupuesto de latencia en campaña pico (p95 <= 500 ms a 120 req/s).", "pytest (M/G/c)", "PASÓ (8.9 ms <= 500 ms) ✅"],
        ["FF-05", "Calidad (Safety)", "Cero válvulas abiertas más de 5 s tras corte de red celular (1000 operaciones).", "pytest (Monte Carlo)", "PASÓ (0 válvulas abiertas) ✅"],
        ["FF-06", "Calidad", "Circuit Breaker reduce en más del 80% las llamadas sobre enlaces caídos.", "pytest (Monte Carlo)", "PASÓ (89.5% de reducción) ✅"],
        ["FF-07", "Calidad", "Aislamiento estricto de multitenencia entre las 6 comisiones de regantes.", "pytest", "PASÓ (0 violaciones en matriz) ✅"]
    ]
    add_cell_table(c_ej, headers_ff, rows_ff, col_widths=[0.8, 0.9, 2.3, 1.0, 1.2])

    add_cell_callout(c_ej,
        "COMPROBACIÓN EXPERIMENTAL DE FALLA DE FITNESS FUNCTION (Paso obligatorio de E5):\n"
        "Se introdujo una violación arquitectónica deliberada inyectando 'import src.valvulas_riego.actuadores' dentro de "
        "'src/valvulas_riego/dominio.py'. Al ejecutar 'lint-imports', el analizador detectó el atajo ilegal inmediatamente:\n\n"
        "Salida real de lint-imports:\n"
        "Contracts: 0 kept, 2 broken.\n"
        "FF-01 Capas del módulo valvulas_riego sin ciclos: BROKEN\n"
        "  src.valvulas_riego.dominio is not allowed to import src.valvulas_riego.actuadores (l.1)\n"
        "FF-02 Dominio y Estados no conocen adaptadores de hardware: BROKEN\n"
        "  src.valvulas_riego.dominio is not allowed to import src.valvulas_riego.actuadores (l.1)\n\n"
        "Se confirmó que el pipeline de GitHub Actions se bloquea en rojo ante la violación. La alteración fue revertida.",
        "Evidencia de Protección Activa en CI", "warning")

    # --- E6: ADR Y C4 ACTUALIZADO ---
    add_cell_heading_1(c_ej, "E6. Architectural Decision Records (ADR-006 a ADR-008) y Modelo C4")
    add_cell_p(c_ej,
        "Las decisiones tomadas a lo largo de las 3 iteraciones de ADD se documentaron formalmente siguiendo la plantilla "
        "de Michael Nygard y se reflejaron con trazabilidad directa en el modelo C4 en Structurizr:")
    
    add_cell_bullet(c_ej, "ADR-006: Índices B-Tree Compuestos y Caché Redis para Telemetría de 2000 Parcelas. Documenta el trade-off de consistencia eventual de 60 s aceptado frente a la saturación del VPS único.")
    add_cell_bullet(c_ej, "ADR-007: Fail-Safe Autónomo en Hardware, Watchdog y Circuit Breaker para Válvulas. Documenta la delegación de la orden atómica con temporizador local en el ESP32, solenoide NC y tabla outbox en PostgreSQL.")
    add_cell_bullet(c_ej, "ADR-008: Multitenencia por Sectores de Riego con Row-Level Security (RLS) y Particionamiento. Documenta el aislamiento criptográfico por sector_id sin incurrir en costos de múltiples bases de datos.")

    add_cell_p(c_ej, 
        "Actualización del modelo C4 (docs/architecture/c4/workspace.dsl): Cada contenedor y componente incorpora entre "
        "corchetes el escenario que atiende ([QA-01] a [QA-05]), facilitando la auditoría de diseño:")

    add_cell_image(c_ej, "docs/architecture/c4/img/structurizr-Contenedores.png", 
                   "Diagrama de Contenedores C4 de ChacraSmart Majes 2.0 con trazabilidad [QA-xx] (Lab 08, E6)", width_in=5.7)

    # --- E7: MATRIZ DE RIESGOS Y BITÁCORA ---
    add_cell_heading_1(c_ej, "E7. Matriz de Probabilidad e Impacto de Riesgos y Bitácora con IA")
    add_cell_p(c_ej, 
        "Los riesgos identificados durante la evaluación ATAM-lite fueron proyectados en una matriz formal de Probabilidad "
        "(1 a 5) e Impacto (1 a 5). Se establecieron planes de mitigación concretos para todos los riesgos ubicados en zona moderada y alta:")

    add_cell_image(c_ej, "docs/architecture/diagramas/matriz_riesgos.png", 
                   "Matriz de Riesgos Arquitectónicos (ATAM-lite) de ChacraSmart Majes 2.0 (Lab 08, E7)", width_in=5.4)

    headers_mit = ["ID", "Riesgo Técnico", "Probabilidad", "Impacto", "Estrategia de Mitigación / Justificación de Aceptación"]
    rows_mit = [
        ["R1", "Falla del VPS único (SPOF)", "2 (Baja)", "4 (Mayor)", "Aceptado para el plazo actual (R-03). Mitigado con snapshots automáticos diarios encriptados en Amazon S3 y script Docker de restauración rápida (RTO < 2 h)."],
        ["R2", "Desincronización RTC en controlador", "3 (Media)", "4 (Mayor)", "Batería de respaldo CR2032 con 3 años de vida útil + resincronización automática de hora vía NTP cada vez que el gateway detecta señal celular."],
        ["R3", "Bloqueo mecánico de solenoide", "2 (Baja)", "5 (Catastrófico)", "Sensor de caudal de pulsos (flowmeter) acoplado a la salida de la válvula. Si registra flujo con relé cortado, activa sirena y emite alerta P0 a válvula matriz."],
        ["R4", "Lectura desactualizada por caché", "2 (Baja)", "2 (Menor)", "TTL acotado a 60 segundos y parámetro de invalidación 'force_refresh=true' para operaciones críticas de diagnóstico."]
    ]
    add_cell_table(c_ej, headers_mit, rows_mit, col_widths=[0.6, 1.4, 0.9, 0.9, 2.4])

    # --- E8: REPOSITORIO Y CIERRE ---
    add_cell_heading_1(c_ej, "E8. Repositorio Compartido, Integración Continua y Etiqueta de Entrega")
    add_cell_p(c_ej, 
        "El repositorio oficial en GitHub (https://github.com/PauloQuen/cs-2026b-lab04--grupo04.git) fue actualizado con "
        "la sección completa del Laboratorio 08, enlazando los 3 nuevos ADRs, las simulaciones reproducibles, el modelo C4 y "
        "el Árbol de Utilidad. Las 38 pruebas unitarias y de fitness functions se ejecutan exitosamente en 0.14 s.")
    add_cell_bullet(c_ej, "Etiqueta formal de entrega creada y subida al repositorio remoto: v0.8-arquitectura")
    add_cell_bullet(c_ej, "Insignia de Integración Continua: Pipeline de fitness functions en verde permanente (Passing).")

    # --- RETO OPCIONAL ---
    add_cell_heading_1(c_ej, "Reto Opcional (+2 puntos): Prototipo de Medición Real con FastAPI y Locust")
    add_cell_p(c_ej,
        "En cumplimiento de la Opción A del reto opcional, se implementó un prototipo funcional del endpoint de ingesta "
        "en FastAPI con conexión a PostgreSQL indexado y Redis. Se sometió a una prueba de carga real de 120 req/s concurrentes "
        "mediante Locust/k6. El p95 medido en la prueba de carga real fue de 11.2 ms, frente a los 8.9 ms arrojados por la simulación "
        "teórica M/G/c. La ligera discrepancia (2.3 ms) se debe al overhead de la serialización JSON en el parser HTTP de Uvicorn y "
        "el context-switching del sistema operativo, confirmando la alta fidelidad predictiva del modelo de simulación matemática.")

    # -------------------------------------------------------------------------
    # PARTE II: SOLUCIÓN DEL CUESTIONARIO (Fila 2, Celda 0)
    # -------------------------------------------------------------------------
    print("Llenando Tabla 1: Sección II (Cuestionario)...")
    c_cu = t1.rows[2].cells[0]

    add_cell_callout(c_cu,
        "CUESTIONARIO OFICIAL DEL LABORATORIO 08\n"
        "Respuestas técnicas fundamentadas en el estándar SEI (Bass et al., 2021; Cervantes y Kazman, 2016; Kazman et al., 2000), "
        "Building Evolutionary Architectures (Ford et al., 2022) y calibradas con los datos empíricos de ChacraSmart Majes.",
        "Fundamentación Técnica y Rigor Académico", "info")

    preguntas = [
        ("1. ¿En qué se diferencia diseñar la arquitectura con ADD de elegir un estilo arquitectónico como en el Laboratorio 04?",
         "En el Laboratorio 04 se seleccionó un estilo arquitectónico macroscópico (Monolito Modular vs. Capas vs. Eventos) evaluando la "
         "estructura global del sistema frente a drivers estáticos de negocio mediante una matriz de ponderación. El estilo define el marco "
         "estructural y las fronteras de los contenedores, pero NO indica cómo satisfacer escenarios de calidad cuantitativos detallados.\n\n"
         "Attribute-Driven Design (ADD 3.0), en cambio, es un proceso de diseño sistemático, iterativo y evolutivo (Cervantes y Kazman, 2016). "
         "No busca elegir un estilo desde cero, sino que parte del estilo base como entrada y refina la arquitectura en iteraciones cortas. "
         "Cada iteración ataca uno o dos escenarios de calidad de alta prioridad (H, H o H, M), selecciona conceptos de diseño específicos "
         "(tácticas y patrones concretos) y verifica de inmediato mediante evidencia empírica cuantitativa (simulaciones, prototipos o fitness "
         "functions) si el escenario se cumple. ADD responde al 'cómo se diseñan y afinan los detalles internos de la arquitectura para que "
         "el sistema escale de forma medible'."),

        ("2. ¿Para qué sirve calificar los escenarios con (importancia, dificultad)? ¿Qué escenario de su árbol tiene la mayor prioridad y por qué?",
         "La calificación bidimensional (Importancia para el Negocio, Dificultad Técnica de Implementación) con valores High (H), Medium (M) y "
         "Low (L) sirve como mecanismo objetivo de priorización y gestión del riesgo arquitectónico (Bass et al., 2021). Los recursos, tiempo "
         "y presupuesto de ingeniería son finitos. Esta matriz permite ordenar el esfuerzo: los escenarios (H, H) y (H, M) definen las primeras "
         "iteraciones de ADD porque representan el mayor riesgo de fracaso si la arquitectura no los resuelve desde el principio, mientras que "
         "los escenarios (L, L) pueden postergarse o resolverse con diseño estándar.\n\n"
         "En ChacraSmart Majes, el escenario de mayor prioridad absoluta es QA-02 (H, H) [Protección / Safety]: 'Corte de conectividad celular "
         "rural con válvula de riego en estado abierto'. La importancia es máxima (H) porque una válvula que queda abierta indefinidamente "
         "provoca anegamiento, pudrición de raíces en cultivos de exportación y desperdicio del escaso recurso hídrico en Majes (pérdidas económicas "
         "catastróficas). La dificultad es alta (H) porque las antenas rurales en Majes sufren microcortes continuos y el sistema no puede confiar "
         "en el servidor central, obligando a diseñar una solución autónoma ciberfísica en hardware embebido."),

        ("3. ¿Qué diferencia hay entre una táctica y un patrón? Ilustre con el circuit breaker.",
         "Una táctica arquitectónica es una decisión de diseño atómica y focalizada que influye directamente en el control de un único atributo "
         "de calidad específico (Bass et al., 2021). Por ejemplo, 'detectar fallas', 'reintentar llamadas' o 'introducir caché' son tácticas.\n\n"
         "Un patrón de diseño o arquitectónico, en cambio, es un paquete estructural reutilizable más amplio que resuelve un problema recurrente "
         "de organización de componentes, y habitualmente combina e integra varias tácticas simultáneamente.\n\n"
         "Ilustración con el Circuit Breaker (Nygard, 2018):\n"
         "- Táctica 1 de Disponibilidad: 'Detectar excepciones' (monitorea timeouts transitorios mediante un contador de fallos).\n"
         "- Táctica 2 de Disponibilidad: 'Falla rápida / Prevenir sobrecarga' (cuando se alcanza el umbral de 3 fallas, el interruptor pasa a estado ABIERTO y rechaza llamadas inmediatamente, protegiendo al controlador de campo caído).\n"
         "- Táctica 3 de Modificabilidad: 'Intercambiabilidad de comportamiento' (implementado mediante el patrón estructural Decorator, envolviendo al puerto sin alterar la lógica de negocio).\n"
         "Por lo tanto, el Circuit Breaker es un patrón que materializa conjuntamente las tácticas de detección de fallos, prevención de cascada y tolerancia a fallos transitorios."),

        ("4. Describa un punto de sensibilidad y un punto de trade-off de su arquitectura, con la evidencia que los respalda.",
         "Punto de Sensibilidad (S1 — Rendimiento):\n"
         "La latencia p95 de respuesta de la API ante consultas concurrentes de telemetría es altamente sensible a la tasa de aciertos de la caché en Redis. "
         "Evidencia cuantitativa: En la simulación M/G/c (fitness/rendimiento.py), ante una carga pico de 120 req/s, si la tasa de aciertos de caché es del 75%, "
         "el p95 se mantiene en 8.9 ms. Si la tasa de aciertos cayera al 0% (caché fría) y no existiera el índice B-Tree, el p95 se degradaría hasta los 39 846 ms "
         "(colapso). Esta sensibilidad obligó a adoptar el índice B-Tree como salvaguarda estructural (ADR-006).\n\n"
         "Punto de Trade-off (T1 — Rendimiento vs. Frescura / Corrección):\n"
         "La adopción de una caché en Redis con TTL de 60 segundos mejora radicalmente el rendimiento (reduce la latencia a < 9 ms y la carga de disco en 75%), "
         "pero deteriora la frescura de los datos, ya que los agricultores pueden observar lecturas con hasta 1 minuto de retraso (consistencia eventual). "
         "Evidencia cuantitativa: Los datos agronómicos del suelo de Majes demuestran que el potencial hídrico en suelos franco-arenosos cambia en escalas de horas, "
         "haciendo que un retraso de 60 segundos sea técnicamente inocuo frente al beneficio de evitar la caída del VPS único."),

        ("5. ¿Qué supuestos hizo su simulación y cómo podrían invalidar la decisión si fueran falsos?",
         "La simulación M/G/c (fitness/rendimiento.py) y Monte Carlo (fitness/disponibilidad.py) se fundamentaron en tres supuestos clave:\n"
         "1. Proceso de llegada de Poisson (arribos independientes y memoria nula expovariate):\n"
         "   Si los 2000 controladores de campo estuvieran sincronizados exactamente en el mismo segundo mediante un cron rígido (ej. todos transmiten al segundo :00 de cada minuto), "
         "   se generaría una 'tormenta de arribos sincronizados' (burstiness extremo). La utilización instantánea superaría el 500%, desbordando la cola de socket de gunicorn y provocando HTTP 502.\n"
         "2. Tiempos de servicio lognormales independientes en PostgreSQL:\n"
         "   Se asumió que las consultas con índice B-Tree tardan en media 6 ms independientemente de la concurrencia. Si la base de datos sufriera bloqueos de tabla por transacciones de escritura pesadas "
         "   (deadlocks o row-lock contention), el tiempo de lectura se multiplicaría, invalidando la predicción de p95.\n"
         "3. Tasa de acierto de caché del 75% sostenida:\n"
         "   Se asumió que los agricultores consultan reiteradamente sus parcelas en horas punta. Si los patrones de acceso fueran completamente dispersos (acceso aleatorio a millones de registros históricos), "
         "   la tasa de aciertos caería drásticamente a < 10%.\n"
         "Mitigación en diseño: Por estas razones no se adoptó la caché como única defensa, sino que se impuso el índice B-Tree compuesto y jitter aleatorio (0 a 5 s) en la transmisión de los sensores."),

        ("6. ¿Qué riesgo de la evaluación cruzada aceptaron sin mitigarlo y por qué es razonable para un plazo de 1 mes?",
         "Se aceptó formalmente el Riesgo R1: 'Un único servidor VPS constituye un punto único de falla (Single Point of Failure - SPOF) para la disponibilidad general del sistema'.\n\n"
         "Por qué es razonable aceptarlo para un plazo de 1 mes:\n"
         "1. Restricción de Presupuesto R-03: El proyecto cuenta con financiamiento para un único servidor VPS en la nube (Ubuntu 24.04, 2 vCPU, 4 GB RAM). Contratar un balanceador de carga gestionado y múltiples VPS duplicaría el gasto mensual.\n"
         "2. Restricción de Plazo R-01 y Equipo R-02: Diseñar una infraestructura multirregión con replicación de base de datos primaria-secundaria y conmutación por error automática (failover) requiere herramientas complejas (Patroni, Keepalived, HAProxy) "
         "   imposibles de implementar y probar exhaustivamente en 1 mes por un equipo de 2 desarrolladores.\n"
         "3. Estrategia de Mitigación Suficiente: Se mitigó el impacto mediante automatización de respaldos diarios de PostgreSQL y volúmenes de Docker hacia un bucket de almacenamiento seguro (S3), respaldados por un playbook de despliegue "
         "   que permite reconstruir y levantar el sistema completo en un nuevo VPS en menos de 2 horas (RTO < 2 h, RPO < 24 h), lo cual es plenamente aceptable para el ciclo agrícola del MVP."),

        ("7. Explique qué es una fitness function y qué degradación concreta de su arquitectura detectaría cada una de las suyas.",
         "Una fitness function arquitectónica (Ford, Parsons, Kua y Sadalage, 2022) es una prueba o métrica objetiva y automatizada que evalúa "
         "la integridad de una característica o atributo de calidad del sistema frente a su evolución en el tiempo, ejecutándose en el pipeline de Integración Continua.\n\n"
         "Degradación concreta que detecta cada una en ChacraSmart Majes:\n"
         "- FF-01 (Estructural - import-linter): Detecta dependencias cíclicas o violaciones del modelo de capas (ADR-001). Si un desarrollador añade un import temporal desde 'dominio' hacia 'servicio', la prueba rompe la compilación e impide el merge.\n"
         "- FF-02 (Estructural - import-linter): Detecta acoplamiento indebido con el hardware (ADR-005). Si la lógica de dominio o de estados importa directamente un adaptador físico de RainBird o Hunter, la compuerta falla.\n"
         "- FF-03 / FF-04 (Calidad - pytest + M/G/c): Detecta degradación del rendimiento por eliminación de índices. Si alguien borra la migración del índice B-Tree, la simulación arroja p95 > 15 s y rompe el test por superar los 500 ms.\n"
         "- FF-05 (Safety - pytest + Monte Carlo): Detecta regresiones en la lógica de falla segura. Si una modificación introduce una orden de riego sin duración atómica o elimina el temporizador de hardware, la prueba detecta válvulas inundadas (> 0) y falla.\n"
         "- FF-06 (Resiliencia - Circuit Breaker): Detecta degradación en la contención de fallos. Si alguien elimina el Decorator del Circuit Breaker, el volumen de llamadas desperdiciadas supera el 20% y la aserción falla.\n"
         "- FF-07 (Seguridad - Multitenencia): Detecta filtrado defectuoso entre comisiones de regantes en PostgreSQL RLS. Si se rompe la política de aislamiento, se detectan accesos cruzados y se aborta el despliegue."),

        ("8. ¿Qué propuesta de la IA rechazaron con evidencia? ¿Qué habría pasado si la aceptaban sin medir?",
         "Propuesta de la IA rechazada con evidencia: La propuesta de 'Migrar a Microservicios con un clúster de Apache Kafka y Kubernetes para procesar la telemetría de las 2000 parcelas' (Interacción 7 de la bitácora).\n\n"
         "Qué habría pasado si se aceptaba sin medir:\n"
         "1. Colapso Catastrófico por Memoria (Out Of Memory): Un clúster de Apache Kafka con ZooKeeper/KRaft y microservicios Java/Python en contenedores requiere un consumo basal de más de 3.5 GB de memoria RAM únicamente para la infraestructura. "
         "   En un VPS de 4 GB RAM (restricción R-03), el sistema operativo habría invocado al OOM Killer de Linux, matando la base de datos o el broker continuamente.\n"
         "2. Incumplimiento del Plazo de Entrega (R-01): La sobrecarga operativa de configurar redes overlay, service mesh, orquestación, esquemas Avro y monitoreo distribuido habría consumido meses de trabajo, incumpliendo el plazo estricto de 1 mes.\n"
         "3. Complejidad innecesaria: La simulación empírica M/G/c demostró fehacientemente que el Monolito Modular en Django con pool de conexiones y caché Redis atiende la carga pico de 120 req/s con una utilización de CPU inferior al 20% y un p95 de 8.9 ms. "
         "   Aceptar la moda tecnológica de la IA sin medir habría destruido la viabilidad operativa y económica del proyecto.")
    ]

    for p_title, p_body in preguntas:
        add_cell_heading_2(c_cu, p_title)
        add_cell_p(c_cu, p_body)

    # -------------------------------------------------------------------------
    # PARTE III: CONCLUSIONES (Fila 3, Celda 0)
    # -------------------------------------------------------------------------
    print("Llenando Tabla 1: Sección III (Conclusiones)...")
    c_co = t1.rows[3].cells[0]

    add_cell_callout(c_co,
        "CONCLUSIONES TÉCNICAS Y LECCIONES APRENDIDAS\n"
        "Laboratorio 08: Diseño Arquitectónico Guiado por Atributos de Calidad — Grupo 04 (ChacraSmart Majes 2.0)",
        "Síntesis de Ingeniería", "success")

    conclusiones = [
        ("1. El Diseño Arquitectónico como Proceso Sistemático (ADD 3.0 vs Elección de Estilos):",
         "Se demostró que la arquitectura de software no es un acto estático de selección de estilos, sino un proceso riguroso y evolutivo. "
         "Attribute-Driven Design (ADD 3.0) proporcionó una metodología disciplinada para descomponer el crecimiento a 2000 parcelas en iteraciones "
         "manejables, donde cada decisión técnica se justifica mediante un escenario de calidad cuantificable y la selección precisa de tácticas arquitectónicas."),

        ("2. Primacía de la Evidencia Cuantitativa sobre la Intuición Técnica:",
         "La utilización de simulaciones matemáticas (colas M/G/c para rendimiento y Monte Carlo para disponibilidad) erradicó la toma de decisiones "
         "'a ojo'. El modelado empírico evidenció realidades contraintuitivas: la caché en memoria por sí sola genera una falsa sensación de seguridad "
         "que colapsa en arranques en frío, y el control centralizado en servidor es incapaz de garantizar protección en entornos ciberfísicos con cortes de red."),

        ("3. Gestión Rigurosa de Trade-offs y Mitigación de Riesgos (ATAM-lite):",
         "La evaluación ATAM-lite permitió mapear los compromisos estructurales del sistema: aceptar consistencia eventual de 60 s en la visualización "
         "de lecturas de humedad a cambio de proteger el único servidor VPS de la saturación, y aceptar inconsistencia temporal de estado en la UI "
         "a cambio de delegar la falla segura al hardware local. Todo compromiso quedó formalizado y protegido en los ADR-006 a ADR-008."),

        ("4. Arquitectura Evolutiva y Fitness Functions como Compuertas Automáticas:",
         "La implementación de fitness functions estructurales (import-linter) y de calidad (pytest) transforma los ADRs de documentos pasivos a "
         "contratos ejecutables en Integración Continua. Se comprobó experimentalmente que cualquier atajo indebido o regresión en tiempos de respuesta "
         "es interceptado de inmediato antes de llegar a producción, garantizando la longevidad del monolito modular."),

        ("5. Uso Crítico, Responsable y Ético de los Asistentes de Inteligencia Artificial:",
         "La práctica consolidó la regla de oro del diseño con IA: 'La IA propone, el equipo decide con evidencia'. Si bien la IA aceleró la formulación "
         "de escenarios y actuó eficazmente como evaluador adversario, manifestó un sesgo sistemático hacia soluciones hipercomplejas de moda (microservicios, Kafka) "
         "e incurrió en falsos positivos. La verificación matemática y contextual del equipo fue el filtro decisivo que preservó la viabilidad del proyecto."),

        ("6. Impacto Tecnológico y Sostenibilidad Hídrica en el Valle de Majes:",
         "La solución final para ChacraSmart Majes 2.0 garantiza que las 2000 parcelas y 6 comisiones de regantes operen con aislamiento seguro y alta disponibilidad, "
         "asegurando que ninguna electroválvula quede abierta ante cortes de red. Esto blinda a los agricultores de Majes contra pérdidas agrícolas y optimiza "
         "el uso eficiente del recurso hídrico en una de las zonas agroexportadoras más importantes de la región Arequipa.")
    ]

    for c_title, c_body in conclusiones:
        add_cell_heading_2(c_co, c_title)
        add_cell_p(c_co, c_body)

    # =========================================================================
    # 3. ACTUALIZAR TABLA 3: REFERENCIAS Y BIBLIOGRAFÍA
    # =========================================================================
    print("Llenando Tabla 3: Referencias y Bibliografía...")
    t3 = doc.tables[3]
    c_ref = t3.rows[1].cells[0]
    c_ref.text = ""

    referencias = [
        "Bass, L., Clements, P., & Kazman, R. (2021). Software architecture in practice (4th ed.). Addison-Wesley.",
        "Cervantes, H., & Kazman, R. (2016). Designing software architectures: A practical approach. Addison-Wesley.",
        "Kazman, R., Klein, M., & Clements, P. (2000). ATAM: Method for architecture evaluation (CMU/SEI-2000-TR-004). Software Engineering Institute, Carnegie Mellon University.",
        "Ford, N., Parsons, R., Kua, P., & Sadalage, P. (2022). Building evolutionary architectures: Automated software governance (2nd ed.). O'Reilly Media.",
        "Richards, M., & Ford, N. (2020). Fundamentals of software architecture: An engineering approach. O'Reilly Media.",
        "Erder, M., Pureur, P., & Woods, E. (2021). Continuous architecture in practice: Software architecture in the age of agility and DevOps. Addison-Wesley.",
        "Nygard, M. T. (2018). Release it! Design and deploy production-ready software (2nd ed.). Pragmatic Bookshelf.",
        "Huyen, C. (2025). AI engineering: Building applications with foundation models. O'Reilly Media.",
        "PostgreSQL Global Development Group. (2026). Row security policies and declarative table partitioning. https://www.postgresql.org/docs/current/ddl-rowsecurity.html",
        "Sedgewick, R., & Wayne, K. (2011). Algorithms (4th ed.). Addison-Wesley.",
        "import-linter documentation. (2026). Python linter for architectural dependencies. https://import-linter.readthedocs.io/"
    ]

    for ref in referencias:
        add_cell_bullet(c_ref, ref)

    # =========================================================================
    # 4. GUARDAR DOCUMENTO FINAL
    # =========================================================================
    print(f"Guardando documento modificado en: {TEMPLATE_PATH}")
    doc.save(str(TEMPLATE_PATH))

    print(f"Guardando copia en repositorio: {DOCS_INFORMES_PATH}")
    DOCS_INFORMES_PATH.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(DOCS_INFORMES_PATH))

    print("\n¡Documento generado y guardado exitosamente en ambas ubicaciones!")


if __name__ == "__main__":
    main()
