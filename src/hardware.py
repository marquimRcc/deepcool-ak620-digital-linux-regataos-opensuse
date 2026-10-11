# -*- coding: utf-8 -*-
"""Detecção de hardware: sensor, device USB e modelo."""

import subprocess
import logging
from typing import Optional

import psutil

from .config import KNOWN_MODELS

logger = logging.getLogger(__name__)


def detect_sensor() -> str:
    """
    Detecta o sensor de temperatura da CPU.
    
    Returns:
        Nome do sensor detectado
        
    Raises:
        RuntimeError: Se nenhum sensor válido for encontrado
    """
    try:
        temps = psutil.sensors_temperatures()
    except AttributeError as e:
        logger.error("psutil.sensors_temperatures() não disponível neste sistema")
        raise RuntimeError("Sistema não suporta leitura de sensores de temperatura") from e
    except Exception as e:
        logger.error(f"Erro ao acessar sensores de temperatura: {e}")
        raise RuntimeError(f"Erro ao detectar sensores: {e}") from e
    
    if not temps:
        logger.warning("Nenhum sensor de temperatura encontrado")
        raise RuntimeError("Nenhum sensor de temperatura disponível no sistema")
    
    # Prioridade: Intel, AMD, AMD alternativo
    for name in ['coretemp', 'k10temp', 'zenpower']:
        if name in temps and temps[name]:
            logger.info(f"Sensor detectado: {name}")
            return name
    
    # Fallback: primeiro sensor válido (excluindo sensores não confiáveis)
    for name, entries in temps.items():
        if entries and name not in ['acpitz', 'nvme', 'iwlwifi']:
            logger.info(f"Sensor detectado (fallback): {name}")
            return name
    
    # Se chegou aqui, usa coretemp como último recurso
    logger.warning("Nenhum sensor prioritário encontrado, usando 'coretemp' como fallback")
    return 'coretemp'


def detect_product_id() -> int:
    """
    Detecta o Product ID do dispositivo DeepCool via lsusb.
    
    Returns:
        Product ID do dispositivo (hexadecimal)
        
    Raises:
        RuntimeError: Se o dispositivo não for encontrado ou ocorrer erro
    """
    try:
        result = subprocess.run(
            ['lsusb'],
            capture_output=True,
            text=True,
            timeout=5,
            check=True
        )
    except subprocess.TimeoutExpired as e:
        logger.error("Timeout ao executar lsusb")
        raise RuntimeError("Timeout ao detectar dispositivos USB") from e
    except subprocess.CalledProcessError as e:
        logger.error(f"Erro ao executar lsusb: {e}")
        raise RuntimeError("Erro ao listar dispositivos USB") from e
    except FileNotFoundError as e:
        logger.error("Comando lsusb não encontrado")
        raise RuntimeError("Comando 'lsusb' não está instalado") from e
    
    # Procurar pelo vendor ID DeepCool
    vendor_id_str: str = '3633'
    for line in result.stdout.split('\n'):
        if vendor_id_str in line.lower():
            try:
                # Formato: "Bus 001 Device 002: ID 3633:0004 ..."
                id_part: str = line.split('ID ')[1].split(' ')[0]
                vendor: str
                product: str
                vendor, product = id_part.split(':')
                product_id: int = int(product, 16)
                logger.info(f"Dispositivo DeepCool encontrado: 0x{product_id:04x}")
                return product_id
            except (IndexError, ValueError) as e:
                logger.warning(f"Erro ao parsear linha do lsusb: {line}")
                continue
    
    # Dispositivo não encontrado
    error_msg: str = f"Dispositivo DeepCool (Vendor ID: {vendor_id_str}) não encontrado"
    logger.error(error_msg)
    raise RuntimeError(
        f"{error_msg}. Verifique se o cooler está conectado via USB."
    )


def detect_model(product_id: int) -> str:
    """
    Retorna nome do modelo pelo Product ID.
    
    Args:
        product_id: Product ID do dispositivo
        
    Returns:
        Nome do modelo
    """
    model: str = KNOWN_MODELS.get(product_id, f"DeepCool (0x{product_id:04x})")
    logger.debug(f"Modelo identificado: {model}")
    return model


def get_temperature(sensor: str) -> float:
    """
    Lê temperatura atual do sensor (em Celsius).
    Prioriza leituras de encapsulamento geral (Package id 0, Tdie, Tctl)
    antes de fazer fallback para núcleos individuais.
    
    Args:
        sensor: Nome do sensor
        
    Returns:
        Temperatura em Celsius
        
    Raises:
        RuntimeError: Se não for possível ler a temperatura
    """
    try:
        temps = psutil.sensors_temperatures()
        if sensor not in temps:
            logger.error(f"Sensor '{sensor}' não encontrado")
            raise RuntimeError(f"Sensor '{sensor}' não está disponível")
        
        entries = temps[sensor]
        if not entries:
            logger.error(f"Sensor '{sensor}' não retornou dados")
            raise RuntimeError(f"Sensor '{sensor}' não retornou leituras")
        
        # Priorizar labels térmicas representativas do pacote/CPU
        priority_labels = ["package id 0", "package", "tdie", "tctl", "cpu", "core 0"]
        for target in priority_labels:
            for entry in entries:
                if entry.label and target in entry.label.lower() and entry.current is not None:
                    logger.debug(f"Temperatura lida de '{sensor}' [{entry.label}]: {entry.current}°C")
                    return float(entry.current)

        # Fallback: primeira leitura válida disponível
        for entry in entries:
            if entry.current is not None:
                logger.debug(f"Temperatura lida de '{sensor}' [fallback]: {entry.current}°C")
                return float(entry.current)

        raise RuntimeError(f"Sensor '{sensor}' não possui leituras válidas de temperatura")
        
    except (KeyError, IndexError) as e:
        logger.error(f"Erro ao acessar dados do sensor '{sensor}': {e}")
        raise RuntimeError(f"Erro ao ler temperatura do sensor '{sensor}'") from e
    except Exception as e:
        logger.error(f"Erro inesperado ao ler temperatura: {e}")
        raise RuntimeError(f"Erro ao ler temperatura: {e}") from e


def get_cpu_usage() -> int:
    """
    Lê uso atual da CPU (percentual).
    Usa medição não-bloqueante (interval=None) para eliminar latência.
    
    Returns:
        Uso da CPU em percentual (0-100)
        
    Raises:
        RuntimeError: Se não for possível ler o uso da CPU
    """
    try:
        usage: int = round(psutil.cpu_percent(interval=None))
        logger.debug(f"Uso da CPU: {usage}%")
        return usage
    except Exception as e:
        logger.error(f"Erro ao ler uso da CPU: {e}")
        raise RuntimeError(f"Erro ao ler uso da CPU: {e}") from e
