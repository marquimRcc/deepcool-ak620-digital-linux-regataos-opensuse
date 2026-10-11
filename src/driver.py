# -*- coding: utf-8 -*-
"""Driver HID - thread que comunica com o cooler DeepCool."""

import time
import threading
import logging
from typing import Dict, Any, Optional

import hid
import psutil

from src.qt import pyqtSignal, QObject
from .config import VENDOR_ID, INTERVAL
from .protocol import build_packet, DisplayMode
from .hardware import get_temperature, get_cpu_usage
from .utils import format_temperature

logger = logging.getLogger(__name__)


class DriverSignals(QObject):
    """Sinais Qt para comunicação entre driver (thread) e GUI."""
    status_updated = pyqtSignal(str, float, int)   # mode, temp_celsius, cpu_percent
    connection_changed = pyqtSignal(bool)           # connected
    error_occurred = pyqtSignal(str)                # error_message


class DeepCoolDriver(threading.Thread):
    """Thread que lê sensores e envia dados para o cooler via HID."""

    def __init__(self, signals: DriverSignals, product_id: int, sensor: str):
        """
        Inicializa o driver.
        
        Args:
            signals: Objeto de sinais Qt para comunicação com GUI
            product_id: Product ID do dispositivo USB
            sensor: Nome do sensor de temperatura
        """
        super().__init__(daemon=True)
        self.signals: DriverSignals = signals
        self.product_id: int = product_id
        self.sensor: str = sensor
        self.running: bool = True
        self.device: Optional[hid.device] = None
        self._device_lock = threading.Lock()
        self._stop_event = threading.Event()

        # Configurações (alteráveis pelo menu)
        self.display_mode: str = "auto"   # "auto", "temp", "util"
        self.temp_unit: str = "C"         # "C" ou "F"
        self.alarm_enabled: bool = False
        self.alarm_temp: int = 80         # Celsius
        
        logger.info(f"Driver inicializado para produto 0x{product_id:04x}, sensor: {sensor}")

    def _connect(self) -> bool:
        """
        Tenta conectar ao dispositivo HID de forma segura.
        
        Returns:
            True se conectado com sucesso
        """
        try:
            with self._device_lock:
                dev = hid.device()
                dev.open(VENDOR_ID, self.product_id)
                dev.set_nonblocking(1)
                
                # Enviar pacote de inicialização
                init_packet: list[int] = build_packet(mode="start")
                dev.write(init_packet)
                self.device = dev
                
            logger.info(f"Conectado ao dispositivo 0x{VENDOR_ID:04x}:0x{self.product_id:04x}")
            self.signals.connection_changed.emit(True)
            return True
            
        except hid.HIDException as e:
            logger.error(f"Erro HID ao conectar: {e}")
            with self._device_lock:
                self.device = None
            self.signals.connection_changed.emit(False)
            self.signals.error_occurred.emit(f"Erro de conexão HID: {e}")
            return False
            
        except OSError as e:
            logger.error(f"Erro de permissão ou dispositivo não encontrado: {e}")
            with self._device_lock:
                self.device = None
            self.signals.connection_changed.emit(False)
            self.signals.error_occurred.emit(
                "Erro de permissão USB. Verifique as regras udev."
            )
            return False
            
        except Exception as e:
            logger.error(f"Erro inesperado ao conectar: {e}", exc_info=True)
            with self._device_lock:
                self.device = None
            self.signals.connection_changed.emit(False)
            self.signals.error_occurred.emit(f"Erro ao conectar: {e}")
            return False

    def _disconnect(self) -> None:
        """Desconecta do dispositivo de forma thread-safe."""
        with self._device_lock:
            if self.device:
                try:
                    self.device.close()
                    logger.info("Dispositivo desconectado")
                except Exception as e:
                    logger.warning(f"Erro ao desconectar dispositivo: {e}")
                finally:
                    self.device = None

    def _is_alarm_active(self, temp_c: float) -> bool:
        """
        Verifica se o alarme deve ser ativado.
        
        Args:
            temp_c: Temperatura em Celsius
            
        Returns:
            True se alarme deve ser ativado
        """
        return self.alarm_enabled and temp_c >= self.alarm_temp

    def _send(self, value: int, mode: DisplayMode, temp_c: Optional[float] = None) -> None:
        """
        Envia pacote para o dispositivo de forma thread-safe.
        
        Args:
            value: Valor a ser exibido
            mode: Modo de exibição
            temp_c: Temperatura em Celsius (opcional, evita releitura redundante)
            
        Raises:
            hid.HIDException: Erro de comunicação HID
            OSError: Erro de I/O
        """
        try:
            if temp_c is None and mode != "util":
                temp_c = get_temperature(self.sensor)

            alarm: bool = self._is_alarm_active(temp_c) if (mode != "util" and temp_c is not None) else False
            data: list[int] = build_packet(value=value, mode=mode, alarm=alarm)
            
            with self._device_lock:
                if self.device is None:
                    raise IOError("Dispositivo não conectado")
                
                self.device.set_nonblocking(1)
                bytes_written: int = self.device.write(data)
                
                if bytes_written == 0:
                    logger.warning("Nenhum byte escrito no dispositivo")
                    raise IOError("Falha ao escrever no dispositivo HID")
                    
            logger.debug(f"Pacote enviado: mode={mode}, value={value}, alarm={alarm}")
            
        except hid.HIDException as e:
            logger.error(f"Erro HID ao enviar dados: {e}")
            raise
        except OSError as e:
            logger.error(f"Erro de I/O ao enviar dados: {e}")
            raise
        except RuntimeError as e:
            logger.error(f"Erro ao ler sensor: {e}")
            raise

    def _cycle_temp(self) -> None:
        """
        Envia temperatura e emite status.
        
        Raises:
            RuntimeError: Erro ao ler sensores
            hid.HIDException: Erro de comunicação HID
        """
        temp_c: float = get_temperature(self.sensor)
        usage: int = get_cpu_usage()
        temp_display, _ = format_temperature(temp_c, self.temp_unit)
        mode: DisplayMode = "temp_c" if self.temp_unit == "C" else "temp_f"
        
        self._send(temp_display, mode, temp_c=temp_c)
        self.signals.status_updated.emit("temp", temp_c, usage)

    def _cycle_util(self) -> None:
        """
        Envia uso de CPU e emite status.
        
        Raises:
            RuntimeError: Erro ao ler sensores
            hid.HIDException: Erro de comunicação HID
        """
        temp_c: float = get_temperature(self.sensor)
        usage: int = get_cpu_usage()
        
        self._send(usage, "util", temp_c=temp_c)
        self.signals.status_updated.emit("util", temp_c, usage)

    def run(self) -> None:
        """Loop principal do driver com controle de parada imediata."""
        logger.info("Thread do driver iniciada")
        
        # Inicializar leitura de CPU
        try:
            psutil.cpu_percent(interval=None)
        except Exception as e:
            logger.error(f"Erro ao inicializar leitura de CPU: {e}")

        while not self._stop_event.is_set():
            try:
                # Tentar conectar se desconectado
                if self.device is None:
                    if not self._connect():
                        logger.debug("Aguardando para tentar reconectar...")
                        if self._stop_event.wait(3):
                            break
                        continue

                # Executar ciclo de acordo com o modo
                if self.display_mode == "temp":
                    self._cycle_temp()
                    if self._stop_event.wait(INTERVAL):
                        break

                elif self.display_mode == "util":
                    self._cycle_util()
                    if self._stop_event.wait(INTERVAL):
                        break

                else:  # auto
                    self._cycle_temp()
                    if self._stop_event.wait(INTERVAL):
                        break
                    self._cycle_util()
                    if self._stop_event.wait(INTERVAL):
                        break

            except (hid.HIDException, OSError) as e:
                logger.error(f"Erro de comunicação com dispositivo: {e}")
                self._disconnect()
                self.signals.connection_changed.emit(False)
                self.signals.error_occurred.emit("Dispositivo desconectado")
                if self._stop_event.wait(3):
                    break
                
            except RuntimeError as e:
                logger.error(f"Erro ao ler sensores: {e}")
                if self._stop_event.wait(INTERVAL):
                    break
                
            except Exception as e:
                logger.error(f"Erro inesperado no loop do driver: {e}", exc_info=True)
                self._disconnect()
                self.signals.connection_changed.emit(False)
                if self._stop_event.wait(3):
                    break
        
        logger.info("Thread do driver encerrada")

    def stop(self) -> None:
        """Para o driver e desconecta de forma imediata e thread-safe."""
        logger.info("Parando driver...")
        self.running = False
        self._stop_event.set()
        self._disconnect()

    def get_settings(self) -> Dict[str, Any]:
        """
        Retorna configurações atuais (para persistência).
        
        Returns:
            Dicionário com as configurações
        """
        return {
            'display_mode': self.display_mode,
            'temp_unit': self.temp_unit,
            'alarm_enabled': self.alarm_enabled,
            'alarm_temp': self.alarm_temp,
        }

    def apply_settings(self, settings: Dict[str, Any]) -> None:
        """
        Aplica configurações salvas.
        
        Args:
            settings: Dicionário com as configurações
        """
        self.display_mode = settings.get('display_mode', 'auto')
        self.temp_unit = settings.get('temp_unit', 'C')
        self.alarm_enabled = settings.get('alarm_enabled', False)
        self.alarm_temp = settings.get('alarm_temp', 80)
        
        logger.info(f"Configurações aplicadas: {settings}")
