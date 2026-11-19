# Issue #03: Se acepta humedad negativa o superior al 100 % en lecturas de sensores

- **Reportado por:** Operador de telemetría LoRaWAN — Valle de Majes
- **Atributo afectado:** Integridad de Datos y Fiabilidad (RF-01)
- **Observado:** En `src/valvulas_riego/operaciones_campo.py::registrar_lectura_humedad()`, se aceptan y almacenan valores físicos imposibles como `-12.5 %` o `135.0 %`, distorsionando las políticas de riego automático por goteo.
- **Esperado:** Solo se deben aceptar porcentajes dentro del rango físico válido `0.0 <= humedad_pct <= 100.0`; cualquier lectura fuera de ese intervalo debe lanzar `ValueError("Humedad fuera de rango físico [0, 100]")`.
- **Prueba que reproduce el error:** `tests/test_issues_lab10.py::test_issue_03_rechaza_humedad_negativa_o_imposible`
