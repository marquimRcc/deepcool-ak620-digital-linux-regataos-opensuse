# -*- coding: utf-8 -*-
"""
Controle de cores da borda LED ARGB via OpenRGB.

As fitas LED ARGB do display do cooler DeepCool são conectadas ao
header ARGB 3-pin da placa-mãe e controladas pelo OpenRGB CLI.

Requer: OpenRGB instalado no sistema (openrgb)
"""

import subprocess
import shutil
import re
import logging
from typing import List, Dict, Optional, Tuple

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────
# Cores predefinidas (chave_i18n, hex)
# ──────────────────────────────────────────────────────────────
PRESET_COLORS: List[Tuple[str, str]] = [
    ("color_red",    "#FF0000"),
    ("color_blue",   "#0066FF"),
    ("color_green",  "#00CC44"),
    ("color_purple", "#9933FF"),
    ("color_cyan",   "#00CCCC"),
    ("color_yellow", "#FFCC00"),
    ("color_orange", "#FF6600"),
    ("color_white",  "#FFFFFF"),
    ("color_pink",   "#FF33AA"),
]

# Modos especiais
COLOR_RAINBOW: str = "__rainbow__"
COLOR_OFF: str = "__off__"
COLOR_DEFAULT: str = "#FF0000"


# ──────────────────────────────────────────────────────────────
# Detecção do OpenRGB
# ──────────────────────────────────────────────────────────────
def is_openrgb_available() -> bool:
    """Verifica se o OpenRGB está instalado no sistema."""
    return shutil.which("openrgb") is not None


def _run_openrgb(*args: str, timeout: int = 10) -> Optional[str]:
    """
    Executa um comando OpenRGB e retorna stdout.

    Args:
        *args: Argumentos para o comando openrgb
        timeout: Timeout em segundos

    Returns:
        stdout do comando ou None em caso de erro
    """
    cmd = ["openrgb"] + list(args)
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout
        )
        if result.returncode != 0:
            logger.warning(
                f"OpenRGB retornou código {result.returncode}: "
                f"{result.stderr.strip()}"
            )
            return None
        return result.stdout
    except subprocess.TimeoutExpired:
        logger.error(f"OpenRGB timeout após {timeout}s")
        return None
    except FileNotFoundError:
        logger.error("OpenRGB não encontrado no PATH")
        return None
    except Exception as e:
        logger.error(f"Erro ao executar OpenRGB: {e}")
        return None


# ──────────────────────────────────────────────────────────────
# Detecção de dispositivos ARGB
# ──────────────────────────────────────────────────────────────
def list_devices() -> List[Dict]:
    """
    Lista dispositivos RGB detectados pelo OpenRGB.

    Returns:
        Lista de dicts: [{"id": 0, "name": "..."}, ...]
    """
    output = _run_openrgb("--noautoconnect", "--list-devices", timeout=15)
    if not output:
        return []

    devices: List[Dict] = []
    for line in output.splitlines():
        match = re.match(r"^(\d+):\s+(.+)$", line.strip())
        if match:
            devices.append({
                "id": int(match.group(1)),
                "name": match.group(2).strip(),
            })
    return devices


def find_motherboard_argb_device() -> Optional[int]:
    """
    Tenta encontrar o dispositivo ARGB da placa-mãe automaticamente.

    Returns:
        ID do dispositivo OpenRGB ou None.
    """
    devices = list_devices()
    if not devices:
        return None

    mobo_keywords = [
        "motherboard", "mainboard", "mobo",
        "aura", "mystic", "fusion", "rgb header",
        "argb header", "addressable",
        "asus", "msi", "gigabyte", "asrock",
        "b550", "b650", "x570", "x670", "b450", "b460",
        "z690", "z790", "h670", "b660",
    ]

    for device in devices:
        name_lower = str(device["name"]).lower()
        for keyword in mobo_keywords:
            if keyword in name_lower:
                logger.info(
                    f"Dispositivo ARGB encontrado: "
                    f"[{device['id']}] {device['name']}"
                )
                return int(device["id"])

    # Fallback: primeiro dispositivo
    logger.info(
        f"Usando primeiro dispositivo RGB: "
        f"[{devices[0]['id']}] {devices[0]['name']}"
    )
    return int(devices[0]["id"])


# ──────────────────────────────────────────────────────────────
# Aplicar cores
# ──────────────────────────────────────────────────────────────
def set_color(hex_color: str, device_id: Optional[int] = None) -> bool:
    """
    Define uma cor estática nas LEDs ARGB.

    Args:
        hex_color: Cor em formato hex ("#FF0000" ou "FF0000")
        device_id: ID do dispositivo OpenRGB (None = auto-detect)

    Returns:
        True se a cor foi aplicada com sucesso.
    """
    if not is_openrgb_available():
        logger.warning("OpenRGB não está instalado")
        return False

    color = hex_color.lstrip("#").upper()
    if len(color) != 6 or not all(c in "0123456789ABCDEF" for c in color):
        logger.error(f"Cor hex inválida: {hex_color}")
        return False

    if device_id is None:
        device_id = find_motherboard_argb_device()
    if device_id is None:
        logger.warning("Nenhum dispositivo RGB encontrado")
        return False

    output = _run_openrgb(
        "--noautoconnect",
        "-d", str(device_id),
        "-m", "Static",
        "-c", color,
    )
    if output is not None:
        logger.info(f"Cor #{color} aplicada ao dispositivo {device_id}")
        return True
    return False


def set_rainbow(device_id: Optional[int] = None) -> bool:
    """
    Define o modo arco-íris nas LEDs ARGB.

    Returns:
        True se o modo foi aplicado com sucesso.
    """
    if not is_openrgb_available():
        return False

    if device_id is None:
        device_id = find_motherboard_argb_device()
    if device_id is None:
        return False

    for mode in ["Spectrum Cycle", "Rainbow", "Rainbow Wave",
                 "Color Cycle", "Breathing"]:
        output = _run_openrgb(
            "--noautoconnect",
            "-d", str(device_id),
            "-m", mode,
        )
        if output is not None:
            logger.info(f"Modo {mode} aplicado ao dispositivo {device_id}")
            return True

    logger.warning("Nenhum modo arco-íris encontrado no dispositivo")
    return False


def set_off(device_id: Optional[int] = None) -> bool:
    """Desliga as LEDs ARGB (cor preta)."""
    return set_color("#000000", device_id)


def apply_color_setting(
    color_value: str, device_id: Optional[int] = None
) -> bool:
    """
    Aplica a configuração de cor salva.

    Args:
        color_value: "#RRGGBB", COLOR_RAINBOW, ou COLOR_OFF
        device_id: ID do dispositivo OpenRGB (None = auto)

    Returns:
        True se aplicado com sucesso.
    """
    if color_value == COLOR_RAINBOW:
        return set_rainbow(device_id)
    elif color_value == COLOR_OFF:
        return set_off(device_id)
    else:
        return set_color(color_value, device_id)


def validate_color(color_value: str) -> bool:
    """
    Valida se o valor de cor é válido.

    Args:
        color_value: Valor a validar

    Returns:
        True se é uma cor hex válida, rainbow ou off.
    """
    if color_value in (COLOR_RAINBOW, COLOR_OFF):
        return True
    color = color_value.lstrip("#")
    return (
        len(color) == 6
        and all(c in "0123456789ABCDEFabcdef" for c in color)
    )
