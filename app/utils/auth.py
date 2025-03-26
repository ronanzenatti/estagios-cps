# app/utils/auth.py
"""
Funções auxiliares para autenticação e controle de acesso.
"""

import secrets
import string
from datetime import datetime, timedelta
from flask import current_app
from ..models import db, User


def gerar_senha_temporaria(tamanho=8):
    """
    Gera uma senha temporária aleatória com letras e números.
    
    Args:
        tamanho (int): Tamanho da senha a ser gerada (padrão: 8)
        
    Returns:
        str: Senha temporária gerada
    """
    alfabeto = string.ascii_letters + string.digits
    senha = ''.join(secrets.choice(alfabeto) for i in range(tamanho))
    return senha


def resetar_senha(user, nova_senha=None):
    """
    Redefine a senha de um usuário.
    
    Args:
        user (User): Objeto do usuário
        nova_senha (str, optional): Nova senha. Se não for fornecida, uma senha aleatória será gerada.
        
    Returns:
        str: A nova senha
    """
    if nova_senha is None:
        nova_senha = gerar_senha_temporaria()
    
    user.set_password(nova_senha)
    db.session.commit()
    
    return nova_senha


def verificar_permissao_unidade(user, unidade_id):
    """
    Verifica se um usuário tem permissão para acessar uma unidade.
    Administradores podem acessar qualquer unidade, e diretores apenas a sua.
    
    Args:
        user (User): Objeto do usuário
        unidade_id (int): ID da unidade a ser verificada
        
    Returns:
        bool: True se o usuário tem permissão, False caso contrário
    """
    if user.is_admin():
        return True
    
    if user.is_diretor() and user.unidade_id == unidade_id:
        return True
    
    return False


def registrar_login(user):
    """
    Registra a data e hora do login de um usuário.
    
    Args:
        user (User): Objeto do usuário
        
    Returns:
        None
    """
    user.last_login = datetime.utcnow()
    db.session.commit()


def criar_token_reset_senha(user, expires_in=3600):
    """
    Cria um token para redefinição de senha com validade limitada.
    Em um sistema real, associaria o token ao usuário no banco de dados.
    
    Args:
        user (User): Objeto do usuário
        expires_in (int): Tempo de validade em segundos (padrão: 1 hora)
        
    Returns:
        str: Token gerado
    """
    token = secrets.token_urlsafe(32)
    
    # Em um sistema real, armazenaria o token, usuário e data de expiração
    # Aqui apenas retornamos o token, para exemplificar
    
    return token


def verificar_token_reset_senha(token):
    """
    Verifica se um token de redefinição de senha é válido.
    Em um sistema real, consultaria o banco de dados para validar o token.
    
    Args:
        token (str): Token a ser verificado
        
    Returns:
        User or None: Objeto do usuário se o token for válido, None caso contrário
    """
    # Implementação de exemplo
    # Em um sistema real, verificaria o token no banco de dados
    
    # Se o token for válido, retorna o usuário associado a ele
    # Caso contrário, retorna None
    
    return None  # Como é apenas um exemplo, retornamos None por padrão
