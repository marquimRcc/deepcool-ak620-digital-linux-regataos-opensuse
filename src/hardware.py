# -*- coding: utf-8 -*-
"""Detecção de hardware: sensor, device USB e modelo."""

import subprocess
import psutil

from .config import KNOWN_MODELS


def detect_sensor():
    """Detecta o sensor de temperatura da CPU."""
    temps = psutil.sensors_temperatures()

    # Prioridade: Intel, AMD, AMD alternativo
    for name in ['coretemp', 'k10temp', 'zenpower']:
        if name in temps and temps[name]:
            return name

    # Fallback: primeiro sensor válido
    for name, entries in temps.items():
        if entries and name not in ['acpitz', 'nvme']:
            return name

    return 'coretemp'


def detect_product_id():
    """Detecta o Product ID do dispositivo DeepCool via lsusb."""
    try:
        result = subprocess.run(['lsusb'], capture_output=True, text=True)
        for line in result.stdout.split('\n'):
            if '3633' in line.lower():
                parts = line.split('ID ')[1].split(' ')[0]
                pid = parts.split(':')[1]
                return int(pid, 16)
    except Exception:
        pass
    return 0x0004  # fallback AK500S


def detect_model(product_id):
    """Retorna nome do modelo pelo Product ID."""
    return KNOWN_MODELS.get(product_id, f"DeepCool (0x{product_id:04x})")


def get_temperature(sensor):
    """Lê temperatura atual do sensor (em Celsius)."""
    try:
        return psutil.sensors_temperatures()[sensor][0].current
    except (KeyError, IndexError):
        return 0.0


def get_cpu_usage():
    """Lê uso atual da CPU (percentual)."""
    try:
        return round(psutil.cpu_percent())
    except Exception:
        return 0
