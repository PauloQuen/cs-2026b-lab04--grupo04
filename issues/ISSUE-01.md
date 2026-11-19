# Issue #01: La válvula no se cierra al perder conexión tras cumplirse el tiempo programado

- **Reportado por:** Técnico de campo — Sector El Pedregal (Majes)
- **Atributo afectado:** QA-01 (Protección / Safety) y ADR-003 (Apagado seguro en controlador)
- **Observado:** En `src/valvulas_riego/operaciones_campo.py::procesar_latido_controlador()`, cuando `segundos_sin_conexion > 10`, el controlador queda esperando confirmación del servidor remoto incluso cuando `segundos_transcurridos_s >= tiempo_programado_s`, devolviendo `{"estado": "ABIERTA", "cerrada": False}`.
- **Esperado:** Al cumplirse `segundos_transcurridos_s >= tiempo_programado_s`, el temporizador local del controlador debe cerrar físicamente la válvula de manera autónoma (`{"estado": "CERRADA", "cerrada": True, "motivo": "cierre_seguro_local"}`) independientemente de si existe o no conectividad con el servidor.
- **Prueba que reproduce el error:** `tests/test_issues_lab10.py::test_issue_01_valvula_cierra_al_perder_conexion`
