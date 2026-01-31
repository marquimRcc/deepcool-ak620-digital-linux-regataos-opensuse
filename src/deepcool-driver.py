#!/usr/bin/env python3.11
# -*- coding: utf-8 -*-
"""
DeepCool Digital Driver - Regata OS / openSUSE
https://github.com/marquimRcc/deepcool-ak620-digital-linux-regataos-opensuse

Based on: https://github.com/raghulkrishna/deepcool-ak620-digital-linux
 (cloude.ai, v: Opus 4.5)
"""
import os
import sys
import time
import hid
import psutil
from datetime import datetime

# Configuração via variáveis de ambiente
VENDOR_ID = 0x3633
PRODUCT_ID = int(os.environ.get('PRODUCT_ID', '0x0004'), 16)
SENSOR = os.environ.get('SENSOR', 'coretemp')
TEMP_UNIT = os.environ.get('TEMP_UNIT', 'C')
INTERVAL = 2  # segundos

# Cores ANSI
class C:
    R, G, Y, B, M, N, D = '\033[91m', '\033[92m', '\033[93m', '\033[94m', '\033[95m', '\033[0m', '\033[2m'


def ts():
    """Timestamp atual"""
    return datetime.now().strftime('%H:%M:%S')


def log(icon, color, msg):
    """Log formatado"""
    print(f"{C.D}[{ts()}]{C.N} {color}{icon}{C.N} {msg}")
    sys.stdout.flush()


def log_display(mode, value, bar_value):
    """Log do display com barra visual"""
    if mode == 'temp':
        color = C.G if value < 60 else C.Y if value < 80 else C.R
        unit = '°F' if TEMP_UNIT == 'F' else '°C'
        val_str = f"{color}{value:3d}{unit}{C.N}"
        mode_str = f"{C.B}[🌡️ TEMP]{C.N}"
    else:
        color = C.M
        val_str = f"{color}{value:3d} %{C.N}"
        mode_str = f"{C.M}[📊 CPU%]{C.N}"
    
    bar = '█' * bar_value + '░' * (10 - bar_value)
    print(f"{C.D}[{ts()}]{C.N} {mode_str} Display: {val_str} │ Barra: [{C.G}{bar}{C.N}]")
    sys.stdout.flush()


def get_bar_value(input_value):
    """Calcula valor da barra (0-10) - protocolo original"""
    if input_value <= 0:
        return 0
    return (input_value - 1) // 10 + 1


def get_data(value=0, mode="util"):
    """
    Constrói pacote HID - protocolo original
    
    mode="start": pacote de inicialização
    mode="temp":  mostra temperatura (°C ou °F)
    mode="util":  mostra porcentagem CPU (%)
    """
    base_data = [16] + [0 for i in range(64 - 1)]
    numbers = [int(char) for char in str(value)]
    base_data[2] = get_bar_value(value)
    
    if mode == "util":
        base_data[1] = 76   # Símbolo %
    elif mode == "start":
        base_data[1] = 170  # Inicialização
        return base_data
    elif mode == "temp":
        base_data[1] = 19 if TEMP_UNIT == 'C' else 35  # °C ou °F
    
    # Preenche dígitos
    if len(numbers) == 1:
        base_data[5] = numbers[0]
    elif len(numbers) == 2:
        base_data[4] = numbers[0]
        base_data[5] = numbers[1]
    elif len(numbers) == 3:
        base_data[3] = numbers[0]
        base_data[4] = numbers[1]
        base_data[5] = numbers[2]
    
    return base_data


def get_temperature():
    """Obtém temperatura e retorna pacote"""
    try:
        temp = psutil.sensors_temperatures()[SENSOR][0].current
        if TEMP_UNIT == 'F':
            temp = (temp * 9/5) + 32
        temp = round(temp)
    except (KeyError, IndexError):
        temp = 0
    return temp, get_data(value=temp, mode="temp")


def get_utils():
    """Obtém uso de CPU e retorna pacote"""
    utils = round(psutil.cpu_percent())
    return utils, get_data(value=utils, mode="util")


def main():
    unit_symbol = '°F' if TEMP_UNIT == 'F' else '°C'
    print(f"\n{C.B}══════════════════════════════════════════════════════{C.N}")
    print(f"{C.G}  DeepCool Digital - Regata OS / openSUSE{C.N}")
    print(f"  Sensor: {C.Y}{SENSOR}{C.N} │ Device: {C.Y}{hex(VENDOR_ID)}:{hex(PRODUCT_ID)}{C.N}")
    print(f"  Unidade: {C.Y}{unit_symbol}{C.N} │ Intervalo: {C.Y}{INTERVAL}s{C.N}")
    print(f"{C.B}══════════════════════════════════════════════════════{C.N}\n")
    
    h = None
    
    while True:
        try:
            # Conectar se necessário
            if h is None:
                log('▶', C.Y, f'Conectando ({hex(VENDOR_ID)}:{hex(PRODUCT_ID)})...')
                h = hid.device()
                h.open(VENDOR_ID, PRODUCT_ID)
                h.set_nonblocking(1)
                h.write(get_data(mode="start"))
                log('✓', C.G, 'Conectado!')
                print("")
                psutil.cpu_percent()
                time.sleep(0.5)
            
            # TEMPERATURA
            temp, temp_packet = get_temperature()
            h.set_nonblocking(1)
            h.write(temp_packet)
            log_display('temp', temp, get_bar_value(temp))
            time.sleep(INTERVAL)
            
            # USO DE CPU
            utils, utils_packet = get_utils()
            h.set_nonblocking(1)
            h.write(utils_packet)
            log_display('util', utils, get_bar_value(utils))
            time.sleep(INTERVAL)
            
        except KeyboardInterrupt:
            print(f"\n{C.Y}▶ Interrompido pelo usuário{C.N}")
            break
            
        except Exception as e:
            log('✗', C.R, f'Erro: {e}')
            if h:
                try:
                    h.close()
                except:
                    pass
                h = None
            log('▶', C.Y, 'Reconectando em 3s...')
            time.sleep(3)
    
    # Cleanup
    if h:
        try:
            h.close()
        except:
            pass
    log('✓', C.G, 'Driver encerrado')


if __name__ == "__main__":
    import signal
    signal.signal(signal.SIGTERM, lambda s, f: sys.exit(0))
    signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))
    main()
