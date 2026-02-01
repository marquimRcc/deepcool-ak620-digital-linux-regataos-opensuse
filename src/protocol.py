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

# Modos do byte[1]
MODE_CELSIUS = 19
MODE_FAHRENHEIT = 35
MODE_PERCENT = 76
MODE_INIT = 170


def get_bar_value(input_value):
    """Calcula valor da barra do topo (0-10)."""
    if input_value <= 0:
        return 0
    return (input_value - 1) // 10 + 1


def build_packet(value=0, mode="util", alarm=False):
    """
    Constrói pacote HID de 64 bytes.

    Args:
        value: Valor numérico para exibir (0-999)
        mode: "temp_c", "temp_f", "util" ou "start"
        alarm: True para piscar o display
    
    Returns:
        list: Pacote de 64 bytes
    """
    data = [16] + [0] * 63

    # Modo
    mode_map = {
        "temp_c": MODE_CELSIUS,
        "temp_f": MODE_FAHRENHEIT,
        "util": MODE_PERCENT,
        "start": MODE_INIT,
    }
    data[1] = mode_map.get(mode, MODE_CELSIUS)

    # Init não precisa de mais nada
    if mode == "start":
        return data

    # Barra
    data[2] = get_bar_value(value)

    # Dígitos
    numbers = [int(c) for c in str(max(0, min(999, value)))]
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
