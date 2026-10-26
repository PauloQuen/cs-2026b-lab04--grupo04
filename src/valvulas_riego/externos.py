"""
Servicios y SDKs externos simulados para ChacraSmart Majes (Laboratorio 07).
Representa controladores de hardware de riego de distintos fabricantes,
pasarelas de mensajería SMS, telemetría LoRaWAN y proveedores de IA generativa.
Cada SDK tiene una interfaz, tipos de datos y convenciones incompatibles entre sí.
"""
from __future__ import annotations
from typing import Any, Dict, Tuple


class RainBirdControllerSDK:
    """SDK oficial del controlador RainBird ESP-TM2.
    Opera en minutos, usa API HTTP/JSON y retorna diccionarios de estado."""

    def __init__(self, ip: str = "192.168.1.50", token: str = "rb_tok_secret", fallas: int = 0):
        self.ip = ip
        self.token = token
        self.fallas_restantes = fallas
        self.llamadas = 0

    def abrir_valvula(self, valvula_id: str, duracion_minutos: int) -> Dict[str, Any]:
        self.llamadas += 1
        if self.fallas_restantes > 0:
            self.fallas_restantes -= 1
            raise TimeoutError("RainBird controller no responde en la red local (timeout)")
        return {
            "status": 200,
            "valve_id": valvula_id,
            "state": "OPEN",
            "duration": duracion_minutos,
            "job_id": f"RB-{valvula_id[:4]}-OK"
        }

    def cerrar_valvula(self, valvula_id: str) -> Dict[str, Any]:
        self.llamadas += 1
        if self.fallas_restantes > 0:
            self.fallas_restantes -= 1
            raise TimeoutError("RainBird controller no responde al comando de cierre")
        return {
            "status": 200,
            "valve_id": valvula_id,
            "state": "CLOSED"
        }


class HunterProC_SDK:
    """SDK del programador de riego Hunter Pro-C vía interfaz Serial/RS-485.
    Opera en SEGUNDOS (requiere conversión), usa códigos de estación enteros
    y retorna tuplas (exito: bool, ack_code: str)."""

    def __init__(self, port: str = "COM3", baudrate: int = 9600, fallas: int = 0):
        self.port = port
        self.baudrate = baudrate
        self.fallas_restantes = fallas
        self.llamadas = 0

    def execute_irrigation(self, station_number: int, duration_seconds: int) -> Tuple[bool, str]:
        self.llamadas += 1
        if self.fallas_restantes > 0:
            self.fallas_restantes -= 1
            raise TimeoutError(f"Hunter Pro-C en puerto {self.port} sin respuesta serial")
        return (True, f"ACK_HUNTER_ST_{station_number}_{duration_seconds}S")

    def stop_irrigation(self, station_number: int) -> Tuple[bool, str]:
        self.llamadas += 1
        if self.fallas_restantes > 0:
            self.fallas_restantes -= 1
            raise TimeoutError("Hunter Pro-C no confirma parada de emergencia")
        return (True, f"ACK_HUNTER_STOP_{station_number}")


class TuyaZigbeeRelaySDK:
    """SDK de relé Tuya/Zigbee genérico para electroválvula solenoide.
    Recibe estado booleano y temporizador en segundos; retorna código HTTP numérico."""

    def __init__(self, gateway_id: str = "GW-MAJES-01", fallas: int = 0):
        self.gateway_id = gateway_id
        self.fallas_restantes = fallas
        self.llamadas = 0

    def set_switch(self, switch_id: str, state: bool, auto_off_seconds: int) -> int:
        self.llamadas += 1
        if self.fallas_restantes > 0:
            self.fallas_restantes -= 1
            raise TimeoutError("Tuya Zigbee Gateway timeout")
        return 204 if state else 200


class ServicioSMSPeru:
    """Servicio de mensajería SMS para avisar al agricultor (RF-05)."""

    def __init__(self):
        self.mensajes_enviados = []

    def enviar_sms(self, celular: str, mensaje: str) -> bool:
        self.mensajes_enviados.append({"celular": celular, "mensaje": mensaje})
        return True


class SensorLoraGateway:
    """Pasarela LoRaWAN de sensores de humedad de suelo en Majes."""

    def __init__(self, lectura_fija: float = 14.5):
        self.lectura_fija = lectura_fija

    def obtener_humedad_actual(self, sensor_id: str) -> float:
        return self.lectura_fija


class ClienteLLMSimulado:
    """Cliente simulado de IA (Claude/OpenAI) para pruebas reproducibles sin API Key."""

    def __init__(self, respuesta_predefinida: str = "Recomendación: Aplicar 25 minutos de riego por goteo a baja presión."):
        self.respuesta = respuesta_predefinida
        self.llamadas = 0
        self.prompts_recibidos = []

    def generar(self, prompt: str) -> str:
        self.llamadas += 1
        self.prompts_recibidos.append(prompt)
        return self.respuesta
