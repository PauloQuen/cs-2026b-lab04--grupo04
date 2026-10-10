<!--
  ChacraSmart Majes — Lab 05 (UML como código) · Caso 9 · Grupo 04
  E6: round-trip — comparación entre el diagrama de diseño (E1/E5) y el
  diagrama obtenido del código con pyreverse (ingeniería inversa).
-->

# Round-trip: del diagrama al código y de vuelta (E6)

> **Ingeniería directa:** Prompt IA (anexo de [bitacora-ia.md](bitacora-ia.md)) → esqueleto Python en
> [`src/valvulas_riego/`](../src/valvulas_riego/) — ver [`dominio.py`](../src/valvulas_riego/dominio.py).
> **Ingeniería inversa:** ejecución real de `pyreverse` (no una imagen prestada):

```bash
.venv/bin/pyreverse -o puml -p valvulas_riego src/valvulas_riego
# genera classes-valvulas-riego-pyreverse.puml y packages-valvulas-riego-pyreverse.puml
java -jar plantuml.jar -tpng -o img classes-valvulas-riego-pyreverse.puml
```

**Resultado ejecutado:** [`classes-valvulas-riego-pyreverse.puml`](classes-valvulas-riego-pyreverse.puml) ·
PNG: [`img/classes_valvulas_riego.png`](img/classes_valvulas_riego.png) (el nombre de salida lo decide el
`@startuml classes_valvulas_riego`, y se conserva tal cual por reproducibilidad).
Paquetes: [`packages-valvulas-riego-pyreverse.puml`](packages-valvulas-riego-pyreverse.puml) →
[`img/packages_valvulas_riego.png`](img/packages_valvulas_riego.png)

---

## Tabla de diferencias (diagrama de diseño vs. diagrama del código)

| Diferencia observada | Causa | Acción |
|---|---|---|
| La composición `Parcela 1 *-- 0..* Valvula` (y `Parcela – LecturaHumedad`) no aparece; las líneas figuran como atributo `valvulas : list[Valvula]` | `pyreverse` no infiere asociaciones desde colecciones tipadas | **Ninguna sobre el diseño** (limitación de la herramienta): el diagrama de diseño se mantiene. Se compensa en código: `ServicioRiego.programar_riego()` rechaza una parcela sin válvula disponible (regla C3) |
| No hay multiplicidades en el diagrama del código | El código no expresa multiplicidades | **Validación en código**: la duración de apertura se valida contra `apertura_maxima_min` (QA-01) y la ausencia de válvulas disponibles lanza `ValueError` |
| Los puertos `ControladorValvula`, `Notificador` y `RepositorioRiego` aparecen como **clases** `{abstract}`, no como **interfaces**; además los métodos de `ControladorCampoAdapter`/`MensajeriaAdapter` figuran `{abstract}` pese a estar implementados | Python implementa interfaces con `ABC`; `astroid`/`pyreverse` marcan `{abstract}` a todo método cuyo cuerpo solo `raise NotImplementedError`, sin distinguir la implementación | **Aceptable en Python; se documenta.** Los puertos se mantienen como `ABC` en código y como `<<puerto>>` en el diseño (misma intención, notación distinta) |
| `ServicioRiego.evaluar_riego_automatico()` figura `{abstract}` **sin ser** `@abstractmethod` | Mismo motivo que la fila anterior: su cuerpo solo `raise NotImplementedError` (stub de orquestación, E4) | **Se documenta** como stub intencional del módulo; es el punto de entrada del riego automático |
| No aparecen las dependencias `ServicioRiego →` (puertos y entidades) del diseño | Se inyectan por constructor (`__init__`); `pyreverse` no infiere dependencias de parámetros privados | **Ninguna**: el diseño (E1) se mantiene como fuente de verdad de las dependencias por puertos (C4) |
| Las operaciones salen en `snake_case` (`abrir(valvula_id, duracion_min)`) frente al `camelCase` del diagrama (`abrir(valvulaId, duracionMin)`) | Convención de Python (PEP 8) | **Aceptable; se documenta la equivalencia** (regla C5) |
| El diagrama de **paquetes** de `pyreverse` solo muestra 2 paquetes (`valvulas_riego`, `valvulas_riego.dominio`), no los 6 del diseño (E5) | `pyreverse` agrupa por estructura de archivos, no por módulos de dominio de un monolito | **Ninguna**: el diseño de paquetes (E5) se mantiene como vista de desarrollo del ADR-001 |

> De las 7 diferencias, **3 se documentan como limitaciones de la herramienta**, **2 se aceptan como convención
> de Python** y **2 se compensan con validaciones en el código** (C3 y QA-01). Ninguna obligó a cambiar el
> diagrama de diseño.