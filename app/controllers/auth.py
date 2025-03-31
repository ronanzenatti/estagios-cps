# app/controllers/auth.py
from datetime import datetime
from flask import current_app

from ..models import db, User

def authenticate_user(email, password):
    """
    Autentica um usuário com base no email e senha.
    Retorna o objeto User se a autenticação for bem-sucedida, None caso contrário.
    """
    if not email or not password:
        return None
    
    # Busca o usuário pelo email
    user = User.query.filter_by(email=email).first()
    
    # Verifica se o usuário existe e a senha está correta
    if user and user.check_password(password):
        # Atualiza o timestamp de último login
        user.last_login = datetime.utcnow()
        db.session.commit()
        return user
    
    return None

def create_user(email, password, role, nome=None, unidade_id=None):
    """
    Cria um novo usuário no sistema.
    
    Args:
        email (str): Email do usuário
        password (str): Senha do usuário
        role (str): Papel do usuário ('admin' ou 'diretor')
        nome (str, optional): Nome do usuário
        unidade_id (int, optional): ID da unidade (apenas para diretores)
        
    Returns:
        User: Objeto do usuário criado ou None em caso de erro
    """
    # Verifica se já existe um usuário com o mesmo email
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return None
    
    # Valida o papel
    if role not in ['admin', 'diretor']:
        return None
    
    # Para diretores, é necessário especificar uma unidade
    if role == 'diretor' and not unidade_id:
        return None
    
    try:
        # Cria o novo usuário
        user = User(
            email=email,
            role=role,
            nome=nome,
            unidade_id=unidade_id
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        return user
    except Exception as e:
        current_app.logger.error(f"Erro ao criar usuário: {str(e)}")
        db.session.rollback()
        return None

def change_password(user_id, current_password, new_password):
    """
    Altera a senha de um usuário.
    
    Args:
        user_id (int): ID do usuário
        current_password (str): Senha atual
        new_password (str): Nova senha
        
    Returns:
        bool: True se a senha foi alterada com sucesso, False caso contrário
    """
    # Busca o usuário pelo ID
    user = User.query.get(user_id)
    if not user:
        return False
    
    # Verifica se a senha atual está correta
    if not user.check_password(current_password):
        return False
    
    try:
        # Altera a senha
        user.set_password(new_password)
        db.session.commit()
        return True
    except Exception as e:
        current_app.logger.error(f"Erro ao alterar senha: {str(e)}")
        db.session.rollback()
        return False

def reset_password(email):
    """
    Reseta a senha de um usuário para uma temporária e envia por email.
    Em uma implementação real, enviaria um link de redefinição por email.
    
    Args:
        email (str): Email do usuário
        
    Returns:
        bool: True se o email de redefinição foi enviado, False caso contrário
    """
    # Busca o usuário pelo email
    user = User.query.filter_by(email=email).first()
    if not user:
        return False
    
    try:
        # Gera uma senha temporária aleatória
        import secrets
        temp_password = secrets.token_urlsafe(8)
        
        # Define a nova senha
        user.set_password(temp_password)
        db.session.commit()
        
        # Em uma implementação real, enviaria um email com a senha temporária
        # ou um link para redefinição
        
        return True
    except Exception as e:
        current_app.logger.error(f"Erro ao resetar senha: {str(e)}")
        db.session.rollback()
        return False

# Função a ser adicionada ao app/controllers/auth.py

def get_all_users_paginated(page=1, per_page=50, search=None, role=None):
    """
    Retorna todos os usuários do sistema com paginação.
    
    Args:
        page (int): Número da página atual
        per_page (int): Quantidade de itens por página
        search (str, optional): Termo de busca para filtrar usuários
        role (str, optional): Papel para filtrar ('admin' ou 'diretor')
        
    Returns:
        Pagination: Objeto de paginação do SQLAlchemy com os usuários
    """
    from ..models import User, Unidade
    from sqlalchemy import or_
    
    query = User.query
    
    # Aplicar filtros se fornecidos
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                User.email.ilike(search_term),
                User.nome.ilike(search_term)
            )
        )
    
    if role and role in ['admin', 'diretor']:
        query = query.filter(User.role == role)
    
    # Ordenar e paginar
    return query.order_by(User.role, User.email).paginate(page=page, per_page=per_page, error_out=False)