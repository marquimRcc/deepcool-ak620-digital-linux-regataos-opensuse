# -*- coding: utf-8 -*-
"""Gerenciamento de persistência de configurações do usuário."""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

from .config import SETTINGS_FILE, CONFIG_DIR

logger = logging.getLogger(__name__)


class SettingsManager:
    """Gerencia a persistência de configurações do usuário."""
    
    # Valores padrão
    DEFAULT_SETTINGS: Dict[str, Any] = {
        'display_mode': 'auto',
        'temp_unit': 'C',
        'alarm_enabled': False,
        'alarm_temp': 80,
    }
    
    def __init__(self, settings_file: Optional[Path] = None):
        """
        Inicializa o gerenciador de configurações.
        
        Args:
            settings_file: Caminho para o arquivo de configurações.
                          Se None, usa o padrão de SETTINGS_FILE.
        """
        self.settings_file = settings_file or SETTINGS_FILE
        self._settings: Dict[str, Any] = self.DEFAULT_SETTINGS.copy()
        self._ensure_config_dir()
    
    def _ensure_config_dir(self) -> None:
        """Garante que o diretório de configuração existe."""
        try:
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Diretório de configuração: {CONFIG_DIR}")
        except Exception as e:
            logger.error(f"Erro ao criar diretório de configuração: {e}")
    
    def load(self) -> Dict[str, Any]:
        """
        Carrega configurações do arquivo.
        
        Returns:
            Dicionário com as configurações carregadas
        """
        if not self.settings_file.exists():
            logger.info("Arquivo de configurações não encontrado, usando padrões")
            return self._settings.copy()
        
        try:
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                loaded_settings = json.load(f)
            
            # Validar e mesclar com padrões
            self._settings = self._validate_and_merge(loaded_settings)
            logger.info(f"Configurações carregadas de {self.settings_file}")
            logger.debug(f"Configurações: {self._settings}")
            
            return self._settings.copy()
            
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao decodificar JSON: {e}")
            logger.warning("Usando configurações padrão")
            return self._settings.copy()
            
        except Exception as e:
            logger.error(f"Erro ao carregar configurações: {e}")
            return self._settings.copy()
    
    def save(self, settings: Dict[str, Any]) -> bool:
        """
        Salva configurações no arquivo.
        
        Args:
            settings: Dicionário com as configurações a serem salvas
            
        Returns:
            True se salvou com sucesso, False caso contrário
        """
        try:
            # Validar antes de salvar
            validated_settings = self._validate_and_merge(settings)
            
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(validated_settings, f, indent=2, ensure_ascii=False)
            
            self._settings = validated_settings
            logger.info(f"Configurações salvas em {self.settings_file}")
            logger.debug(f"Configurações salvas: {validated_settings}")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao salvar configurações: {e}")
            return False
    
    def _validate_and_merge(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida e mescla configurações com valores padrão.
        
        Args:
            settings: Configurações a serem validadas
            
        Returns:
            Configurações validadas e mescladas
        """
        validated: Dict[str, Any] = self.DEFAULT_SETTINGS.copy()
        
        # display_mode
        if 'display_mode' in settings:
            mode = settings['display_mode']
            if mode in ('auto', 'temp', 'util'):
                validated['display_mode'] = mode
            else:
                logger.warning(f"display_mode inválido: {mode}, usando padrão")
        
        # temp_unit
        if 'temp_unit' in settings:
            unit = settings['temp_unit']
            if unit in ('C', 'F'):
                validated['temp_unit'] = unit
            else:
                logger.warning(f"temp_unit inválido: {unit}, usando padrão")
        
        # alarm_enabled
        if 'alarm_enabled' in settings:
            if isinstance(settings['alarm_enabled'], bool):
                validated['alarm_enabled'] = settings['alarm_enabled']
            else:
                logger.warning(f"alarm_enabled inválido, usando padrão")
        
        # alarm_temp
        if 'alarm_temp' in settings:
            temp = settings['alarm_temp']
            if isinstance(temp, (int, float)) and 0 <= temp <= 150:
                validated['alarm_temp'] = int(temp)
            else:
                logger.warning(f"alarm_temp inválido: {temp}, usando padrão")
        
        return validated
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Obtém valor de uma configuração.
        
        Args:
            key: Chave da configuração
            default: Valor padrão se a chave não existir
            
        Returns:
            Valor da configuração ou default
        """
        return self._settings.get(key, default)
    
    def reset(self) -> bool:
        """
        Reseta configurações para os valores padrão.
        
        Returns:
            True se resetou com sucesso, False caso contrário
        """
        logger.info("Resetando configurações para padrão")
        return self.save(self.DEFAULT_SETTINGS.copy())
    
    def delete(self) -> bool:
        """
        Remove o arquivo de configurações.
        
        Returns:
            True se removeu com sucesso, False caso contrário
        """
        try:
            if self.settings_file.exists():
                self.settings_file.unlink()
                logger.info(f"Arquivo de configurações removido: {self.settings_file}")
                return True
            return True
        except Exception as e:
            logger.error(f"Erro ao remover arquivo de configurações: {e}")
            return False
