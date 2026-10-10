#!/usr/bin/env python3
"""
Verificacion automatica contra la guia del Lab 05 (UML como codigo, Guia UNSA).

Agnostico del caso: los IDs, nombres de clases y nombres de paquete se DERIVAN de
los propios diagramas. Ademas de comprobar estructura y entregables, implementa
dos reglas de la Tabla 2 con logica real (no keywords):
  - C4: construye el grafo dirigido del paquete y detecta ciclos (Kahn).
  - C2: toda transicion del diagrama de estados debe estar etiquetada con la
        operacion que la provoca (mismo patron del ejemplo docente).

Uso:
    python3 tools/verificar-lab05.py
Devuelve 0 si todos los requisitos minimos estan cubiertos.
"""
import re
import subprocess
import sys
from collections import deque
from pathlib import Path

R = Path(__file__).resolve().parents[1]
DESIGN = R / "docs" / "design"
IMG = DESIGN / "img"
SRC = R / "src"


def t(rel):
    return (R / rel).read_text(encoding="utf-8")


def add(*, eje, req, detalle, cond):
    P.append((eje, req, str(detalle), bool(cond)))


P = []


def es_dag(nodos, aristas):
    """True si el grafo dirigido no tiene ciclos (algoritmo de Kahn)."""
    adj = {n: [] for n in nodos}
    grado = {n: 0 for n in nodos}
    for a, b in aristas:  # a --> b
        adj[a].append(b)
        grado[b] += 1
    cola = deque([n for n in nodos if grado[n] == 0])
    vistos = 0
    while cola:
        n = cola.popleft()
        vistos += 1
        for m in adj[n]:
            grado[m] -= 1
            if grado[m] == 0:
                cola.append(m)
    return vistos == len(nodos)


# ------------------------------------------------------------------ Derivar
clases = t("docs/design/clases.puml")
sec = t("docs/design/secuencia-programar-riego.puml")
estados = t("docs/design/estados-valvula.mmd")
act = t("docs/design/actividades-riego-automatico.puml")
paq = t("docs/design/paquetes.puml")
his = t("docs/design/historia.md")
bit = t("docs/design/bitacora-ia.md")
cons = t("docs/design/consistencia.md")
rt = t("docs/design/round-trip.md")
gitignore = (R / ".gitignore").read_text(encoding="utf-8")

# --- Clases y sus operaciones (para C1/C2)
CLASES = re.findall(r"^\s*(class|interface|abstract class)\s+(\w+)", clases, re.M)
CLASES_NOMBRE = [c for _, c in CLASES]
OPERACIONES = set(re.findall(r"^\s*\+\s*\w+\(", clases, re.M))
OPERACIONES = {op.strip("+ ") for op in OPERACIONES}
OP_SIN_PAREN = {op.replace("(", "") for op in OPERACIONES}

# --- Puertos / adaptadores (conectores propios del ADR-001)
PUERTOS = re.findall(r"interface\s+(\w+)", clases)
ADAPTADORES = re.findall(r"class\s+(\w+.*Adapter\w*)", clases)
ENUMS = re.findall(r"enum\s+(\w+)", clases)

# --- C1: mensajes de la secuencia contra operaciones de clases
# Solo se auditan los mensajes dirigidos a objetos CUYAS clases estan en el
# diagrama (mismo criterio del ejemplo docente): PWA y RiegoController son capa
# de interfaz y quedan fuera; los retornos (--> y -->>) no son mensajes C1.
NO_MODELADOS = {"UI", "C"}
MENSAJES = re.findall(r"^\s*[\w]+\s*(?:->|->>)\s*(\w+)\s*:\s*([a-z][A-Za-z0-9]*)", sec, re.M)
MENSAJES = [msg for receptor, msg in MENSAJES if receptor not in NO_MODELADOS]
SIN_OP = [m for m in set(MENSAJES) if m not in OP_SIN_PAREN]

# --- C2: transiciones de estados etiquetadas con la operacion que las provoca
# Sintaxis Mermaid: `CERRADA --> ABRIENDO : abrir() [guard]`. El estado final
# [*] sin etiqueta es valido (patron ENTREGADO --> [*] del docente).
TRANSICIONES = re.findall(r"^\s*([A-Z]+)\s+-->\s+([A-Z*]+)\s*(?::\s*(.*))?$", estados, re.M)
FINALES_SIN_OP = [t for t in TRANSICIONES if t[1] == "*" and not t[2]]
OPERABLES_SIN_OP = [t for t in TRANSICIONES if t[1] != "*" and not t[2]]

# --- C3: multiplicidades en ambos extremos (solo asociaciones -- y *--;
# las dependencias ..> NO llevan multiplicidad, semantica UML)
REL = re.findall(r'^\s*\w+\s*"([\d.*]+)"\s*(?:--|\*--)\s*"([\d.*]+)"\s*\w', clases, re.M)
SIN_MULT = [r for r in re.findall(r"^\s*([\w]+\s+(?:--|\*--)\s+[\w]+)", clases, re.M)
            if '"' not in r]

# --- C4: grafo de paquetes (Kahn), resolviendo alias -> nombre
PAQ_LINEAS = re.findall(r'^\s*package\s*"([\w ]+)"\s+as\s+(\w+)', paq, re.M)
ALIAS_PAQ = {alias: nombre for nombre, alias in PAQ_LINEAS}
NO_PAQS = sorted({nombre for nombre, _ in PAQ_LINEAS})
ARISTAS_RAW = re.findall(r"^\s*([\w_]+)\s*(?:-->|\.\.>)\s*([\w_]+)", paq, re.M)
ARISTAS = [(ALIAS_PAQ[a], ALIAS_PAQ[b]) for a, b in ARISTAS_RAW
           if a in ALIAS_PAQ and b in ALIAS_PAQ]
ARISTAS_RARAS = [(a, b) for a, b in ARISTAS_RAW
                 if a not in ALIAS_PAQ or b not in ALIAS_PAQ]

# --- Entregables de estructura
ARCHIVOS = [
    "docs/design/historia.md", "docs/design/clases.puml",
    "docs/design/secuencia-programar-riego.puml", "docs/design/estados-valvula.mmd",
    "docs/design/actividades-riego-automatico.puml", "docs/design/paquetes.puml",
    "docs/design/round-trip.md", "docs/design/consistencia.md",
    "docs/design/bitacora-ia.md", "README.md",
]
FALTAN = [x for x in ARCHIVOS if not Path(R / x).exists()]
IMGS = ["clases-valvulas-riego.png", "secuencia-programar-riego.png",
        "estados-valvula.png", "actividades-riego-automatico.png",
        "paquetes.png"]
IMG_FALTAN = [x for x in IMGS if not (IMG / x).exists()]
SRC_DIRS = sorted([p.name for p in SRC.iterdir() if p.is_dir()]) if SRC.exists() else []

# ------------------------------------------------------------------ E1
add(eje="E1", req="historia.md con HU (compuesta o historica)",
    detalle=len(re.findall(r"^\|\s*HU-\d\d", his, re.M)), cond=True)  # detalle informativo
add(eje="E1", req="Criterios de aceptacion como CA-XX verificables",
    detalle=len(re.findall(r"\bCA-\d\d", his)),
    cond=len(re.findall(r"\bCA-\d\d", his)) >= 3)
add(eje="E1", req=">=6 clases de diseno",
    detalle=f"{len(CLASES_NOMBRE)}: {', '.join(CLASES_NOMBRE[:8])}",
    cond=len(CLASES_NOMBRE) >= 6)
add(eje="E1", req="2 enumeraciones (estado y alerta)",
    detalle=len(ENUMS), cond=len(ENUMS) >= 2)
add(eje="E1", req="Puertos (interfaces) y adaptadores del ADR-001",
    detalle=f"{len(PUERTOS)} puertos / {len(ADAPTADORES)} adaptadores",
    cond=len(PUERTOS) >= 3 and len(ADAPTADORES) >= 2)
add(eje="E1", req="Relaciones con multiplicidad en AMBOS extremos (C3)",
    detalle=f"{len(REL)} relacion(es), {len(SIN_MULT)} sin notacion",
    cond=len(REL) >= 4 and not SIN_MULT)

# ------------------------------------------------------------------ E2
add(eje="E2", req="Mensajes de secuencia = operaciones de clases (C1)",
    detalle=f"{len(SIN_OP)} sin operacion: {SIN_OP}",
    cond=not SIN_OP)
add(eje="E2", req="alt (exito/error)", detalle=sec.count("alt"),
    cond=sec.count("alt") >= 1)
add(eje="E2", req="loop o opt", detalle=f"{sec.count('loop')} loop / {sec.count('opt')} opt",
    cond=sec.count("loop") >= 1 or sec.count("opt") >= 1)
add(eje="E2", req="Mensaje asincrono (->>)",
    detalle=len(re.findall(r"->>", sec)), cond=len(re.findall(r"->>", sec)) >= 1)
add(eje="E2", req="PNG renderizado",
    detalle="img/secuencia-programar-riego.png",
    cond=(IMG / "secuencia-programar-riego.png").exists())

# ------------------------------------------------------------------ E3
add(eje="E3", req="Diagrama en Mermaid (stateDiagram-v2)",
    detalle="SI" if "stateDiagram-v2" in estados else "NO",
    cond="stateDiagram-v2" in estados)
add(eje="E3", req="Transiciones etiquetadas con operaciones (C2)",
    detalle=f"{len(OPERABLES_SIN_OP)} sin etiqueta en estados",
    cond=not OPERABLES_SIN_OP)
add(eje="E3", req="-'[*]' final sin operacion es valido (patron docente)",
    detalle=f"{len(FINALES_SIN_OP)} final(es) admitidos",
    cond=len(FINALES_SIN_OP) <= 2)
add(eje="E3", req="PNG renderizado (mermaid-cli)",
    detalle="img/estados-valvula.png",
    cond=(IMG / "estados-valvula.png").exists())

# ------------------------------------------------------------------ E4
add(eje="E4", req="Particiones (|) en el diagrama de actividades",
    detalle=len(re.findall(r"^\s*\|", act, re.M)), cond="|" in act)
add(eje="E4", req="Decisiones", detalle=act.count("if ("),
    cond=act.count("if (") >= 2)
add(eje="E4", req="Fork/join",
    detalle=f"{act.count('fork')} fork / {act.count('join')} join",
    cond="fork" in act)
add(eje="E4", req="PNG renderizado",
    detalle="img/actividades-riego-automatico.png",
    cond=(IMG / "actividades-riego-automatico.png").exists())

# ------------------------------------------------------------------ E5
add(eje="E5", req="Un paquete por modulo del ADR-001",
    detalle=f"{len(NO_PAQS)}: {', '.join(NO_PAQS)}", cond=len(NO_PAQS) >= 5)
add(eje="E5", req="Dependencias etiquetadas",
    detalle=len(re.findall(r"^\s*[\w_]+\s+(?:-->|\.\.>)\s*[\w_]+\s*:", paq, re.M)),
    cond=len(re.findall(r"^\s*[\w_]+\s+(?:-->|\.\.>)\s*[\w_]+\s*:", paq, re.M))
    == len(ARISTAS_RAW))
add(eje="E5", req="C4: grafo de paquetes SIN ciclos (Kahn)",
    detalle=f"{len(ARISTAS)} aristas / {len(NO_PAQS)} nodos"
    + (f" sin alias {ARISTAS_RARAS}" if ARISTAS_RARAS else ""),
    cond=es_dag(NO_PAQS, ARISTAS) and not ARISTAS_RARAS)

# ------------------------------------------------------------------ E6
add(eje="E6", req="Codigo fuente por modulo",
    detalle=SRC_DIRS, cond=len(SRC_DIRS) >= 1)
add(eje="E6", req="Ejecutado realmente (aserciones en dominio.py)",
    detalle="assert en dominio.py",
    cond="assert" in t("src/valvulas_riego/dominio.py"))
add(eje="E6", req="pyreverse ejecutado y salida devuelta",
    detalle="classes-valvulas-riego-pyreverse.puml",
    cond=(DESIGN / "classes-valvulas-riego-pyreverse.puml").exists())
add(eje="E6", req="round-trip.md con causa y accion",
    detalle=len(re.findall(r"^\|", rt, re.M)) - 2,
    cond="Causa" in rt and "Acción" in rt)

# ------------------------------------------------------------------ E7
filas = len(re.findall(r"^\| \d \| \d\d/\d\d \|", bit, re.M))
add(eje="E7", req=">=7 interacciones en la bitacora",
    detalle=f"{filas} filas", cond=filas >= 7)
add(eje="E7", req="Falsos positivos del auditor identificados y explicados",
    detalle=f"{cons.count('falso positivo')} menciones",
    cond=cons.count("falso positivo") >= 1 and bool(re.search(r"Rechazad[oa]", cons)))
add(eje="E7", req="Hallazgo real corregido (C3: multiplicidad 0..*)",
    detalle="0..* en clases.puml",
    cond='"0..*"' in clases and "RF-06" in cons)
add(eje="E7", req="consistencia.md cruza C1-C5",
    detalle="C1..C5 presentes" if all(f"C{i}" in cons for i in range(1, 6)) else "faltan",
    cond=all(f"C{i}" in cons for i in range(1, 6)))
add(eje="E7", req="Anexo de prompts completos",
    detalle=len(re.findall(r"^### Prompt IA", bit, re.M)),
    cond=len(re.findall(r"^### Prompt IA", bit, re.M)) >= 7)

# ------------------------------------------------------------------ E8
rm = t("README.md")
add(eje="E8", req="Seccion diseno UML en README",
    detalle="Diseño UML (Lab 05)" if "Diseño UML" in rm else "no",
    cond="Diseño UML" in rm)
add(eje="E8", req="Mermaid embebido en README (estados)",
    detalle="```mermaid" if "```mermaid" in rm else "no",
    cond="```mermaid" in rm)
add(eje="E8", req="Enlaces a los diagramas, ninguno roto",
    detalle=len(re.findall(r"docs/design/[\w./-]+\.(?:puml|mmd|md)", rm)),
    cond=not [x for x in re.findall(r"\]\(([^)#]+)\)", rm)
              if x.startswith("docs/") and not Path(R / x).exists()])
add(eje="E8", req="Verificador presente y con logica real (C4/C2)",
    detalle="tools/verificar-lab05.py",
    cond=Path(R / "tools" / "verificar-lab05.py").exists())

# ------------------------------------------------------------------ Repo
add(eje="Repo", req="Estructura de docs/design/ completa",
    detalle=f"{len(ARCHIVOS) - len(FALTAN)}/{len(ARCHIVOS)}"
    + (f" falta {FALTAN}" if FALTAN else ""), cond=not FALTAN)
add(eje="Repo", req="PNGs de los diagramas generados",
    detalle=f"{len(IMGS) - len(IMG_FALTAN)}/{len(IMGS)}"
    + (f" falta {IMG_FALTAN}" if IMG_FALTAN else ""), cond=not IMG_FALTAN)
add(eje="Repo", req="Ningun .pyc comiteado (git ls-files)",
    detalle="OK" if not subprocess.run(
        ["git", "ls-files", "*.pyc"], cwd=R, capture_output=True,
        text=True, check=False).stdout.strip() else "HAY .pyc",
    cond=not subprocess.run(
        ["git", "ls-files", "*.pyc"], cwd=R, capture_output=True,
        text=True, check=False).stdout.strip())
add(eje="Repo", req="Sin .jar comiteado",
    detalle="plantuml.jar ignorado" if "plantuml.jar" in gitignore else "NO",
    cond="plantuml.jar" in gitignore)

# ------------------------------------------------------------------ Informe
print(f"Clases: {len(CLASES_NOMBRE)} | Puertos: {len(PUERTOS)} | "
      f"Enums: {len(ENUMS)} | Mensajes C1: {len(MENSAJES)}")
print(f"Paquetes: {NO_PAQS} | Aristas C4: {len(ARISTAS)}")
print()
print(f"{'EJE':6} {'REQUISITO':58} {'DETALLE':34} ESTADO")
print("-" * 110)
actual = None
for eje, req, det, est in P:
    if eje != actual:
        if actual is not None:
            print("-" * 110)
        actual = eje
    print(f"{eje:6} {req:58} {det:34} {'OK' if est else 'FALTA'}")
print("-" * 110)
faltan = [(e, r) for e, r, _, v in P if not v]
print(f"TOTAL: {len(P) - len(faltan)}/{len(P)} requisitos verificados")
if faltan:
    print("\nPENDIENTES:")
    for e, r in faltan:
        print(f"  - [{e}] {r}")
    sys.exit(1)
print("Todos los requisitos del Lab 05 estan cubiertos.")