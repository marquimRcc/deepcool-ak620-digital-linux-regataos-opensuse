# -*- coding: utf-8 -*-
"""Funções utilitárias comuns."""

from typing import Union


def celsius_to_fahrenheit(temp_celsius: float) -> int:
    """
    Converte temperatura de Celsius para Fahrenheit.
    
    Args:
        temp_celsius: Temperatura em graus Celsius
        
    Returns:
        Temperatura em graus Fahrenheit (arredondada)
        
    Example:
        >>> celsius_to_fahrenheit(25.0)
        77
        >>> celsius_to_fahrenheit(0.0)
        32
    """
    return round((temp_celsius * 9 / 5) + 32)


def format_temperature(temp_celsius: float, unit: str = 'C') -> tuple[int, str]:
    """
    Formata temperatura para exibição na unidade especificada.
    
    Args:
        temp_celsius: Temperatura em graus Celsius
        unit: Unidade desejada ('C' para Celsius, 'F' para Fahrenheit)
        
    Returns:
        Tupla (valor_formatado, símbolo_unidade)
        
    Example:
        >>> format_temperature(25.0, 'C')
        (25, '°C')
        >>> format_temperature(25.0, 'F')
        (77, '°F')
    """
    if unit == 'F':
        return (celsius_to_fahrenheit(temp_celsius), '°F')
    return (round(temp_celsius), '°C')


def validate_temperature_unit(unit: str) -> bool:
    """
    Valida se a unidade de temperatura é válida.
    
    Args:
        unit: Unidade a ser validada
        
    Returns:
        True se válida, False caso contrário
    """
    return unit in ('C', 'F')


def validate_display_mode(mode: str) -> bool:
    """
    Valida se o modo de exibição é válido.
    
    Args:
        mode: Modo a ser validado
        
    Returns:
        True se válido, False caso contrário
    """
    return mode in ('auto', 'temp', 'util')


def clamp(value: Union[int, float], min_value: Union[int, float], 
          max_value: Union[int, float]) -> Union[int, float]:
    """
    Limita um valor entre um mínimo e máximo.
    
    Args:
        value: Valor a ser limitado
        min_value: Valor mínimo
        max_value: Valor máximo
        
    Returns:
        Valor limitado entre min_value e max_value
        
    Example:
        >>> clamp(150, 0, 100)
        100
        >>> clamp(-10, 0, 100)
        0
        >>> clamp(50, 0, 100)
        50
    """
    return max(min_value, min(value, max_value))
