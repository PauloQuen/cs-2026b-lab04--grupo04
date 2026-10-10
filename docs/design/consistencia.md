<!--
  ChacraSmart Majes — Lab 05 (UML como código) · Caso 9 · Grupo 04
  E7: revisión de consistencia C1–C5 sobre los cinco diagramas.
  Método: Prompt IA auditor (anexo de bitacora-ia.md) → hallazgos → verificación
  del equipo → veredicto. Regla de oro: la IA propone, el equipo decide y verifica.
--->

# Revisión de consistencia (E7)

Se aplicó el Prompt IA de auditoría a los cinco diagramas de `docs/design/`:
[`clases.puml`](clases.puml), [`secuencia-programar-riego.puml`](secuencia-programar-riego.puml),
[`estados-valvula.mmd`](estados-valvula.mmd), [`actividades-riego-automatico.puml`](actividades-riego-automatico.puml)
y [`paquetes.puml`](paquetes.puml), contra las reglas C1–C5 de la Tabla 2 de la guía. Cada hallazgo se
**verificó contra los archivos** (no se aceptó a ciegas): 1 hallazgo real corregido y **2 falsos positivos
rechazados**.

| Regla | Hallazgo de la IA | Verificación del equipo | Veredicto |
|---|---|---|---|
| C1 | *"Los mensajes del diagrama de secuencia dirigidos a objetos corresponden a operaciones de sus clases."* (sin observaciones nuevas) | Verificación manual mensaje por mensaje contra `clases.puml`: `buscarValvulasPorParcela`, `guardarProgramacion`, `iniciar`, `finalizar`, `abrir`, `confirmarApertura`, `cerrar`, `notificarAlerta` — todas existen. La corrección por C1 ya se aplicó en E2 | **Aceptado** |
| C2 | *"La transición `FALLA --> [*]` no corresponde a ninguna operación de la clase."* | **Falso positivo.** `FALLA` es un **estado final**; la guía y el ejemplo docente (`ENTREGADO --> [*]`, `CANCELADO --> [*]`) no exigen operación para las transiciones hacia `[*]`. La C2 se cumple: todas las transiciones *entre estados* usan operaciones de `Valvula` (`abrir`, `confirmarApertura`, `cerrar`, `confirmarCierre`, `fallarCierreSeguro`) | **Rechazada (falso positivo)**, con evidencia: `estados-valvula.mmd` y ejemplo docente |
| C3 | *"La multiplicidad `Parcela 1 *-- 1..* Valvula` es inconsistente con RF-06: el técnico registra la parcela y luego instala las válvulas, por lo que una parcela puede existir sin válvula."* | **Correcto.** Efectivamente, nada en el enunciado obliga a que toda parcela nazca con válvula (el sensor de humedad puede estar sin válvula instalada). Se corrigió a **`0..*`** en `clases.puml` y se re-verificó el código: `ServicioRiego.programar_riego()` ya rechaza la parcela sin válvulas con `ValueError`. Las demás multiplicidades (`1..0..*`, `1..0..*`, `0..*..1`) se confirmaron coherentes con los criterios de aceptación | **Corregida** — `Parcela–Valvula` pasa a `0..*`; PNG y código re-verificados |
| C4 | *"Existe un ciclo: `programacion → lecturas → alertas → dispositivos` y `dispositivos → compartido`, luego `compartido` conduce de vuelta a `programacion`."* | **Falso positivo.** Se trazó el grafo dirigido real del `paquetes.puml`: `programacion → {lecturas, control_valvulas}`, `lecturas → alertas`, `{control_valvulas, alertas} → dispositivos`, todos → `compartido`. **No existe la arista `dispositivos → programacion` ni `compartido → *`**: es un DAG (orden topológico válido), no hay ciclos (la IA leyó la nota '*control_valvulas NO depende de programacion*' como una dependencia) | **Rechazada (falso positivo)** — grafo acíclico verificado arista por arista |
| C5 | *"Los nombres usan el lenguaje del dominio y son iguales en diagramas, código e historias."* (con la salvedad de `snake_case`) | `Valvula`, `Parcela`, `ProgramacionRiego`, `LecturaHumedad`, `Agricultor`, `estado_valvula` son idénticos en `clases.puml`, `estados-valvula.mmd`, `historia.md` y `src/valvulas_riego/dominio.py`. La equivalencia `abrir(duracionMin)` ↔ `abrir(duracion_min)` (PEP 8) está documentada en `round-trip.md` | **Aceptado** |

**Resumen de veredictos:** 2 aceptados · 1 corregido (C3) · 2 falsos positivos rechazados (C2, C4). La corrección
C3 (multiplicidad `Parcela–Valvula 0..*`) se propagó al diagrama y al round-trip; no cambió el ADR-001 ni generó
ADR nuevo porque no hubo ciclo.