# Issue #02: Se permite iniciar riego en el turno de otro usuario

- **Reportado por:** Junta de Usuarios / Comisión de Regantes San Camilo (Majes)
- **Atributo afectado:** Seguridad e Integridad Multitenencia (QA-05 / ADR-008)
- **Observado:** En `src/valvulas_riego/operaciones_campo.py::iniciar_riego_en_turno()`, solo se valida que `volumen_m3 > 0`, pero no se verifica que el `solicitante_id` coincida con `parcela_propietario_id` ni con `turno_asignado_id`. Cualquier agricultor puede activar el riego en la parcela o turno de otro regante.
- **Esperado:** Si `solicitante_id != parcela_propietario_id` o `solicitante_id != turno_asignado_id`, el sistema debe lanzar `PermissionError("No autorizado: el turno pertenece a otro agricultor")` y no autorizar la apertura.
- **Prueba que reproduce el error:** `tests/test_issues_lab10.py::test_issue_02_bloquea_riego_en_turno_ajeno`
