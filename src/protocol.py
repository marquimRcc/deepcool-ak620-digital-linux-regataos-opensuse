# -*- coding: utf-8 -*-
"""
Protocolo HID DeepCool AK Series Digital.

Pacote de 64 bytes:
  [0]  = 16       (comando)
  [1]  = modo     (19=°C, 35=°F, 76=%, 170=init)
  [2]  = barra    (0-10, uso de CPU)
  [3]  = centena  (dígito ou 0=vazio)
  [4]  = dezena   (dígito ou 0=vazio)
  [5]  = unidade  (dígito)
  [6]  = alarme   (0=off, 1=piscar)
  [7-63] = 0

Baseado em:
  - https://github.com/raghulkrishna/deepcool-ak620-digital-linux
  - https://github.com/Algorithm0/deepcool-digital-info
  - Issue #9 (Tasshack): protocolo HID decodificado
"""

from typing import Literal

# Modos do byte[1]
MODE_CELSIUS: int = 19
MODE_FAHRENHEIT: int = 35
MODE_PERCENT: int = 76
MODE_INIT: int = 170

# Type alias para modos válidos
DisplayMode = Literal["temp_c", "temp_f", "util", "start"]


def get_bar_value(input_value: int) -> int:
    """
    Calcula valor da barra do topo (0-10).
    
    Args:
        input_value: Valor de entrada (0-100)
        
    Returns:
        Valor da barra (0-10)
        
    Example:
        >>> get_bar_value(0)
        0
        >>> get_bar_value(15)
        2
        >>> get_bar_value(100)
        10
    """
    if input_value <= 0:
        return 0
    return min((input_value - 1) // 10 + 1, 10)


def build_packet(value: int = 0, mode: DisplayMode = "util", alarm: bool = False) -> list[int]:
    """
    Constrói pacote HID de 64 bytes.

    Args:
        value: Valor numérico para exibir (0-999)
        mode: Modo de exibição ("temp_c", "temp_f", "util" ou "start")
        alarm: True para piscar o display
    
    Returns:
        Pacote de 64 bytes como lista de inteiros
        
    Example:
        >>> packet = build_packet(25, "temp_c", False)
        >>> len(packet)
        64
        >>> packet[0]
        16
    """
    data: list[int] = [16] + [0] * 63

    # Modo
    mode_map: dict[DisplayMode, int] = {
        "temp_c": MODE_CELSIUS,
        "temp_f": MODE_FAHRENHEIT,
        "util": MODE_PERCENT,
        "start": MODE_INIT,
    }
    data[1] = mode_map.get(mode, MODE_CELSIUS)

    # Init não precisa de mais nada
    if mode == "start":
        return data

    # Limitar valor entre 0 e 999
    clamped_value: int = max(0, min(999, value))

    # Barra
    data[2] = get_bar_value(clamped_value)

    # Dígitos
    numbers: list[int] = [int(c) for c in str(clamped_value)]
    if len(numbers) == 1:
        data[5] = numbers[0]
    elif len(numbers) == 2:
        data[4] = numbers[0]
        data[5] = numbers[1]
    elif len(numbers) == 3:
        data[3] = numbers[0]
        data[4] = numbers[1]
        data[5] = numbers[2]

    # Alarme
    if alarm:
        data[6] = 1

    return data
