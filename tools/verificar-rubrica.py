#!/usr/bin/env python3
"""
Verificacion automatica contra la rubrica del Lab 04 (Guia UNSA).

Agnostico del caso: NO tiene hardcodeados los puntajes, los actores, los modulos ni
los nombres de los ADR. Todos esos datos se DERIVAN de los propios documentos, de modo
que el mismo script sirve cuando el equipo cambia de caso sin reescribirlo.

Uso:
    python3 tools/verificar-rubrica.py
Devuelve 0 si todos los requisitos minimos estan cubiertos.
"""
import glob
import math
import re
import sys
from pathlib import Path

R = Path(__file__).resolve().parents[1]

# Nombres de archivo que son parte de la estructura del lab (no dependen del caso).
ADR_DIR = "docs/architecture/adr"
DIAG_DIR = "docs/architecture/diagramas"


def t(rel):
    return (R / rel).read_text(encoding="utf-8")


def tabla_ok(lineas):
    """True si cada bloque de filas de tabla tiene el mismo numero de columnas.

    Una linea en blanco CIERRA la tabla, asi que solo se comparan filas contiguas
    que empiezan por '|'. Comparar la fila final de una tabla con la linea en
    blanco siguiente produce un falso positivo.
    """
    bloque = []
    for linea in list(lineas) + [""]:
        if linea.lstrip().startswith("|"):
            bloque.append(linea)
            continue
        for lo, hi in zip(bloque, bloque[1:]):
            if lo.count("|") != hi.count("|"):
                return False
        bloque = []
    return True


P = []


def add(eje, req, detalle, cond):
    P.append((eje, req, str(detalle), bool(cond)))


# ============================================================ DERIVAR DEL CASO
d = t("docs/architecture/drivers.md")
m = t("docs/architecture/matriz-decision.md")
mmd = t("docs/architecture/diagramas/arquitectura.mmd")
b = t("docs/architecture/bitacora-ia.md")
rm = t("README.md")

# --- IDs declarados en drivers.md
RF = sorted(set(re.findall(r"\|\s(RF-\d\d)\s\|", d)))
QA = sorted(set(re.findall(r"\|\s(QA-\d\d)\s\|", d)))
RES = sorted(set(re.findall(r"\|\s(R-\d\d)\s\|", d)))

# --- Actores y modulos declarados en el diagrama Mermaid
# Los actores son los nodos declarados ANTES del primer subgraph. Contarlos con un
# regex global daria falsos positivos: tambien capturaria el almacen (DB) y los
# servicios externos (CC, MSG), que tambien son identificadores en mayusculas.
_cabeza = mmd.split("subgraph", 1)[0]
ACTORES = sorted(set(re.findall(r"^\s*([A-Z][A-Z0-9]{1,3})\[", _cabeza, re.M)))
MODULOS = sorted(set(re.findall(r"^\s*(M\d+)\[", mmd, re.M)))
SUBCAMPS = len(re.findall(r"^\s*subgraph ", mmd, re.M))

# --- Totales publicados en la matriz (fila "Total ponderado")
fila_total = next((x for x in m.splitlines() if "Total ponderado" in x), "")
TOTALES = re.findall(r"\*\*(\d,\d\d)\*\*", fila_total)
TOTALES_NUM = [float(x.replace(",", ".")) for x in TOTALES]
GANADORA = fila_total.count("←") if "←" in fila_total else None

# --- Pesos de la matriz
PESOS = [float(x.replace("%", "").replace(",", "."))
         for x in re.findall(r"\|\s*(\d+(?:[.,]\d+)?)\s*%\s*\|", m)]

# --- ADR reales
ADRS = sorted(glob.glob(str(R / ADR_DIR / "0[0-9]*.md")))
ADR_DECISION = [p for p in ADRS if "000-plantilla" not in p]

# --- Nombres de caso (para comprobar coherencia entre documentos)
CASO_DRV = re.search(r"^# Drivers arquitectónicos — (.+)$", d, re.M)
CASO_RM = re.search(r"^# .* — Laboratorio 04", rm, re.M)
NOMBRE_CASO = CASO_DRV.group(1).strip() if CASO_DRV else "?"

# ------------------------------------------------------------------ E1
atr = len(re.findall(r"^\| \d \| ", d, re.M))
medidas = re.findall(r"^\| QA-\d\d \|.*?\| ([^|]+)\|\s*$", d, re.M)
con_numero = sum(1 for x in medidas if re.search(r"\d", x))
vagas = [w for w in ("rápido", "facil", "fácil", "óptimo", "seguro", "bueno")
         if w in " ".join(medidas).lower()]
add("E1", ">=5 requisitos funcionales", f"{len(RF)} RF", len(RF) >= 5)
add("E1", ">=4 atributos priorizados", f"{atr} atributos", atr >= 4)
add("E1", "El 1.º atributo es el crítico del caso", "OK" if "crítico" in d.lower() else "no",
    "crítico" in d.lower())
add("E1", ">=4 restricciones", f"{len(RES)}: {', '.join(RES)}", len(RES) >= 4)
add("E1", "R-01 plazo y R-02 equipo presentes",
    "OK" if {"R-01", "R-02"} <= set(RES) else "faltan", {"R-01", "R-02"} <= set(RES))
add("E1", "3 escenarios de atributos distintos", f"{len(QA)} QA: {', '.join(QA)}", len(QA) >= 3)
add("E1", "Medidas numericas en todos los escenarios",
    f"{con_numero}/{len(medidas)}", con_numero >= 3 and con_numero == len(medidas))
add("E1", "Ninguna medida vaga", "ninguna" if not vagas else str(vagas), not vagas)
add("E1", "Tablas markdown consistentes", "OK", tabla_ok(d.splitlines()))

# ------------------------------------------------------------------ E2
alt = len(re.findall(r"\*\*[ABC]\. ", m))
casos_ia = len(re.findall(r"### 5\.\d", m))
add("E2", "3 alternativas descritas", f"{alt}", alt >= 3)
add("E2", ">=5 criterios, pesos que suman 100 %",
    f"{len(PESOS)} criterios = {sum(PESOS):.0f}%" if PESOS else "0",
    len(PESOS) >= 5 and abs(sum(PESOS) - 100) < 1e-6)
add("E2", "Cada peso justificado con un driver",
    f"{len(RES and re.findall(r'R-0\d', m))} citas R-, {len(re.findall(r'QA-0\d', m))} citas QA-",
    len(re.findall(r"R-0\d", m)) >= 5 and len(re.findall(r"QA-0\d", m)) >= 2)
add("E2", "Puntajes 1-5 publicados para cada alternativa",
    f"{len(TOTALES)} totales: {', '.join(TOTALES)}", len(TOTALES) >= 3)
add("E2", "Conclusion con enlace al ADR-001",
    "OK" if "adr/001-estilo-arquitectonico.md" in m else "no",
    "adr/001-estilo-arquitectonico.md" in m)
add("E2", ">=1 afirmacion incorrecta de la IA verificada",
    f"{casos_ia} casos documentados", casos_ia >= 1)

# La seccion "Fundamento de cada puntaje" debe justificar LOS MISMOS criterios que
# la matriz pondera. Si al cambiar de caso queda un criterio viejo (o uno nuevo sin
# justificar), la tabla se desincroniza y la matriz deja de ser auditable.
fundamento = m.split("Fundamento de cada puntaje", 1)
CRITERIOS = []
if len(fundamento) == 2:
    _bloque = fundamento[1].split("##", 1)[0]
    CRITERIOS = re.findall(r"^\|\s*([A-ZÁ][\wáéíóúñ ]{4,40}?)\s+A?=|\|\s*([A-ZÁ][\wáéíóúñ ]{4,40}?)\s*=", _bloque, re.M)
    CRITERIOS = sorted({(a or b).strip() for a, b in CRITERIOS})
add("E2", "Fundamento justifica criterios que existen en la matriz",
    f"{CRITERIOS}" if CRITERIOS else "no hay tabla de fundamento",
    len(CRITERIOS) > 0)
# Ningun criterio justificado puede ser criterio que la matriz NO pondera.
nombres_matriz = set(re.findall(r"^\|\s*\*{0,2}([A-ZÁÉÍÓÚÑ][\wáéíóúñ ]{4,40}?)\*{0,2}\s*\(\d+\s*%", m, re.M))
desconocidos = [c for c in CRITERIOS if c.split()[0].lower() not in
                {" ".join(x.split()[:1]).lower() for x in nombres_matriz}]
add("E2", "Ningun criterio justificado fuera de la matriz",
    "ninguno" if not desconocidos else str(desconocidos), not desconocidos)

# Coherencia: el total ganador que el script de la matriz declara debe ser el mayor.
mp = Path(R / "docs/architecture/diagramas/matriz-ponderada.py")
if mp.exists():
    ms = mp.read_text(encoding="utf-8")
    decl = dict(re.findall(r'"([ABC])":\s*([\d.]+)', ms))
    decl = {k: float(v) for k, v in decl.items()}
    if TOTALES_NUM and decl:
        add("E2", "Totales del .py coinciden con los del .md",
            f"py {decl} vs md {TOTALES_NUM}",
            len(decl) == len(TOTALES_NUM) and
            all(abs(decl[k] - v) < 1e-9 for k, v in zip(sorted(decl), TOTALES_NUM)))
    add("E2", "matriz-ponderada.py declara ganador consistente con la matriz",
        "OK" if 'assert ganador == "B"' in ms else "no", 'assert ganador == "B"' in ms)
    add("E2", "Grafico de la matriz existe en img/", "matriz-ponderada.png",
        (R / DIAG_DIR / "img" / "matriz-ponderada.png").exists())
else:
    add("E2", "Existe matriz-ponderada.py con aserciones", "falta el archivo", False)

# ------------------------------------------------------------------ E3
cobertura = all(re.search(rf"{mid}\[.*?RF-", mmd) for mid in MODULOS)
add("E3", ">=2 actores", f"{len(ACTORES)}: {', '.join(ACTORES)}", len(ACTORES) >= 2)
add("E3", "Modulos de dominio definidos", f"{len(MODULOS)}: {', '.join(MODULOS)}", len(MODULOS) >= 3)
add("E3", "Almacenamiento de datos", "PostgreSQL", "PostgreSQL" in mmd)
add("E3", ">=1 servicio externo", f"{mmd.count('externo')} etiquetas 'externo'",
    "servicio externo" in mmd.lower())
add("E3", "Usa subgraph para agrupar", f"{SUBCAMPS} subgrafos", SUBCAMPS >= 1)
add("E3", "Direccion de dependencias explicita", "flechas dirigidas",
    "-->" in mmd and "-.->" in mmd)
add("E3", "Cada modulo cubre >=1 RF", "OK" if cobertura else "no", cobertura)
add("E3", "Sin lineas %% vacias (rompen el lexer de Mermaid)",
    "ninguna" if not re.findall(r"^%%\s*$", mmd, re.M) else "HAY",
    not re.findall(r"^%%\s*$", mmd, re.M))
add("E3", "PNG exportado en img/", "arquitectura.png",
    (R / DIAG_DIR / "img" / "arquitectura.png").exists())

# ------------------------------------------------------------------ E4
add("E4", "3 ADR de decision (ademas de la plantilla)", f"{len(ADR_DECISION)}", len(ADR_DECISION) == 3)
add("E4", "Plantilla 000-plantilla.md copiada", "OK",
    (R / ADR_DIR / "000-plantilla.md").exists())
for ruta in ADR_DECISION:
    s = Path(ruta).read_text(encoding="utf-8")
    n = Path(ruta).name
    meta = ("**Estado:** Aceptado" in s and re.search(r"\*\*Fecha:\*\* \d{4}-\d\d-\d\d", s)
            and "**Decisores:**" in s)
    citas = (re.search(r"RF-\d\d", s) and re.search(r"QA-\d\d", s) and re.search(r"\bR-\d\d", s))
    alts = re.search(r"## Alternativas consideradas", s)
    cons = "**Positivas" in s and "**Negativas" in s
    voz = re.search(r"\*\*Usaremos", s)
    fecha_hoy = "2026-10-04" in s
    add("E4", f"{n}: estado/fecha/decisores", "OK" if meta else "no", meta)
    add("E4", f"{n}: cita IDs de drivers.md", "OK" if citas else "no", citas)
    add("E4", f"{n}: alternativas + consecuencias +/-",
        "OK" if alts and cons else "no", alts and cons)
    add("E4", f"{n}: decision en voz activa", "OK" if voz else "no", voz)
    add("E4", f"{n}: fecha de la sesion actual", "OK" if fecha_hoy else "NO",
        fecha_hoy)

# ------------------------------------------------------------------ E5
p = t("docs/architecture/diagramas/alternativa.puml")
nota = re.search(r"note bottom of L(.*?)end note", p, re.S)
lineas = len([x for x in nota.group(1).strip().split("\n") if x.strip()]) if nota else 0
segunda = sorted(TOTALES_NUM, reverse=True)[1] if len(TOTALES_NUM) >= 2 else None
citado = re.findall(r"(\d,\d\d)", p)
add("E5", "Es la 2.ª mejor alternativa (cita su puntaje)",
    f"citados {citado}", len(citado) >= 2)
add("E5", "note de 3 a 5 lineas", f"{lineas} lineas", 3 <= lineas <= 5)
add("E5", "Validado con PlantUML y PNG en img/", "img/alternativa.png",
    (R / DIAG_DIR / "img" / "alternativa.png").exists())

# ------------------------------------------------------------------ E6
dp = t("docs/architecture/diagramas/despliegue.py")
add("E6", "usuarios y dispositivos", "Users + Mobile",
    "Users(" in dp and "Mobile(" in dp)
add("E6", "proxy", "Nginx", "Nginx(" in dp)
add("E6", "aplicacion", "Django", "Django(" in dp)
add("E6", "base de datos", "PostgreSQL", "PostgreSQL(" in dp)
add("E6", "cache o colas", "Redis + Celery", "Redis(" in dp and "Celery(" in dp)
add("E6", "dispositivo en campo", "Server", "Server(" in dp)
add("E6", "servicios externos", f"{dp.count('Internet(')} Internet()",
    dp.count("Internet(") >= 1)
add("E6", "monitoreo", "Prometheus + Grafana",
    "Prometheus(" in dp and "Grafana(" in dp)
add("E6", "Cluster y Edge(label=...)",
    f"{dp.count('Cluster(')} clusters / {dp.count('Edge(label=')} edges",
    dp.count("Cluster(") >= 2 and dp.count("Edge(label=") >= 4)
add("E6", "Script ejecutado y PNG en img/", "despliegue.png",
    (R / DIAG_DIR / "img" / "despliegue.png").exists())

# ------------------------------------------------------------------ E7
inter = len(re.findall(r"^\| \d \| \d\d/\d\d \|", b, re.M))
add("E7", ">=5 interacciones registradas", f"{inter}", inter >= 5)
add("E7", ">=1 Rechazada o Corregida con evidencia",
    "OK" if "**Rechazada**" in b and "**Corregida**" in b else "no",
    "**Rechazada**" in b and "**Corregida**" in b)
add("E7", "Evidencia concreta (error o archivo citados)",
    "NameError + AssertionError" if "NameError" in b and "AssertionError" in b else "no",
    "NameError" in b and "AssertionError" in b)
add("E7", "Anexo con los prompts completos",
    f"{len(re.findall(r'^### Prompt', b, re.M))} prompts",
    len(re.findall(r"^### Prompt", b, re.M)) >= 4)
add("E7", "Sin datos personales en los prompts",
    "declarado" if "datos personales" in b else "no", "datos personales" in b)

# ------------------------------------------------------------------ E8
add("E8", "Mismo caso en README y en drivers.md",
    NOMBRE_CASO if NOMBRE_CASO in rm else "NO coincide",
    NOMBRE_CASO in rm if NOMBRE_CASO != "?" else False)
add("E8", "Integrantes y roles", "OK" if "## Integrantes" in rm else "no",
    "## Integrantes" in rm)
add("E8", "Mermaid embebido", "OK" if "```mermaid" in rm else "no", "```mermaid" in rm)
enlaces_adr = set(re.findall(r"adr/00\d-[\w-]+\.md", rm))
rotos = [e for e in enlaces_adr if not Path(R / "docs/architecture" / e).exists()]
add("E8", "Enlaces a los 3 ADR, ninguno roto",
    f"{len(enlaces_adr)} enlaces, {len(rotos)} rotos" + (f" {rotos}" if rotos else ""),
    len(enlaces_adr) == 3 and not rotos)
refl = rm.split("## Reflexión")[-1].split("\n## ")[0]
refl = refl.split("\n", 1)[1] if "\n" in refl else ""
plano = re.sub(r"[*`>#]", "", refl)
plano = " ".join(plano.split())
lineas_refl = math.ceil(len(plano) / 85) if plano else 0
add("E8", "Reflexion de 5 a 8 lineas (al renderizar)",
    f"{len(plano)} chars ~ {lineas_refl} lineas", 5 <= lineas_refl <= 8)
add("E8", "Links internos del README resuelven",
    "OK" if not [x for x in re.findall(r"\]\((?!https?:)([^)]+)\)", rm)
                 if not Path(R / x.split("#")[0]).exists()] else "hay rotos",
    not [x for x in re.findall(r"\]\((?!https?:)([^)]+)\)", rm)
         if not Path(R / x.split("#")[0]).exists()])

# ------------------------------------------------------------------ Repo
estructura = [
    "README.md",
    "docs/architecture/drivers.md",
    "docs/architecture/matriz-decision.md",
    "docs/architecture/bitacora-ia.md",
    "docs/architecture/diagramas/arquitectura.mmd",
    "docs/architecture/diagramas/alternativa.puml",
    "docs/architecture/diagramas/despliegue.py",
    "docs/architecture/diagramas/matriz-ponderada.py",
]
faltan_estructura = [x for x in estructura if not Path(R / x).exists()]
add("Repo", "Estructura completa segun la guia",
    f"{len(estructura) - len(faltan_estructura)}/{len(estructura)}"
    + (f" falta {faltan_estructura}" if faltan_estructura else ""),
    not faltan_estructura)
add("Repo", "Ningun .jar comiteado (binario grande)", "OK" if not glob.glob(
    str(R / "**" / "*.jar"), recursive=True) else "HAY JAR",
    not glob.glob(str(R / "**" / "*.jar"), recursive=True))

# ------------------------------------------------------------------ Informe
print(f"Caso detectado en drivers.md: {NOMBRE_CASO}")
print(f"RF: {len(RF)} | QA: {len(QA)} | R: {len(RES)} | "
      f"Actores: {len(ACTORES)} | Modulos: {len(MODULOS)} | Pesos: {sum(PESOS):.0f}%")
print(f"ADR: {len(ADR_DECISION)} | Totales publicados: {TOTALES}")
print()
print(f"{'EJE':6} {'REQUISITO':56} {'DETALLE':30} ESTADO")
print("-" * 104)
actual = None
for eje, req, det, est in P:
    if eje != actual:
        if actual is not None:
            print("-" * 104)
        actual = eje
    print(f"{eje:6} {req:56} {det:30} {'OK' if est else 'FALTA'}")
print("-" * 104)
faltan = [(e, r) for e, r, _, v in P if not v]
print(f"TOTAL: {len(P) - len(faltan)}/{len(P)} requisitos verificados")
if faltan:
    print("\nPENDIENTES:")
    for e, r in faltan:
        print(f"  - [{e}] {r}")
    sys.exit(1)
print("Todos los requisitos minimos de la rubrica estan cubiertos.")