# -*- coding: utf-8 -*-
"""Internacionalização - detecção de idioma e traduções."""

import os

TRANSLATIONS = {
    "pt": {
        "display_switch": "Chave de exibição",
        "temperature": "Temperatura",
        "utilization": "Utilização",
        "automatic": "Automático",
        "temp_display": "Mostrador de temperatura",
        "alarm_control": "Controle de alarme",
        "alarm_off": "Desligado",
        "launch_startup": "Executar na inicialização",
        "support": "Suporte",
        "website": "Website",
        "version": "Versão",
        "restart": "Reinicialização",
        "exit": "Saída",
        "connected": "Conectado",
        "disconnected": "Desconectado",
        "connecting": "Conectando...",
        "already_running": "já está em execução.",
    },
    "en": {
        "display_switch": "Display Switch",
        "temperature": "Temperature",
        "utilization": "Utilization",
        "automatic": "Automatic",
        "temp_display": "Temperature Display",
        "alarm_control": "Alarm Control",
        "alarm_off": "Off",
        "launch_startup": "Launch at startup",
        "support": "Support",
        "website": "Website",
        "version": "Version",
        "restart": "Restart",
        "exit": "Exit",
        "connected": "Connected",
        "disconnected": "Disconnected",
        "connecting": "Connecting...",
        "already_running": "is already running.",
    },
}

_current_lang = None


def detect_language():
    """Detecta idioma do sistema sem usar locale.getdefaultlocale (deprecated)."""
    global _current_lang
    if _current_lang:
        return _current_lang

    # Verificar variáveis de ambiente na ordem de prioridade
    for var in ('LC_ALL', 'LC_MESSAGES', 'LANG', 'LANGUAGE'):
        lang = os.environ.get(var, '')
        if lang.startswith('pt'):
            _current_lang = 'pt'
            return 'pt'

    _current_lang = 'en'
    return 'en'


def tr(key, **kwargs):
    """Retorna texto traduzido para o idioma atual."""
    lang = detect_language()
    text = TRANSLATIONS.get(lang, TRANSLATIONS['en']).get(key, key)
    if kwargs:
        text = text.format(**kwargs)
    return text
