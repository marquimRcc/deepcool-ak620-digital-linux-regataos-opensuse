# -*- coding: utf-8 -*-
"""Driver HID - thread que comunica com o cooler DeepCool."""

import time
import threading

import hid
import psutil
from PyQt5.QtCore import pyqtSignal, QObject

from .config import VENDOR_ID, INTERVAL
from .protocol import build_packet
from .hardware import get_temperature, get_cpu_usage


class DriverSignals(QObject):
    """Sinais Qt para comunicação entre driver (thread) e GUI."""
    status_updated = pyqtSignal(str, float, int)   # mode, temp_celsius, cpu_percent
    connection_changed = pyqtSignal(bool)           # connected


class DeepCoolDriver(threading.Thread):
    """Thread que lê sensores e envia dados para o cooler via HID."""

    def __init__(self, signals, product_id, sensor):
        super().__init__(daemon=True)
        self.signals = signals
        self.product_id = product_id
        self.sensor = sensor
        self.running = True
        self.device = None

        # Configurações (alteráveis pelo menu)
        self.display_mode = "auto"   # "auto", "temp", "util"
        self.temp_unit = "C"         # "C" ou "F"
        self.alarm_enabled = False
        self.alarm_temp = 80         # Celsius

    def _connect(self):
        """Tenta conectar ao dispositivo HID."""
        try:
            self.device = hid.device()
            self.device.open(VENDOR_ID, self.product_id)
            self.device.set_nonblocking(1)
            self.device.write(build_packet(mode="start"))
            self.signals.connection_changed.emit(True)
            return True
        except Exception:
            self.device = None
            self.signals.connection_changed.emit(False)
            return False

    def _disconnect(self):
        """Desconecta do dispositivo."""
        if self.device:
            try:
                self.device.close()
            except Exception:
                pass
            self.device = None

    def _temp_for_display(self, temp_c):
        """Converte temperatura para unidade configurada."""
        if self.temp_unit == 'F':
            return round((temp_c * 9 / 5) + 32)
        return round(temp_c)

    def _is_alarm_active(self, temp_c):
        """Verifica se o alarme deve ser ativado."""
        return self.alarm_enabled and temp_c >= self.alarm_temp

    def _send(self, value, mode):
        """Envia pacote para o dispositivo."""
        alarm = self._is_alarm_active(get_temperature(self.sensor)) if mode != "util" else False
        data = build_packet(value=value, mode=mode, alarm=alarm)
        self.device.set_nonblocking(1)
        self.device.write(data)

    def _cycle_temp(self):
        """Envia temperatura e emite status."""
        temp_c = get_temperature(self.sensor)
        usage = get_cpu_usage()
        temp_display = self._temp_for_display(temp_c)
        mode = "temp_c" if self.temp_unit == "C" else "temp_f"
        self._send(temp_display, mode)
        self.signals.status_updated.emit("temp", temp_c, usage)

    def _cycle_util(self):
        """Envia uso de CPU e emite status."""
        temp_c = get_temperature(self.sensor)
        usage = get_cpu_usage()
        self._send(usage, "util")
        self.signals.status_updated.emit("util", temp_c, usage)

    def run(self):
        """Loop principal do driver."""
        psutil.cpu_percent()
        time.sleep(0.5)

        while self.running:
            try:
                if self.device is None:
                    if not self._connect():
                        time.sleep(3)
                        continue

                if self.display_mode == "temp":
                    self._cycle_temp()
                    time.sleep(INTERVAL)

                elif self.display_mode == "util":
                    self._cycle_util()
                    time.sleep(INTERVAL)

                else:  # auto
                    self._cycle_temp()
                    time.sleep(INTERVAL)
                    if not self.running:
                        break
                    self._cycle_util()
                    time.sleep(INTERVAL)

            except Exception:
                self._disconnect()
                self.signals.connection_changed.emit(False)
                time.sleep(3)

    def stop(self):
        """Para o driver e desconecta."""
        self.running = False
        self._disconnect()

    def get_settings(self):
        """Retorna configurações atuais (para preservar no restart)."""
        return {
            'display_mode': self.display_mode,
            'temp_unit': self.temp_unit,
            'alarm_enabled': self.alarm_enabled,
            'alarm_temp': self.alarm_temp,
        }

    def apply_settings(self, settings):
        """Aplica configurações salvas."""
        self.display_mode = settings.get('display_mode', 'auto')
        self.temp_unit = settings.get('temp_unit', 'C')
        self.alarm_enabled = settings.get('alarm_enabled', False)
        self.alarm_temp = settings.get('alarm_temp', 80)
