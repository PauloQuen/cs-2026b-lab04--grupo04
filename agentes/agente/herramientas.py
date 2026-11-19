"""Herramientas acotadas en sandbox para el agente de código (Paso 5, E4)."""
from __future__ import annotations

import ast
import pathlib
import subprocess
import sys
from typing import Dict, List


class Herramientas:
    """Provee operaciones seguras confinadas dentro del directorio raíz (sandbox)."""

    def __init__(self, raiz: str | pathlib.Path, ruta_notas: str = "agentes/notas.md") -> None:
        self.raiz = pathlib.Path(raiz).resolve()
        self.ruta_notas = ruta_notas

    def _ruta(self, ruta: str) -> pathlib.Path:
        p = (self.raiz / ruta).resolve()
        if self.raiz not in p.parents and p != self.raiz:
            raise PermissionError(f"Ruta fuera del sandbox: {ruta}")
        return p

    def catalogo(self) -> Dict[str, str]:
        """Documentación concisa de herramientas: propósito, parámetros y retorno."""
        return {
            "listar_archivos": "listar_archivos(subdir: str = '.') -> str. Lista archivos en un subdirectorio del sandbox.",
            "leer_archivo": "leer_archivo(ruta: str, inicio: int = 1, fin: int = 120) -> str. Lee líneas numeradas de un archivo.",
            "buscar": "buscar(patron: str, subdir: str = '.') -> str. Busca texto exacto en archivos .py/.md.",
            "editar_archivo": "editar_archivo(ruta: str, antes: str, despues: str) -> str. Reemplaza un fragmento único.",
            "ejecutar_pruebas": "ejecutar_pruebas(objetivo: str = 'tests/test_issues_lab10.py') -> str. Ejecuta pytest.",
            "ver_cambios": "ver_cambios() -> str. Devuelve git diff del directorio actual.",
            "ejecutar_comando": "ejecutar_comando(comando: str) -> str. Ejecuta un comando permitido por la política.",
            "mapa_repo": "mapa_repo(subdir: str = 'src') -> str. Extrae clases y firmas de funciones con AST.",
            "anotar": "anotar(texto: str) -> str. Agrega una nota/hipótesis persistente a la memoria de pizarra (notas.md).",
            "leer_notas": "leer_notas() -> str. Lee las notas guardadas en la pizarra de la tarea.",
        }

    def listar_archivos(self, subdir: str = ".") -> str:
        base = self._ruta(subdir)
        if not base.exists():
            return f"ERROR: no existe {subdir}"
        items = []
        for p in sorted(base.rglob("*")):
            if p.is_file() and ".git" not in p.parts and "__pycache__" not in p.parts and "node_modules" not in p.parts:
                items.append(str(p.relative_to(self.raiz)).replace("\\", "/"))
        return "\n".join(items[:80]) if items else "(sin archivos)"

    def leer_archivo(self, ruta: str, inicio: int = 1, fin: int = 120) -> str:
        p = self._ruta(ruta)
        if not p.is_file():
            return f"ERROR: archivo no encontrado: {ruta}"
        lineas = p.read_text(encoding="utf-8").splitlines()
        i = max(1, int(inicio))
        f = min(len(lineas), int(fin))
        salida = [f"{idx}: {lineas[idx - 1]}" for idx in range(i, f + 1)]
        return "\n".join(salida)

    def buscar(self, patron: str, subdir: str = ".") -> str:
        base = self._ruta(subdir)
        coincidencias: List[str] = []
        for p in sorted(base.rglob("*")):
            if p.is_file() and p.suffix in (".py", ".md", ".yaml", ".json") and "node_modules" not in p.parts:
                try:
                    for n_lin, linea in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
                        if patron in linea:
                            rel = str(p.relative_to(self.raiz)).replace("\\", "/")
                            coincidencias.append(f"{rel}:{n_lin}: {linea.strip()}")
                except UnicodeDecodeError:
                    continue
        return "\n".join(coincidencias[:40]) if coincidencias else f"Sin coincidencias para {patron!r}"

    def editar_archivo(self, ruta: str, antes: str, despues: str) -> str:
        p = self._ruta(ruta)
        if not p.is_file():
            return f"ERROR: archivo no encontrado: {ruta}"
        texto = p.read_text(encoding="utf-8")
        conteo = texto.count(antes)
        if conteo != 1:
            return f"ERROR: el fragmento aparece {conteo} veces; debe aparecer exactamente 1"
        p.write_text(texto.replace(antes, despues, 1), encoding="utf-8")
        return f"OK: {ruta} modificado"

    def ejecutar_pruebas(self, objetivo: str = "tests/test_issues_lab10.py") -> str:
        self._ruta(objetivo)
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", objetivo],
            cwd=str(self.raiz),
            capture_output=True,
            text=True,
            timeout=30,
        )
        out = (proc.stdout + "\n" + proc.stderr).strip()
        return f"EXIT={proc.returncode}\n{out}"

    def ver_cambios(self) -> str:
        proc = subprocess.run(
            ["git", "diff", "--", "src/"],
            cwd=str(self.raiz),
            capture_output=True,
            text=True,
            timeout=15,
        )
        out = proc.stdout.strip()
        return out if out else "(sin cambios en src/)"

    def ejecutar_comando(self, comando: str) -> str:
        partes = comando.strip().split()
        if partes and partes[0] == "python":
            partes[0] = sys.executable
        proc = subprocess.run(
            partes,
            cwd=str(self.raiz),
            capture_output=True,
            text=True,
            timeout=30,
        )
        out = (proc.stdout + "\n" + proc.stderr).strip()
        return f"EXIT={proc.returncode}\n{out[:1200]}"

    def mapa_repo(self, subdir: str = "src") -> str:
        """Herramienta E4: analiza módulos Python con ast para extraer clases y firmas."""
        base = self._ruta(subdir)
        if not base.exists():
            return f"ERROR: no existe {subdir}"
        resumen: List[str] = []
        for p in sorted(base.rglob("*.py")):
            if "__pycache__" in p.parts:
                continue
            rel = str(p.relative_to(self.raiz)).replace("\\", "/")
            tree = ast.parse(p.read_text(encoding="utf-8"), filename=rel)
            items: List[str] = []
            for node in tree.body:
                if isinstance(node, ast.ClassDef):
                    metodos = [m.name for m in node.body if isinstance(m, ast.FunctionDef)]
                    items.append(f"  class {node.name} (L{node.lineno}): {', '.join(metodos)}")
                elif isinstance(node, ast.FunctionDef):
                    args = [a.arg for a in node.args.args]
                    items.append(f"  def {node.name}({', '.join(args)}) (L{node.lineno})")
            if items:
                resumen.append(f"{rel}:")
                resumen.extend(items)
        return "\n".join(resumen) if resumen else "(sin definiciones Python)"

    def anotar(self, texto: str) -> str:
        """Memoria de pizarra E4: agrega una nota o hipótesis en notas.md dentro del sandbox."""
        p = self._ruta(self.ruta_notas)
        p.parent.mkdir(parents=True, exist_ok=True)
        previo = p.read_text(encoding="utf-8") if p.exists() else "# Notas del Agente (Memoria de Pizarra)\n\n"
        nuevo = previo + f"- {texto.strip()}\n"
        p.write_text(nuevo, encoding="utf-8")
        return f"OK: nota guardada en {self.ruta_notas}"

    def leer_notas(self) -> str:
        """Memoria de pizarra E4: lee las notas acumuladas durante la tarea."""
        p = self._ruta(self.ruta_notas)
        if not p.exists():
            return "(sin notas registradas)"
        return p.read_text(encoding="utf-8")
