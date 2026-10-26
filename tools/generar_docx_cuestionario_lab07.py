#!/usr/bin/env python3
"""
Generador del documento Word (.docx) con el Cuestionario Oficial del Laboratorio 07:
"Refactorizar hacia patrones de diseño con IA: Strategy, Adapter, Factory,
Decorator, State, Observer y Chain of Responsibility, medidos con pruebas y métricas"
Caso 9: ChacraSmart Majes — Grupo 04.

Respuestas técnicas, precisas y fundamentadas en el código, las métricas reales de Radon
y la arquitectura implementada en el repositorio.
"""

import sys
from pathlib import Path

import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

REPO_ROOT = Path(__file__).resolve().parent.parent

# Paleta corporativa formal institucional UNSA
COLOR_PRIMARY = RGBColor(0x1A, 0x36, 0x5D)    # Azul institucional (#1A365D)
COLOR_SECONDARY = RGBColor(0x2B, 0x6C, 0xB0)  # Azul medio (#2B6CB0)
COLOR_ACCENT = RGBColor(0x2C, 0x52, 0x82)     # Azul pizarra (#2C5282)
COLOR_TEXT = RGBColor(0x2D, 0x37, 0x48)       # Gris carbón (#2D3748)
COLOR_MUTED = RGBColor(0x71, 0x80, 0x96)      # Gris suave (#718096)
COLOR_CODE = RGBColor(0x1A, 0x20, 0x2C)       # Gris código


def add_qa_item(doc, num, question, answer_paragraphs):
    """Inserta una pregunta formal con encabezado y caja de respuesta estructurada."""
    # Pregunta
    p_q = doc.add_paragraph()
    p_q.paragraph_format.space_before = Pt(14)
    p_q.paragraph_format.space_after = Pt(4)
    p_q.paragraph_format.keep_with_next = True

    r_num = p_q.add_run(f"Pregunta {num}: ")
    r_num.font.name = 'Arial'
    r_num.font.bold = True
    r_num.font.size = Pt(11)
    r_num.font.color.rgb = COLOR_SECONDARY

    r_q = p_q.add_run(question)
    r_q.font.name = 'Arial'
    r_q.font.bold = True
    r_q.font.size = Pt(11)
    r_q.font.color.rgb = COLOR_PRIMARY

    # Caja de respuesta estilizada
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False

    cell = tbl.cell(0, 0)
    cell.width = Inches(6.5)

    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="F8FAFC"/>')
    tcPr.append(shd)

    borders = parse_xml(f'''
        <w:tcBorders {nsdecls("w")}>
            <w:top w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>
            <w:left w:val="single" w:sz="24" w:space="0" w:color="2B6CB0"/>
            <w:bottom w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>
            <w:right w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>
        </w:tcBorders>
    ''')
    tcPr.append(borders)

    tcMar = parse_xml(f'''
        <w:tcMar {nsdecls("w")}>
            <w:top w:w="120" w:type="dxa"/>
            <w:left w:w="160" w:type="dxa"/>
            <w:bottom w:w="120" w:type="dxa"/>
            <w:right w:w="160" w:type="dxa"/>
        </w:tcMar>
    ''')
    tcPr.append(tcMar)

    for idx, (prefix, text, is_code) in enumerate(answer_paragraphs):
        if idx == 0:
            p = cell.paragraphs[0]
        else:
            p = cell.add_paragraph()

        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.15

        if is_code:
            p.paragraph_format.line_spacing = 1.05
            lines = text.strip().splitlines()
            for l_idx, line in enumerate(lines):
                if l_idx > 0:
                    p = cell.add_paragraph()
                    p.paragraph_format.space_before = Pt(0)
                    p.paragraph_format.space_after = Pt(0)
                    p.paragraph_format.line_spacing = 1.05
                run_c = p.add_run(line if line.strip() else ' ')
                run_c.font.name = 'Consolas'
                run_c.font.size = Pt(8.5)
                run_c.font.color.rgb = COLOR_CODE
        else:
            if prefix:
                r_pre = p.add_run(prefix)
                r_pre.font.name = 'Calibri'
                r_pre.font.size = Pt(10)
                r_pre.font.bold = True
                r_pre.font.color.rgb = COLOR_PRIMARY
            r_txt = p.add_run(text)
            r_txt.font.name = 'Calibri'
            r_txt.font.size = Pt(10)
            r_txt.font.color.rgb = COLOR_TEXT


def build_cuestionario_docx(output_path: Path):
    """Genera el documento Word respondiendo con precisión a las 8 preguntas del cuestionario."""
    doc = Document()

    # Márgenes estándar de 1 pulgada
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # Encabezado institucional
    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_inst.paragraph_format.space_before = Pt(4)
    p_inst.paragraph_format.space_after = Pt(2)

    r_univ = p_inst.add_run("UNIVERSIDAD NACIONAL DE SAN AGUSTÍN DE AREQUIPA\n")
    r_univ.font.name = 'Arial'
    r_univ.font.size = Pt(13)
    r_univ.font.bold = True
    r_univ.font.color.rgb = COLOR_PRIMARY

    r_fac = p_inst.add_run("FACULTAD DE INGENIERÍA DE PRODUCCIÓN Y SERVICIOS — EPIS\n")
    r_fac.font.name = 'Arial'
    r_fac.font.size = Pt(10)
    r_fac.font.bold = True
    r_fac.font.color.rgb = COLOR_SECONDARY

    r_cur = p_inst.add_run("Construcción de Software (2026-B) · Caso 9: ChacraSmart Majes")
    r_cur.font.name = 'Calibri'
    r_cur.font.size = Pt(9.5)
    r_cur.font.italic = True
    r_cur.font.color.rgb = COLOR_MUTED

    # Título del Cuestionario
    p_tit = doc.add_paragraph()
    p_tit.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_tit.paragraph_format.space_before = Pt(8)
    p_tit.paragraph_format.space_after = Pt(12)

    r_tit = p_tit.add_run("CUESTIONARIO OFICIAL — LABORATORIO 07\n")
    r_tit.font.name = 'Arial'
    r_tit.font.size = Pt(15)
    r_tit.font.bold = True
    r_tit.font.color.rgb = COLOR_PRIMARY

    r_sub = p_tit.add_run("Refactorizar hacia patrones de diseño con IA: Strategy, Adapter, Factory, Decorator, State, Observer y Chain of Responsibility")
    r_sub.font.name = 'Arial'
    r_sub.font.size = Pt(10)
    r_sub.font.italic = True
    r_sub.font.color.rgb = COLOR_SECONDARY

    # Cuadro de datos del grupo
    tbl_meta = doc.add_table(rows=3, cols=2)
    tbl_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_meta.autofit = False

    meta_items = [
        ("Grupo y Caso:", "Grupo 04 · Caso 9: ChacraSmart Majes (Riego Inteligente con Falla Segura)"),
        ("Integrantes:", "• Quenta Ahumada Paulo Estefano\n• Kevin Joel Callo Ccagiavilca"),
        ("Fecha de Entrega:", "24 de Octubre de 2026 (Semestre 2026-B)")
    ]

    for idx, (label, val) in enumerate(meta_items):
        c_lbl = tbl_meta.rows[idx].cells[0]
        c_val = tbl_meta.rows[idx].cells[1]
        c_lbl.width = Inches(1.8)
        c_val.width = Inches(4.7)
        c_lbl.text = label
        c_val.text = val

        c_lbl.paragraphs[0].runs[0].font.name = 'Arial'
        c_lbl.paragraphs[0].runs[0].font.bold = True
        c_lbl.paragraphs[0].runs[0].font.size = Pt(9)
        c_lbl.paragraphs[0].runs[0].font.color.rgb = COLOR_PRIMARY

        for r in c_val.paragraphs[0].runs:
            r.font.name = 'Calibri'
            r.font.size = Pt(9)
            r.font.color.rgb = COLOR_TEXT

        for c in (c_lbl, c_val):
            tcPr = c._tc.get_or_add_tcPr()
            shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="F1F5F9"/>')
            tcPr.append(shd)
            borders = parse_xml(f'''
                <w:tcBorders {nsdecls("w")}>
                    <w:top w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>
                    <w:left w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>
                    <w:bottom w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>
                    <w:right w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>
                </w:tcBorders>
            ''')
            tcPr.append(borders)

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # =========================================================================
    # PREGUNTA 1
    # =========================================================================
    p1_q = "¿Qué diferencia hay entre un patrón arquitectónico (Laboratorio 04) y un patrón de diseño? Dé un ejemplo de cada uno en su caso."
    p1_ans = [
        (
            "Diferencia de escala y nivel de abstracción: ",
            "Un patrón arquitectónico define la macroestructura global del sistema: organiza subsistemas de alto nivel, capas, contenedores de despliegue y protocolos de comunicación física entre ellos, determinando atributos de calidad a gran escala (seguridad de hardware, tolerancia a fallos de red y disponibilidad). Por el contrario, un patrón de diseño opera a nivel microestructural dentro de un subsistema o módulo: resuelve problemas recurrentes de acoplamiento entre clases, instanciación de objetos, variación de algoritmos y adherencia a los principios SOLID sin alterar la topología de la arquitectura.",
            False
        ),
        (
            "Ejemplo de Patrón Arquitectónico en ChacraSmart (Lab 04): ",
            "Arquitectura Hexagonal (Puertos y Adaptadores, ADR-001) combinada con Broker de Mensajería MQTT (ADR-002) y Falla Segura en Controlador de Campo (ADR-003). Esta arquitectura a nivel de sistema desacopla el núcleo de dominio de la infraestructura de telecomunicaciones y garantiza que, ante la pérdida total de conexión con el servidor en la nube, el temporizador local del controlador cierre físicamente la válvula de forma autónoma.",
            False
        ),
        (
            "Ejemplo de Patrón de Diseño en ChacraSmart (Lab 07): ",
            "Patrón State en la entidad Valvula (estados.py) y Strategy en PoliticaRiego (politicas.py). Ambos operan internamente dentro del proceso Python de valvulas_riego: State sustituye sentencias condicionales dispersas por objetos polimórficos de estado, y Strategy encapsula fórmulas agronómicas sin afectar la arquitectura de contenedores ni el despliegue del sistema.",
            False
        )
    ]
    add_qa_item(doc, 1, p1_q, p1_ans)

    # =========================================================================
    # PREGUNTA 2
    # =========================================================================
    p2_q = "Explique con su código cómo Strategy materializa el principio abierto/cerrado. ¿Qué tuvo que modificar para agregar una variante nueva?"
    p2_ans = [
        (
            "Materialización del Principio Abierto/Cerrado (OCP): ",
            "El principio OCP establece que una entidad de software debe estar abierta a la extensión pero cerrada a la modificación. En la versión 'antes' (src/valvulas_riego/antes/servicio.py), cada nueva política de riego exigía abrir y modificar el método ejecutar_orden_riego() agregando ramas if/elif (politica == 'GOTEO', 'ASPERSION', etc.), elevando la complejidad ciclomática a 25. Con Strategy (politicas.py), se definió la interfaz abstracta PoliticaRiego con el método calcular_duracion(duracion_min, humedad). El servicio ServicioRiego ahora depende únicamente de esta abstracción.",
            False
        ),
        (
            "¿Qué se tuvo que modificar para agregar una variante nueva? ",
            "Absolutamente NADA en el código existente de ServicioRiego. Como se demostró formalmente en la prueba test_open_closed_nueva_politica_riego_sin_modificar_servicio en tests/test_patrones.py, para incorporar la nueva variante 'MICROASPERSION' únicamente se requirió:",
            False
        ),
        (
            "",
            "# 1. Extender la abstracción creando la nueva clase (sin tocar ServicioRiego)\n"
            "class PoliticaMicroaspersion(PoliticaRiego):\n"
            "    nombre = 'MICROASPERSION'\n"
            "    def calcular_duracion(self, duracion_min: int, humedad: float) -> int:\n"
            "        return int(duracion_min * 0.7)\n"
            "\n"
            "# 2. Registrar la nueva estrategia en la fábrica en tiempo de ejecución\n"
            "fabrica_pol.registrar('MICROASPERSION', PoliticaMicroaspersion)\n"
            "\n"
            "# 3. El servicio la consume inmediatamente: servicio.ejecutar_orden_riego(..., politica_tipo='MICROASPERSION')",
            True
        )
    ]
    add_qa_item(doc, 2, p2_q, p2_ans)

    # =========================================================================
    # PREGUNTA 3
    # =========================================================================
    p3_q = "¿En qué se diferencian Adapter y Decorator si ambos 'envuelven' un objeto?"
    p3_ans = [
        (
            "Diferencia fundamental de intención y contrato de interfaz: ",
            "Aunque ambos patrones utilizan composición para envolver a un objeto interno, difieren completamente en su propósito y en las interfaces que exponen al cliente:",
            False
        ),
        (
            "1. Patrón Adapter (Intención: compatibilidad de interfaces incompatibles): ",
            "El objeto envuelto (Adaptee) posee una interfaz externa y tipos de datos incompatibles con los del sistema. El Adapter implementa la interfaz esperada por el cliente (Target) y traduce las llamadas hacia el Adaptee. Cambia la interfaz para que dos sistemas dispares puedan interoperar.",
            False
        ),
        (
            "2. Patrón Decorator (Intención: adición transparente de responsabilidades): ",
            "El decorador implementa exactamente la MISMA interfaz que el objeto que envuelve (Component). No traduce ni altera firmas; su propósito es inyectar dinámicamente un comportamiento transversal (reintentos, caché, auditoría, control de tiempos) de forma transparente para el cliente.",
            False
        ),
        (
            "Ejemplificación en ChacraSmart Majes: ",
            "• Adapter (AdaptadorHunter): Envuelve a HunterProC_SDK. El SDK opera en SEGUNDOS y devuelve tuplas (bool, 'ACK'); el adaptador traduce y expone la interfaz ControladorValvula que opera en MINUTOS y retorna objetos ResultadoOperacion.\n"
            "• Decorator (ConReintentos): Envuelve a cualquier ControladorValvula e implementa ControladorValvula. No modifica unidades; intercepta TimeoutError y reintenta la llamada hasta 3 veces de forma transparente.",
            False
        )
    ]
    add_qa_item(doc, 3, p3_q, p3_ans)

    # =========================================================================
    # PREGUNTA 4
    # =========================================================================
    p4_q = "¿Por qué el patrón State es la implementación natural de un diagrama de máquina de estados? ¿Qué ganó frente a usar condicionales?"
    p4_ans = [
        (
            "Correspondencia isomórfica con el modelo formal UML: ",
            "Un diagrama de máquina de estados (estados-valvula.mmd) modela formalmente nodos de estado y transiciones dirigidas activadas por eventos. El patrón State materializa esta definición de forma uno a uno: cada estado del diagrama se convierte en una clase concreta (EstadoCerrada, EstadoAbriendo, EstadoAbierta, EstadoCerrando, EstadoFalla) y cada transición se modela como un método polimórfico (abrir, confirmar_apertura, cerrar, confirmar_cierre, fallar_cierre_seguro). La flecha de transición se implementa mediante valvula.cambiar_a(NuevoEstado()).",
            False
        ),
        (
            "Ganancias directas frente al uso de condicionales (if/elif): ",
            "1. Principio Fail-Closed y Robustez: La clase base EstadoValvulaBase prohíbe todas las transiciones lanzando TransicionEstadoInvalida. Cada subclase solo habilita explícitamente las transiciones seguras. Cualquier combinación no modelada es bloqueada por diseño.\n"
            "2. Eliminación de Primitive Obsession: Se erradicaron las cadenas primitivas dispersas ('CERRADA', 'ABIERTA') que provocaban bugs tipográficos o estados intermedios inconsistentes.\n"
            "3. Blindaje de Falla Segura (QA-01 / ADR-003): En la clase EstadoFalla, todas las operaciones de apertura o cierre son rechazadas, garantizando que una electroválvula bloqueada en campo permanezca estanca hasta la revisión presencial del técnico.\n"
            "4. Reducción de Complejidad: El método ejecutar_orden_riego pasó de complejidad ciclomática 25 a 3 al transferir la validación de transiciones al objeto de estado.",
            False
        )
    ]
    add_qa_item(doc, 4, p4_q, p4_ans)

    # =========================================================================
    # PREGUNTA 5
    # =========================================================================
    p5_q = "¿Por qué son indispensables las pruebas de caracterización antes de refactorizar? Describa un error que sus pruebas detectaron."
    p5_ans = [
        (
            "Indispensabilidad de las pruebas de caracterización (Feathers / Fowler): ",
            "Las pruebas de caracterización no juzgan si el diseño actual es elegante; describen de manera empírica y reproducible el comportamiento observable del sistema existente (casos de éxito, conversiones, excepciones y eventos de salida). Constituyen una red de seguridad indispensable porque, al ejecutarse simultáneamente sobre la versión 'antes' y la versión 'después' con un fixture parametrizado (m), garantizan matemáticamente que el refactor preserva intacto el comportamiento del negocio sin introducir regresiones silenciosas.",
            False
        ),
        (
            "Error real detectado por las pruebas en nuestro proyecto: ",
            "Durante la refactorización de actuadores asistida por IA (Interacción 2 de la Bitácora), la IA generó el AdaptadorHunter asumiendo que todos los fabricantes de hardware operaban en minutos, enviando duracion_min de forma directa al SDK.\n\n"
            "Al ejecutar pytest tests/test_comportamiento.py, la prueba de caracterización test_riego_hunter_exitoso_con_conversion falló inmediatamente en rojo: el simulador HunterProC_SDK requería obligatoriamente la duración en SEGUNDOS. Gracias a la prueba previa, el equipo detectó la discrepancia de inmediato y corrigió el adaptador incorporando la conversión encapsulada duracion_segundos = duracion_min * 60. Sin esta prueba, una válvula Hunter real en Majes habría regado únicamente 20 segundos en vez de 20 minutos (1/60 del agua necesaria), arruinando los cultivos.",
            False
        )
    ]
    add_qa_item(doc, 5, p5_q, p5_ans)

    # =========================================================================
    # PREGUNTA 6
    # =========================================================================
    p6_q = "¿Qué patrón propuso la IA que ustedes rechazaron y por qué? ¿Qué es la 'patternitis'?"
    p6_ans = [
        (
            "Patrones propuestos por la IA rechazados por el equipo: ",
            "1. Rechazo de Singleton para el Controlador de Válvulas: La IA propuso implementar ControladorValvula como Singleton para 'evitar colisiones de hardware'. Se rechazó porque introduce acoplamiento global oculto, viola la regla de oro de la guía ('no introduzcas Singleton ni estado global') y destruye la testabilidad paralela al impedir inyectar mocks/fakes con fallas programadas (fallas=2). Se reemplazó por Inyección de Dependencias gestionada por FabricaControladores.\n"
            "2. Rechazo de LLM-as-a-judge: La IA propuso auditar la salida del LLM con un segundo LLM. Se rechazó por duplicar costos, agregar más de 2 segundos de latencia y carecer de determinismo. Se adoptó una cadena determinista de Guardrails (Chain of Responsibility).",
            False
        ),
        (
            "¿Qué es la 'patternitis'? ",
            "La 'patternitis' (o sobrediseño compulsivo por patrones) es el antipatrón de diseño consistente en sobrecargar una solución introduciendo la mayor cantidad posible de patrones GoF (Visitor, Memento, Interpreter, Abstract Factory, etc.) sin que existan olores de código reales ni variaciones de negocio que los justifiquen. Produce una sobreingeniería nociva ('accidental complexity'): multiplica exponencialmente las líneas de código (en nuestra kata adversaria aumentó a 1,240 SLOC), divide la lógica en decenas de clases microscópicas y eleva la carga cognitiva para el equipo. Los patrones deben ser la respuesta a un olor demostrado, no un fin en sí mismos.",
            False
        )
    ]
    add_qa_item(doc, 6, p6_q, p6_ans)

    # =========================================================================
    # PREGUNTA 7
    # =========================================================================
    p7_q = "¿Por qué se debe tratar la salida de un LLM como dato no confiable? Describa los guardrails de su caso y qué protegen."
    p7_ans = [
        (
            "Tratamiento de la IA como dato no confiable (Zero-Trust Output): ",
            "Los Modelos de Lenguaje (LLMs) son componentes estocásticos y no deterministas: ante prompts idénticos o variaciones contextuales pueden alucinar datos falsos con alta convicción, equivocarse en magnitudes numéricas, omitir restricciones de seguridad o ser vulnerables a inyecciones de prompt. En un sistema ciberfísico como ChacraSmart Majes, donde las recomendaciones conllevan la apertura física de electroválvulas en parcelas agrícolas, un error del LLM puede provocar anegamiento de cultivos, marchitamiento por estrés hídrico o sobrecostos energéticos en Majes (QA-01). Por ello, la salida de la IA debe tratarse con la misma desconfianza que una entrada de red no autenticada.",
            False
        ),
        (
            "Guardrails implementados en nuestro caso (Chain of Responsibility en ia.py): ",
            "1. GuardrailMaximoRiego (Seguridad Física QA-01 / ADR-003): Analiza la respuesta generada buscando recomendaciones de tiempo (ej. '95 minutos'). Si el valor supera la apertura_maxima_min de la válvula (ej. 60 min), bloquea la salida y lanza ValueError impidiendo el sobre-riego físico.\n"
            "2. GuardrailConsistenciaHumedad (Integridad de Datos): Detecta valores de humedad imposibles generados por alucinación (porcentajes negativos como '-15%' o superiores al 100%), garantizando consistencia con la telemetría LoRaWAN.\n"
            "3. GuardrailLenguajeCampesino (Ética y Veracidad): Filtra y bloquea promesas comerciales no auditadas o fraudulentas ('garantizado al 100%', 'cero riesgo hídrico', 'agua infinita'), protegiendo la confianza del agricultor.",
            False
        )
    ]
    add_qa_item(doc, 7, p7_q, p7_ans)

    # =========================================================================
    # PREGUNTA 8
    # =========================================================================
    p8_q = "Según sus métricas, ¿valió la pena el refactor? Argumente con la complejidad ciclomática, las líneas de código y los cambios previstos."
    p8_ans = [
        (
            "Balance cuantitativo de complejidad y volumen de código: ",
            "• Complejidad Ciclomática (radon cc): El método principal ejecutar_orden_riego se redujo drásticamente de complejidad 25 (Rango D - Alerta Crítica) a complejidad 3 (Rango A - Excelente), lo que representa una reducción del 88.0%. El método cerrar_valvula se redujo de 15 (Rango C) a 2 (Rango A). La complejidad promedio global de todo el módulo disminuyó de 10.16 (Rango C) a 2.16 (Rango A).\n"
            "• Volumen de Código (radon raw): El servicio orquestador principal redujo su volumen de 159 a 108 SLOC (-32.1%). A nivel global del sistema, el código creció de 159 a 561 SLOC (+252.8%) distribuidos en 7 módulos altamente cohesivos con Responsabilidad Única.",
            False
        ),
        (
            "Argumentación respecto a los cambios previstos: ",
            "El refactor VALIÓ ABSOLUTAMENTE LA PENA. Si ChacraSmart Majes fuese un script descartable para una sola parcela con un único actuador que jamás cambiaría, la versión 'antes' habría sido suficiente. Sin embargo, en el escenario real de producción agrícola en Majes, se prevé la incorporación continua de hardware de distintos fabricantes (Hunter, RainBird, Tuya, ESP32) y políticas agronómicas variadas (goteo, aspersión, deficitario). Gracias a Adapter + Factory + Strategy, agregar una nueva variante se probó que requiere CERO modificaciones en el servicio. Además, el patrón State blindó la falla segura obligatoria (ADR-003) y la cadena de guardrails garantizó la inocuidad física del componente de IA. El costo en líneas de código e indirección queda plenamente justificado por la robustez, extensibilidad y mantenibilidad demostradas.",
            False
        )
    ]
    add_qa_item(doc, 8, p8_q, p8_ans)

    # Guardar documento
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(output_path))
    print(f"Cuestionario generado exitosamente en: {output_path}")


if __name__ == "__main__":
    desktop_dir = Path("C:/Users/USUARIO/Desktop")
    out_desktop = desktop_dir / "Cuestionario_Lab07_Patrones_Diseno_Grupo04.docx"
    out_repo = REPO_ROOT / "docs" / "Cuestionario_Lab07_Patrones_Diseno_Grupo04.docx"

    build_cuestionario_docx(out_desktop)
    build_cuestionario_docx(out_repo)
    print("Exportación dual del Cuestionario completada!")
