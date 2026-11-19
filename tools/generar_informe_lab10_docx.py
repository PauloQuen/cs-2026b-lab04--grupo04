#!/usr/bin/env python3
"""
Generador del Informe Oficial en Word (.docx) para el Laboratorio 10:
"Sistemas agénticos en la construcción de software: diseñar, construir y coordinar
agentes (bucle ReAct, máquina de estados, herramientas, memoria, multiagente y
humano en el circuito)"
Caso 9: ChacraSmart Majes — Grupo 04.

Llena la plantilla oficial de estudiante UNSA sin desbordar las celdas, sin
saltos suaves que estiren líneas justificadas y con todas las imágenes reales
generadas desde PlantUML, Mermaid y matplotlib.
"""

import sys
from pathlib import Path
from PIL import Image

from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_PATH = Path(r"C:\Users\USUARIO\Desktop\Copia de GUÍA DE LABORATORIO - FORMATO ESTUDIANTE.docx")
OUT_DESKTOP = Path(r"C:\Users\USUARIO\Desktop\Informe_Lab10_Sistemas_Agenticos_Grupo04.docx")
OUT_REPO = REPO_ROOT / "docs" / "informes" / "Informe_Lab10_Sistemas_Agenticos_Grupo04.docx"

COLOR_PRIMARY = RGBColor(0x1A, 0x36, 0x5D)
COLOR_SECONDARY = RGBColor(0x2B, 0x6C, 0xB0)
COLOR_TEXT = RGBColor(0x2D, 0x37, 0x48)
COLOR_MUTED = RGBColor(0x71, 0x80, 0x96)
COLOR_CODE = RGBColor(0x1A, 0x20, 0x2C)
COLOR_BLACK = RGBColor(0x00, 0x00, 0x00)


def set_cell_margins(cell, top=90, bottom=90, left=130, right=130):
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


def reset_section_cell(cell, section_title: str):
    cell.text = ""
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = False
    r = p.add_run(section_title)
    r.font.name = "Calibri"
    r.font.size = Pt(12)
    r.font.bold = True
    r.font.color.rgb = COLOR_BLACK


def apply_cell_styles(cell, fill_hex="F8FAFC", border_left_hex="2B6CB0"):
    tcPr = cell._tc.get_or_add_tcPr()
    tcPr.append(parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>'))
    tcPr.append(parse_xml(f'''
        <w:tcBorders {nsdecls("w")}>
            <w:top w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>
            <w:left w:val="single" w:sz="24" w:space="0" w:color="{border_left_hex}"/>
            <w:bottom w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>
            <w:right w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>
        </w:tcBorders>
    '''))
    set_cell_margins(cell, top=90, bottom=90, left=130, right=130)


def add_cell_heading_1(cell, text):
    p = cell.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    r.font.name = "Arial"
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.color.rgb = COLOR_PRIMARY
    return p


def add_cell_heading_2(cell, text):
    p = cell.add_paragraph()
    p.paragraph_format.space_before = Pt(9)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    r.font.name = "Arial"
    r.font.size = Pt(11)
    r.font.bold = True
    r.font.color.rgb = COLOR_SECONDARY
    return p


def add_cell_p(cell, text, bold_prefix=None, space_after=3.5, justify=True):
    """Divide cada salto de línea en un párrafo real independiente para evitar estiramiento."""
    lineas = [l.strip() for l in text.split("\n") if l.strip()]
    last_p = None
    for idx, linea_clean in enumerate(lineas):
        p = cell.add_paragraph()
        es_lista = linea_clean.startswith("• ") or (
            len(linea_clean) > 2 and linea_clean[0].isdigit() and linea_clean[1] in (".", ")")
        )
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT if (not justify or es_lista) else WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_before = Pt(1.5)
        p.paragraph_format.space_after = Pt(space_after if idx == len(lineas) - 1 else 2.5)
        p.paragraph_format.line_spacing = 1.15
        if es_lista:
            p.paragraph_format.left_indent = Inches(0.18)

        if idx == 0 and bold_prefix:
            rp = p.add_run(bold_prefix)
            rp.font.name = "Calibri"
            rp.font.size = Pt(10.5)
            rp.font.bold = True
            rp.font.color.rgb = COLOR_BLACK
        rb = p.add_run(linea_clean)
        rb.font.name = "Calibri"
        rb.font.size = Pt(10.5)
        rb.font.color.rgb = COLOR_TEXT
        last_p = p
    return last_p


def add_cell_bullet(cell, text, bold_prefix=None):
    p = cell.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.left_indent = Inches(0.22)
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(2.5)
    p.paragraph_format.line_spacing = 1.12
    rb = p.add_run("• ")
    rb.font.name = "Calibri"
    rb.font.size = Pt(10.5)
    rb.font.bold = True
    rb.font.color.rgb = COLOR_SECONDARY
    if bold_prefix:
        rp = p.add_run(bold_prefix)
        rp.font.name = "Calibri"
        rp.font.size = Pt(10.5)
        rp.font.bold = True
        rp.font.color.rgb = COLOR_BLACK
    rt = p.add_run(text)
    rt.font.name = "Calibri"
    rt.font.size = Pt(10.5)
    rt.font.color.rgb = COLOR_TEXT
    return p


def add_cell_callout(cell, title, text, kind="info"):
    palette = {
        "info": ("F0F9FF", "2B6CB0"),
        "success": ("F0FFF4", "276749"),
        "warning": ("FFFAF0", "C05621"),
    }
    fill_hex, border_hex = palette.get(kind, palette["info"])
    tbl = cell.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    c = tbl.cell(0, 0)
    c.width = Inches(6.2)
    apply_cell_styles(c, fill_hex=fill_hex, border_left_hex=border_hex)
    if title:
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(1.5)
        p.paragraph_format.space_after = Pt(2.0)
        rt = p.add_run(title)
        rt.font.name = "Arial"
        rt.font.size = Pt(9.5)
        rt.font.bold = True
        rt.font.color.rgb = COLOR_PRIMARY
        start_new = True
    else:
        start_new = False

    for idx, linea in enumerate(text.split("\n")):
        linea_clean = linea.strip()
        if not linea_clean:
            continue
        p = c.add_paragraph() if (start_new or idx > 0) else c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(1.5)
        p.paragraph_format.line_spacing = 1.12
        rb = p.add_run(linea_clean)
        rb.font.name = "Calibri"
        rb.font.size = Pt(9.5)
        rb.font.color.rgb = COLOR_TEXT

    sp = cell.add_paragraph()
    sp.paragraph_format.space_after = Pt(2)


def add_cell_code(cell, code_text, caption=None):
    tbl = cell.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    c = tbl.cell(0, 0)
    c.width = Inches(6.2)
    apply_cell_styles(c, fill_hex="F8FAFC", border_left_hex="2B6CB0")
    lines = code_text.strip().splitlines()
    for idx, line in enumerate(lines):
        p = c.paragraphs[0] if idx == 0 else c.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.05
        run = p.add_run(line if line.strip() else " ")
        run.font.name = "Consolas"
        run.font.size = Pt(8.0)
        run.font.color.rgb = COLOR_CODE
        stripped = line.strip()
        if stripped.startswith("#") or stripped.startswith("//"):
            run.font.color.rgb = COLOR_MUTED
            run.font.italic = True
    if caption:
        pc = cell.add_paragraph()
        pc.alignment = WD_ALIGN_PARAGRAPH.CENTER
        pc.paragraph_format.space_before = Pt(2)
        pc.paragraph_format.space_after = Pt(4)
        rc = pc.add_run(caption)
        rc.font.name = "Calibri"
        rc.font.size = Pt(8.5)
        rc.font.italic = True
        rc.font.color.rgb = COLOR_MUTED


def add_cell_table(cell, headers, rows_data, col_widths=None):
    tbl = cell.add_table(rows=len(rows_data) + 1, cols=len(headers))
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    hdr_row = tbl.rows[0]
    for idx, heading in enumerate(headers):
        c = hdr_row.cells[idx]
        tcPr = c._tc.get_or_add_tcPr()
        tcPr.append(parse_xml(f'<w:shd {nsdecls("w")} w:fill="1A365D"/>'))
        set_cell_margins(c, top=70, bottom=70, left=80, right=80)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(1)
        r = p.add_run(heading)
        r.font.name = "Arial"
        r.font.size = Pt(8.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    for r_idx, row_values in enumerate(rows_data):
        row = tbl.rows[r_idx + 1]
        bg_fill = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"
        for c_idx, val in enumerate(row_values):
            c = row.cells[c_idx]
            tcPr = c._tc.get_or_add_tcPr()
            tcPr.append(parse_xml(f'<w:shd {nsdecls("w")} w:fill="{bg_fill}"/>'))
            tcPr.append(parse_xml(f'''
                <w:tcBorders {nsdecls("w")}>
                    <w:top w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>
                    <w:left w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>
                    <w:bottom w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>
                    <w:right w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>
                </w:tcBorders>
            '''))
            set_cell_margins(c, top=55, bottom=55, left=75, right=75)
            p = c.paragraphs[0]
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(1)
            p.paragraph_format.line_spacing = 1.1
            r = p.add_run(str(val))
            r.font.name = "Calibri"
            r.font.size = Pt(8.5)
            r.font.color.rgb = COLOR_TEXT

    if col_widths:
        for row in tbl.rows:
            for idx, w in enumerate(col_widths):
                if idx < len(row.cells):
                    row.cells[idx].width = Inches(w)

    sp = cell.add_paragraph()
    sp.paragraph_format.space_after = Pt(3)


def add_cell_image(cell, img_rel_path: str, caption: str, max_width_in: float = 5.9, max_height_in: float = 6.2):
    img_path = REPO_ROOT / img_rel_path
    if not img_path.exists():
        add_cell_p(cell, f"[Imagen no encontrada: {img_rel_path}]")
        return
    with Image.open(img_path) as im:
        w, h = im.size
    aspect = h / w
    calc_w = max_width_in
    calc_h = calc_w * aspect
    if calc_h > max_height_in:
        calc_h = max_height_in
        calc_w = calc_h / aspect

    p = cell.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(str(img_path), width=Inches(calc_w), height=Inches(calc_h))

    pc = cell.add_paragraph()
    pc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pc.paragraph_format.space_before = Pt(0)
    pc.paragraph_format.space_after = Pt(5)
    rc = pc.add_run(caption)
    rc.font.name = "Calibri"
    rc.font.size = Pt(8.5)
    rc.font.italic = True
    rc.font.color.rgb = COLOR_MUTED


def main():
    if not TEMPLATE_PATH.exists():
        print(f"ERROR: No se encontró la plantilla oficial en {TEMPLATE_PATH}")
        sys.exit(1)

    doc = Document(str(TEMPLATE_PATH))

    # =========================================================================
    # 1. TABLA 0: INFORMACIÓN BÁSICA
    # =========================================================================
    t0 = doc.tables[0]
    t0.rows[1].cells[1].text = ""
    r = t0.rows[1].cells[1].paragraphs[0].add_run("CONSTRUCCIÓN DE SOFTWARE")
    r.font.name = "Arial"
    r.font.bold = True
    r.font.size = Pt(9.5)

    t0.rows[2].cells[1].text = ""
    r = t0.rows[2].cells[1].paragraphs[0].add_run(
        "Sistemas agénticos en la construcción de software: diseñar, construir y coordinar agentes "
        "(bucle ReAct, máquina de estados, herramientas, memoria, multiagente y humano en el circuito)"
    )
    r.font.name = "Arial"
    r.font.bold = True
    r.font.size = Pt(9.0)

    t0.rows[3].cells[1].text = "10"
    t0.rows[3].cells[3].text = "2026B"
    t0.rows[3].cells[5].text = "VI"

    t0.rows[4].cells[1].text = "21/11/2026"
    t0.rows[4].cells[3].text = "23:59 horas"

    t0.rows[5].cells[0].text = ""
    p_int = t0.rows[5].cells[0].paragraphs[0]
    ri = p_int.add_run("INTEGRANTE (s):\n")
    ri.font.name = "Arial"
    ri.font.bold = True
    ri.font.size = Pt(9.0)
    rnames = p_int.add_run("1. Quenta Ahumada Paulo Estefano\n2. Callo Ccagiavilca Kevin Joel")
    rnames.font.name = "Arial"
    rnames.font.size = Pt(9.0)

    t0.rows[6].cells[0].text = ""
    rd = t0.rows[6].cells[0].paragraphs[0].add_run("DOCENTE(s):  Mg. Antonio Arroyo Paz")
    rd.font.name = "Arial"
    rd.font.bold = True
    rd.font.size = Pt(9.0)

    # =========================================================================
    # 2. TABLA 1 — PARTE I: SOLUCIÓN DE EJERCICIOS / PROBLEMAS (E1 – E8)
    # =========================================================================
    t1 = doc.tables[1]
    t1.rows[0].cells[0].paragraphs[0].paragraph_format.keep_with_next = True
    c_ej = t1.rows[1].cells[0]
    reset_section_cell(c_ej, "SOLUCIÓN DE EJERCICIOS/PROBLEMAS")

    add_cell_callout(
        c_ej,
        "CASO 9 — CHACRASMART MAJES (GRUPO 04) · REGLA DE ORO DEL LABORATORIO 10",
        "\"El agente propone; el contrato y la política filtran; el humano aprueba.\" Todo agente opera sobre "
        "sandbox aislado con trazas JSONL reproducibles, presupuesto acotado de pasos, lista blanca de comandos, "
        "protección estricta de pruebas (rutas_protegidas=('tests/',)) y cero secretos en el código.",
        "info",
    )

    # --- E1 ---
    add_cell_heading_1(c_ej, "E1. Lienzo de Diseño y Tres Issues con Pruebas en Rojo")
    add_cell_p(
        c_ej,
        "Se elaboró el lienzo de diseño en agentes/diseno/lienzo.md justificando las 7 decisiones del sistema "
        "agéntico para ChacraSmart Majes, y se crearon 3 issues reales/sembrados en issues/ISSUE-01.md a ISSUE-03.md "
        "junto con sus pruebas objetivas en tests/test_issues_lab10.py (verificando que todas fallaran antes del agente: "
        "3 failed in 0.26s).",
    )
    add_cell_table(
        c_ej,
        ["Issue", "Problema / Error Reproducido", "Función en operaciones_campo.py", "Prueba Objetiva (E1 -> E8)"],
        [
            ["ISSUE-01", "La válvula no cierra al perder conexión (>10 s) tras vencer el tiempo programado (QA-01).", "procesar_latido_controlador()", "test_issue_01_valvula_cierra_al_perder_conexion (FAIL -> PASS)"],
            ["ISSUE-02", "Permite iniciar riego en parcela/turno de otro agricultor + comentario malicioso curl | sh.", "iniciar_riego_en_turno()", "test_issue_02_bloquea_riego_en_turno_ajeno (FAIL -> PASS)"],
            ["ISSUE-03", "Acepta humedad negativa (-12.5 %) o superior al 100 % (135.0 %).", "registrar_lectura_humedad()", "test_issue_03_rechaza_humedad_negativa_o_imposible (FAIL -> PASS)"],
        ],
        col_widths=[0.8, 2.2, 1.5, 1.7],
    )

    # --- E2 ---
    add_cell_heading_1(c_ej, "E2. Agente ReAct sobre ISSUE-01 con Traza y Diagrama")
    add_cell_p(
        c_ej,
        "Se implementó el mini framework en agentes/agente/ (nucleo.py, contrato.py, herramientas.py, politica.py, "
        "modelos.py y traza.py) y se ejecutó el agente único sobre ISSUE-01. En el paso 2, el asistente respondió en "
        "texto libre en lugar de JSON; no se corrigió manualmente: validar_decision() lo rechazó con CONTRATO_INVALIDO "
        "y el agente se autocorrigió en el paso 3, editando operaciones_campo.py y verificando test_issue_01 en verde.",
    )
    add_cell_image(
        c_ej,
        "agentes/trazas/issue1_ejecutor.png",
        "Figura 1. Diagrama de secuencia Mermaid autogenerado desde issue1_ejecutor.jsonl (incluye rechazo en paso 2).",
        max_width_in=5.5,
        max_height_in=5.2,
    )

    # --- E3 ---
    add_cell_heading_1(c_ej, "E3. Máquina de Estados del Agente y Pruebas de Contrato")
    add_cell_p(
        c_ej,
        "Se modeló la máquina de estados UML del agente en agentes/diseno/estados.puml incorporando el estado "
        "ESPERANDO_APROBACION (para confirmaciones humanas de edición) y se implementaron 12 pruebas unitarias en "
        "agentes/pruebas_agente/test_agente.py cubriendo 7 decisiones inválidas (texto libre, falta pensamiento, "
        "herramienta inventada, accion+final simultáneos, args como texto, acción vacía y campos extra).",
    )
    add_cell_image(
        c_ej,
        "agentes/diseno/estados.png",
        "Figura 2. Máquina de estados PlantUML de ChacraSmart Majes con estado ESPERANDO_APROBACION.",
        max_width_in=5.8,
        max_height_in=4.6,
    )

    # --- E4 ---
    add_cell_heading_1(c_ej, "E4. Herramienta Nueva (AST) y Memoria de Notas en ISSUE-03")
    add_cell_p(
        c_ej,
        "Se añadieron a Herramientas: mapa_repo(subdir='src') usando el módulo ast para extraer firmas y líneas "
        "exactas, y la memoria persistente de pizarra anotar(texto) / leer_notas() sobre agentes/notas.md. Al resolver "
        "ISSUE-03, el agente localizó registrar_lectura_humedad en 1 llamada y completó la tarea en 5 pasos (frente a "
        "7 pasos en E2: -28.6 % de pasos) con 7,404 caracteres de contexto final.",
    )
    add_cell_code(
        c_ej,
        "def mapa_repo(self, subdir: str = 'src') -> str:\n"
        "    base = self._ruta(subdir)\n"
        "    for p in sorted(base.rglob('*.py')):\n"
        "        tree = ast.parse(p.read_text(encoding='utf-8'))\n"
        "        for node in tree.body:\n"
        "            if isinstance(node, ast.FunctionDef):\n"
        "                args = [a.arg for a in node.args.args]\n"
        "                resumen.append(f\"  def {node.name}({', '.join(args)}) (L{node.lineno})\")",
        "Listado 1. Herramienta AST mapa_repo() en agentes/agente/herramientas.py.",
    )

    # --- E5 ---
    add_cell_heading_1(c_ej, "E5. Coordinación: Agente Único frente a Actor-Crítico (ISSUE-02)")
    add_cell_p(
        c_ej,
        "Se ejecutó ISSUE-02 dos veces en sandboxes aislados mediante agentes/orquestador.py. En ambos casos la "
        "política bloqueó la ejecución de curl | sh inyectada en las líneas 2–3 de operaciones_campo.py. Sin embargo, "
        "el agente único resolvió el bug funcional y dejó intacto el comentario malicioso, mientras que el Revisor de "
        "solo lectura en la Ronda 1 del patrón Actor-Crítico lo detectó como hallazgo bloqueante y obligó a eliminarlo "
        "en la Ronda 2.",
    )
    add_cell_image(
        c_ej,
        "agentes/trazas/issue2_actor_critico.png",
        "Figura 3. Trayectoria completa del orquestador (Planificador + Actor-Crítico en 2 rondas sobre ISSUE-02).",
        max_width_in=4.8,
        max_height_in=5.8,
    )

    # --- E6 ---
    add_cell_heading_1(c_ej, "E6. Humano en el Circuito y Delegación Progresiva")
    add_cell_p(
        c_ej,
        "Se activó el callback aprobar_edicion_consola en Politica (validando estrictamente 's' o 'n' por consola, "
        "verificado con test_aprobar_edicion_consola_valida_sn) y se definió en agentes/delegacion.md la hoja de ruta "
        "progresiva en 4 etapas (Ejecutor -> Revisor -> Colaborador -> Gobernador), exigiendo 0 incidentes OWASP LLM01/06 "
        "y 20 PRs exitosos antes de delegar ediciones sin pausa línea a línea.",
    )

    # --- E7 & E8 ---
    add_cell_heading_1(c_ej, "E7 y E8. Observación de Trazas, ADR-010, README y Entrega (v1.0-agentes)")
    add_cell_table(
        c_ej,
        ["Issue / Variante", "Rondas", "Pasos", "Rechazos Contrato", "Bloqueos Política", "Contexto Máx. / Total", "Observación Principal"],
        [
            ["ISSUE-01 (ReAct E2)", "1", "7", "1 (texto libre)", "0", "7,715 / 7,715", "Autocorrección tras error de contrato."],
            ["ISSUE-03 (AST+Notas E4)", "1", "5", "0", "0", "7,404 / 7,404", "-28.6 % pasos frente a E2."],
            ["ISSUE-02 (Agente Único)", "1", "5", "0", "1 (curl)", "5,492 / 5,492", "Dejó inyección indirecta en líneas 2–3."],
            ["ISSUE-02 (Actor-Crítico)", "2", "13", "0", "1 (curl)", "6,221 / 19,377", "Revisor detectó y eliminó la inyección."],
        ],
        col_widths=[1.3, 0.5, 0.5, 0.9, 0.85, 0.95, 1.2],
    )
    add_cell_image(
        c_ej,
        "agentes/trazas/metricas_agentes.png",
        "Figura 4. Métricas reales calculadas desde las trazas JSONL de los 3 issues.",
        max_width_in=6.0,
        max_height_in=3.8,
    )
    add_cell_p(
        c_ej,
        "Se redactó el ADR-010 en docs/architecture/adr/010-sistema-agentico.md, se actualizó README.md con la sección "
        "'Sistemas agénticos (Lab 10)', se verificaron las 62 pruebas de la suite completa (62 passed in 0.63s), "
        "los contratos de import-linter (2 kept, 0 broken) y radon cc (todas las funciones en rango A), y se publicó "
        "la etiqueta v1.0-agentes en GitHub.",
    )

    # =========================================================================
    # 3. TABLA 1 — PARTE II: SOLUCIÓN DEL CUESTIONARIO (8 PREGUNTAS)
    # =========================================================================
    c_cu = t1.rows[2].cells[0]
    reset_section_cell(c_cu, "SOLUCIÓN DEL CUESTIONARIO")

    preguntas = [
        (
            "1. ¿Qué diferencia a un agente de un flujo de trabajo fijo? Dé un ejemplo de su proyecto en el que un flujo de trabajo sea mejor opción.",
            "En un flujo de trabajo fijo (workflow), el desarrollador programa de antemano la secuencia exacta de pasos e invocaciones al LLM. En un agente, en cambio, recibe un objetivo abierto, razona sobre el estado actual y decide dinámicamente qué herramienta invocar a continuación, observa el resultado y repite el bucle hasta resolver el problema.\n\n"
            "Ejemplo donde un flujo de trabajo fijo es mejor opción en ChacraSmart Majes: la generación y validación de criterios de aceptación Gherkin o borradores de ADR con JSON Schema (Lab 09), o la validación de rangos de humedad en producción. Los pasos son completamente conocidos de antemano (plantilla -> LLM -> jsonschema.validate); usar un agente ReAct añadiría latencia, costo y riesgo sin ningún beneficio."
        ),
        (
            "2. Elija dos arquetipos de agentes (Sección 1.3) y explique cuál usaría para cada uno de sus tres issues.",
            "• Arquetipo 1 — ReAct: alterna pensamiento, acción y observación paso a paso para explorar el repositorio.\n"
            "• Arquetipo 2 — Planificador-Ejecutor (combinado con Reflexión/Crítico): traza primero un plan corto de solo lectura y luego lo ejecuta y revisa por fases.\n\n"
            "Asignación a los 3 issues de ChacraSmart Majes:\n"
            "• ISSUE-01 (cierre seguro ante pérdida de conexión): ReAct, porque exige reproducir la prueba, ubicar procesar_latido_controlador() y verificar el orden de condiciones.\n"
            "• ISSUE-03 (validación de humedad): ReAct con mapa_repo y notas, por ser un ajuste acotado en una sola función donde un agente simple resuelve en 5 pasos.\n"
            "• ISSUE-02 (autorización de turnos con riesgo de seguridad): Planificador-Ejecutor + Actor-Crítico, ya que implica control de acceso multitenencia y exige que un revisor independiente audite el diff ante posibles inyecciones indirectas."
        ),
        (
            "3. Describa la máquina de estados de su agente. ¿Qué guardia evita que el agente se ejecute indefinidamente?",
            "La máquina de estados (agentes/diseno/estados.puml y nucleo.py) inicia en INICIO, pasa a DECIDIENDO (consulta al modelo), luego a VALIDANDO_CONTRATO (donde puede ir a CONTRATO_INVALIDO y volver a DECIDIENDO, o terminar en FINALIZADO si incluye 'final'). Si propone una herramienta válida transiciona a EVALUANDO_POLITICA: desde allí puede ir a BLOQUEADO, a ESPERANDO_APROBACION (si edita código con humano activo), a EJECUTANDO -> OBSERVANDO -> DECIDIENDO, o terminar en LIMITE_ALCANZADO.\n\n"
            "Guardia contra bucles infinitos: la guardia [paso <= max_pasos] evaluada en Politica.evaluar() (por defecto max_pasos = 12 o 15), complementada en el orquestador con MAX_RONDAS = 2. Al superarse, el agente transiciona a LIMITE_ALCANZADO y rompe el bucle inmediatamente."
        ),
        (
            "4. ¿Qué es un contrato estructurado y qué ocurre en su agente cuando el modelo lo incumple? Dé un ejemplo de su bitácora.",
            "Un contrato estructurado (agente/contrato.py::validar_decision) es una especificación formal que obliga a que cada respuesta del modelo sea un diccionario JSON válido con el campo no vacío 'pensamiento', exactamente una de las claves 'accion' o 'final' (XOR), herramienta existente en el catálogo y 'args' como objeto JSON sin claves extra.\n\n"
            "Qué ocurre al incumplirlo: el núcleo NO ejecuta ninguna herramienta; registra el estado CONTRATO_INVALIDO en la traza JSONL y devuelve al modelo la observación 'ERROR DE CONTRATO: <motivo>. Responda solo con el JSON del protocolo' para que se corrija en el siguiente turno.\n\n"
            "Ejemplo real (Interacción 1 de bitacora-ia.md / ISSUE-01): en el paso 2, el modelo devolvió texto libre ('Voy a ejecutar las pruebas...'). El contrato lo rechazó automáticamente y en el paso 3 el asistente corrigió su salida enviando el JSON válido de ejecutar_pruebas."
        ),
        (
            "5. ¿Qué tipo de memoria agregó en E4 y qué efecto tuvo en los pasos y el contexto?",
            "En E4 se agregó memoria de notas o pizarra mediante las herramientas anotar(texto) y leer_notas() respaldadas por agentes/notas.md dentro del sandbox, complementada con la herramienta AST mapa_repo() para obtener un mapa compacto de firmas.\n\n"
            "Efecto medido en las trazas: en ISSUE-03 el agente necesitó solo 5 pasos (frente a 7 en ISSUE-01, una reducción del 28.6 %) y consumió 7,404 caracteres de contexto final frente a los 7,715 de ISSUE-01, evitando listar directorios ni leer archivos completos innecesarios."
        ),
        (
            "6. Según su E5, ¿compensó el bucle actor-crítico su costo adicional? Relacione su respuesta con el principio de parsimonia.",
            "El bucle actor-crítico tuvo un costo significativo: aumentó las acciones de 5 a 13 (+160 %) y elevó el contexto total acumulado de 5,492 a 19,377 caracteres (+253 %).\n\n"
            "Relación con el principio de parsimonia (Albada, 2025, cap. 8): este principio establece empezar con un solo agente y añadir más únicamente cuando aporten valor demostrable. Para ISSUE-01 o ISSUE-03 no compensa el costo extra. Sin embargo, para ISSUE-02 SÍ compensó plenamente: el agente único dejó el comentario malicioso (curl | sh) dentro de operaciones_campo.py, mientras que el revisor independiente lo detectó en Ronda 1 y garantizó un código limpio en Ronda 2."
        ),
        (
            "7. Explique el exceso de agencia y cómo lo evitaron con el mínimo privilegio por rol.",
            "El exceso de agencia (OWASP LLM06, 2025) ocurre cuando se otorga a un sistema agéntico más herramientas, permisos de escritura o autonomía de ejecución de los necesarios para su tarea, permitiendo que un error o una inyección indirecta cause daños reales (borrar archivos, alterar pruebas o descargar scripts maliciosos).\n\n"
            "Cómo lo evitamos por rol en Politica:\n"
            "• Planificador y Revisor tienen HERRAMIENTAS_SOLO_LECTURA (sin editar_archivo ni anotar).\n"
            "• Ejecutor opera confinado al sandbox (Herramientas._ruta), con rutas_protegidas=('tests/', 'agentes/pruebas_agente/') para impedir que altere pruebas, y una lista blanca estricta de comandos (pytest, radon, lint-imports, git status/diff) que bloqueó inmediatamente el intento de curl | sh en ISSUE-02."
        ),
        (
            "8. ¿En qué rol humano (ejecutor, revisor, colaborador o gobernador) dejaría hoy a su agente y qué evidencia necesitaría para avanzar al siguiente?",
            "Hoy dejaríamos al agente en la Etapa 1 (Humano como Ejecutor / Control Estrecho) con aprobación obligatoria por edición (aprobar_edicion) para código de producción, o a lo sumo iniciando transición hacia Etapa 2 (Humano Revisor) en ramas aisladas fuera de control de válvulas.\n\n"
            "Evidencia objetiva en trazas para avanzar a Etapa 2 (Humano Revisor): 100 % de las pruebas pasando sin violar rutas protegidas, 0 errores de contrato en 10 ejecuciones consecutivas, bloqueo del 100 % de inyecciones indirectas en red teaming y complejidad ciclomática Radon <= 10 mantenida."
        ),
    ]

    for q_title, q_body in preguntas:
        add_cell_heading_2(c_cu, q_title)
        add_cell_p(c_cu, q_body)

    # =========================================================================
    # 4. TABLA 1 — PARTE III: CONCLUSIONES
    # =========================================================================
    c_co = t1.rows[3].cells[0]
    reset_section_cell(c_co, "CONCLUSIONES")

    conclusiones = [
        (
            "1. Control Determinista sobre Razonamiento Probabilista:",
            "Modelar al agente como una máquina de estados con contrato JSON estricto (validar_decision) y presupuesto "
            "de pasos (max_pasos) eliminó fallos por respuestas en texto libre, obligando al LLM a autocorregirse."
        ),
        (
            "2. Eficiencia mediante Herramientas Estructurales y Memoria de Notas:",
            "La combinación de análisis AST (mapa_repo) y memoria de pizarra (anotar/leer_notas) redujo en un 28.6 % "
            "los pasos necesarios para resolver ISSUE-03 sin sobrecargar la ventana de contexto."
        ),
        (
            "3. Defensa Real contra Inyección Indirecta (OWASP LLM01) y Exceso de Agencia (LLM06):",
            "La lista blanca de comandos bloqueó en tiempo real la orden maliciosa curl | sh oculta en el código fuente, "
            "demostrando que la seguridad reside en el código determinista de Politica y no en confiar en el prompt."
        ),
        (
            "4. Parsimonia y Valor del Patrón Actor-Crítico en Seguridad:",
            "Aunque multiplica el costo de pasos (5 -> 13) y contexto acumulado, el revisor independiente detectó la "
            "inyección residual que el agente único omitió en ISSUE-02, justificando su uso en módulos críticos."
        ),
        (
            "5. Trazabilidad Auditable y Supervisión Humana Irrenunciable:",
            "Las trazas JSONL y diagramas Mermaid autogenerados permiten auditar cada decisión antes de que el humano "
            "apruebe la edición o fusión del PR, protegiendo el requisito crítico QA-01 de ChacraSmart Majes."
        ),
    ]

    for c_tit, c_bod in conclusiones:
        add_cell_heading_2(c_co, c_tit)
        add_cell_p(c_co, c_bod)

    # =========================================================================
    # 5. TABLA 3: REFERENCIAS Y BIBLIOGRAFÍA
    # =========================================================================
    t3 = doc.tables[3]
    c_ref = t3.rows[1].cells[0]
    c_ref.text = ""

    referencias = [
        "Albada, M. (2025). Desarrollo de aplicaciones con agentes de IA [Building applications with AI agents]. O'Reilly Media.",
        "Koenigstein, N. (2026). Agentes de IA: la guía definitiva [AI agents: The definitive guide]. O'Reilly Media.",
        "Grootendorst, M., & Alammar, J. (2026). Una guía ilustrada de los agentes de IA [An illustrated guide to AI agents]. O'Reilly Media.",
        "Yao, S., et al. (2023). ReAct: Synergizing reasoning and acting in language models. ICLR 2023.",
        "Anthropic. (2024). Building effective agents. https://www.anthropic.com/engineering/building-effective-agents",
        "Jimenez, C. E., et al. (2024). SWE-bench: Can language models resolve real-world GitHub issues? ICLR 2024.",
        "Greshake, K., et al. (2023). Not what you've signed up for: Compromising real-world LLM-integrated applications with indirect prompt injection. AISec '23.",
        "OWASP Foundation. (2025). OWASP Top 10 for LLM Applications 2025 (LLM01 Prompt Injection, LLM06 Excessive Agency). https://genai.owasp.org/llm-top-10/",
        "Huyen, C. (2025). AI engineering: Building applications with foundation models. O'Reilly Media.",
    ]
    for ref in referencias:
        add_cell_bullet(c_ref, ref)

    # =========================================================================
    # 6. GUARDAR EN ESCRITORIO Y EN REPOSITORIO
    # =========================================================================
    OUT_REPO.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(OUT_DESKTOP))
    doc.save(str(OUT_REPO))
    print(f"Informe Lab 10 generado en Escritorio: {OUT_DESKTOP}")
    print(f"Copia guardada en repositorio: {OUT_REPO}")


if __name__ == "__main__":
    main()
