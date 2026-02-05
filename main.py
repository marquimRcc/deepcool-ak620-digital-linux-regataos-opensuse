#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DeepCool Digital - System Tray App
Para Regata OS / openSUSE (KDE Plasma)

https://github.com/marquimRcc/deepcool-ak620-digital-linux-regataos-opensuse
"""

import sys
import fcntl
import logging
from pathlib import Path
from typing import Optional, TextIO

from PyQt5.QtWidgets import QApplication, QMessageBox

from src.config import APP_DISPLAY_NAME, LOCK_FILE, LOG_FILE
from src.i18n import tr
from src.hardware import detect_product_id, detect_model, detect_sensor
from src.tray import DeepCoolTray


def setup_logging() -> None:
    """Configura o sistema de logging."""
    log_dir: Path = Path(LOG_FILE).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler()
        ]
    )


def acquire_lock() -> TextIO:
    """
    Adquire lock de instância única usando gerenciador de contexto.
    
    Returns:
        Arquivo de lock aberto
        
    Raises:
        RuntimeError: Se já existe uma instância rodando
    """
    try:
        lock_file: TextIO = open(LOCK_FILE, 'w')
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        return lock_file
    except IOError as e:
        raise RuntimeError(f"{APP_DISPLAY_NAME} {tr('already_running')}") from e
    except Exception as e:
        raise RuntimeError(f"Erro ao criar arquivo de lock: {e}") from e


def release_lock(lock_file: Optional[TextIO]) -> None:
    """
    Libera o lock de instância única.
    
    Args:
        lock_file: Arquivo de lock a ser liberado
    """
    if lock_file is not None:
        try:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
            lock_file.close()
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.warning(f"Erro ao liberar lock: {e}")


def main() -> None:
    """Função principal da aplicação."""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info(f"Iniciando {APP_DISPLAY_NAME}...")
    
    lock_file: Optional[TextIO] = None
    exit_code: int = 0
    
    try:
        # Prevenir múltiplas instâncias
        lock_file = acquire_lock()
        
        # Qt App
        app: QApplication = QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(False)
        app.setApplicationName(APP_DISPLAY_NAME)
        
        # Detectar hardware
        logger.info("Detectando hardware...")
        product_id: int = detect_product_id()
        model: str = detect_model(product_id)
        sensor: str = detect_sensor()
        
        logger.info(f"Hardware detectado: {model} (0x{product_id:04x})")
        logger.info(f"Sensor de temperatura: {sensor}")
        
        # Tray
        tray: DeepCoolTray = DeepCoolTray(app, product_id, model, sensor)
        tray.start()
        
        logger.info("Aplicação iniciada com sucesso")
        exit_code = app.exec_()
        
    except RuntimeError as e:
        # Erros esperados (já logados, instância duplicada, etc.)
        logger.error(str(e))
        print(str(e))
        exit_code = 1
        
    except ImportError as e:
        error_msg: str = (
            f"Erro ao importar dependências: {e}\n"
            "Verifique se todas as dependências estão instaladas."
        )
        logger.critical(error_msg)
        QMessageBox.critical(None, "Erro de Dependências", error_msg)
        exit_code = 2
        
    except Exception as e:
        error_msg = f"Erro inesperado ao iniciar aplicação: {e}"
        logger.critical(error_msg, exc_info=True)
        QMessageBox.critical(None, "Erro Fatal", error_msg)
        exit_code = 3
        
    finally:
        # Liberar lock usando função dedicada
        release_lock(lock_file)
    
    logger.info(f"Aplicação encerrada com código {exit_code}")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
