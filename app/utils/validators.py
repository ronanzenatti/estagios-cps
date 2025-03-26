# app/utils/validators.py
"""
Funções de validação utilizadas na aplicação.
Inclui validadores para CPF, email, telefone e outros dados.
"""

import re
from functools import lru_cache


def validar_cpf(cpf):
    """
    Valida se um CPF é válido seguindo as regras da Receita Federal.
    
    Args:
        cpf (str): CPF a ser validado, pode conter pontuação
        
    Returns:
        bool: True se o CPF é válido, False caso contrário
    """
    # Remove caracteres não numéricos
    cpf = ''.join(filter(str.isdigit, cpf))
    
    # Verifica se tem 11 dígitos
    if len(cpf) != 11:
        return False
    
    # Verifica se todos os dígitos são iguais
    if cpf == cpf[0] * 11:
        return False
    
    # Cálculo do primeiro dígito verificador
    soma = 0
    for i in range(9):
        soma += int(cpf[i]) * (10 - i)
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto
    
    # Verifica o primeiro dígito verificador
    if digito1 != int(cpf[9]):
        return False
    
    # Cálculo do segundo dígito verificador
    soma = 0
    for i in range(10):
        soma += int(cpf[i]) * (11 - i)
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto
    
    # Verifica o segundo dígito verificador
    return digito2 == int(cpf[10])


def validar_email(email):
    """
    Valida se um endereço de email está em formato válido.
    
    Args:
        email (str): Email a ser validado
        
    Returns:
        bool: True se o formato é válido, False caso contrário
    """
    # Padrão básico de validação de email
    padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if re.match(padrao, email):
        return True
    return False


def validar_telefone(telefone):
    """
    Valida se um número de telefone está em formato válido.
    Aceita formatos como (11) 98765-4321 ou 11987654321.
    
    Args:
        telefone (str): Número de telefone a ser validado
        
    Returns:
        bool: True se o formato é válido, False caso contrário
    """
    # Remove caracteres não numéricos
    telefone = ''.join(filter(str.isdigit, telefone))
    
    # Verifica se tem entre 10 e 11 dígitos (com ou sem DDD)
    if len(telefone) < 10 or len(telefone) > 11:
        return False
    
    return True


def formatar_cpf(cpf):
    """
    Formata um CPF para o padrão XXX.XXX.XXX-XX.
    
    Args:
        cpf (str): CPF a ser formatado
        
    Returns:
        str: CPF formatado ou o valor original se não for possível formatar
    """
    # Remove caracteres não numéricos
    cpf_numeros = ''.join(filter(str.isdigit, cpf))
    
    # Verifica se tem 11 dígitos
    if len(cpf_numeros) != 11:
        return cpf  # Retorna o CPF original se não tiver 11 dígitos
    
    # Aplica a formatação
    return f"{cpf_numeros[:3]}.{cpf_numeros[3:6]}.{cpf_numeros[6:9]}-{cpf_numeros[9:]}"


def formatar_telefone(telefone):
    """
    Formata um número de telefone para o padrão (XX) XXXXX-XXXX ou (XX) XXXX-XXXX.
    
    Args:
        telefone (str): Telefone a ser formatado
        
    Returns:
        str: Telefone formatado ou o valor original se não for possível formatar
    """
    # Remove caracteres não numéricos
    numeros = ''.join(filter(str.isdigit, telefone))
    
    # Verifica o tamanho
    if len(numeros) == 11:  # Celular com DDD
        return f"({numeros[:2]}) {numeros[2:7]}-{numeros[7:]}"
    elif len(numeros) == 10:  # Telefone fixo com DDD
        return f"({numeros[:2]}) {numeros[2:6]}-{numeros[6:]}"
    else:
        return telefone  # Retorna o original se não conseguir formatar
