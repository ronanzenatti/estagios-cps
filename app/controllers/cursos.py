# app/controllers/cursos.py
# app/controllers/cursos.py
from flask import current_app
from datetime import datetime
from sqlalchemy import or_

from ..models import db, Curso, Unidade

def get_all_cursos():
    """
    Retorna todos os cursos cadastrados, ordenados por nome.
    
    Returns:
        list: Lista de objetos Curso
    """
    return Curso.query.order_by(Curso.nome).all()

def get_all_cursos_paginated(page=1, per_page=50, search=None, status=None, tipo_unidade=None):
    """
    Retorna todos os cursos cadastrados com paginação.
    
    Args:
        page (int): Número da página atual
        per_page (int): Quantidade de itens por página
        search (str, optional): Termo de busca para filtrar cursos
        status (str, optional): Status para filtrar ('ativo' ou 'inativo')
        tipo_unidade (str, optional): Tipo de unidade para filtrar ('Fatec' ou 'Etec')
        
    Returns:
        Pagination: Objeto de paginação do SQLAlchemy
    """
    query = Curso.query
    
    # Aplicar filtros se fornecidos
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Curso.nome.ilike(search_term),
                Curso.codigo.ilike(search_term) if Curso.codigo else False
            )
        )
    
    if status == 'ativo':
        query = query.filter(Curso.ativo == True)
    elif status == 'inativo':
        query = query.filter(Curso.ativo == False)
        
    if tipo_unidade:
        query = query.join(Unidade).filter(Unidade.tipo == tipo_unidade)
    
    # Ordenar e paginar
    return query.order_by(Curso.nome).paginate(page=page, per_page=per_page, error_out=False)

def get_cursos_by_unidade(unidade_id):
    """
    Retorna todos os cursos de uma unidade, ordenados por nome.
    
    Args:
        unidade_id (int): ID da unidade
        
    Returns:
        list: Lista de objetos Curso
    """
    return Curso.query.filter_by(unidade_id=unidade_id).order_by(Curso.nome).all()

def get_cursos_by_unidade_paginated(unidade_id, page=1, per_page=50, search=None, status=None):
    """
    Retorna os cursos de uma unidade com paginação.
    
    Args:
        unidade_id (int): ID da unidade
        page (int): Número da página atual
        per_page (int): Quantidade de itens por página
        search (str, optional): Termo de busca para filtrar cursos
        status (str, optional): Status para filtrar ('ativo' ou 'inativo')
        
    Returns:
        Pagination: Objeto de paginação do SQLAlchemy
    """
    query = Curso.query.filter_by(unidade_id=unidade_id)
    
    # Aplicar filtros se fornecidos
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Curso.nome.ilike(search_term),
                Curso.codigo.ilike(search_term) if Curso.codigo else False
            )
        )
    
    if status == 'ativo':
        query = query.filter(Curso.ativo == True)
    elif status == 'inativo':
        query = query.filter(Curso.ativo == False)
    
    # Ordenar e paginar
    return query.order_by(Curso.nome).paginate(page=page, per_page=per_page, error_out=False)

def get_all_cursos():
    """
    Retorna todos os cursos cadastrados, ordenados por nome.
    
    Returns:
        list: Lista de objetos Curso
    """
    return Curso.query.order_by(Curso.nome).all()

def get_cursos_by_unidade(unidade_id):
    """
    Retorna todos os cursos de uma unidade, ordenados por nome.
    
    Args:
        unidade_id (int): ID da unidade
        
    Returns:
        list: Lista de objetos Curso
    """
    return Curso.query.filter_by(unidade_id=unidade_id).order_by(Curso.nome).all()

def get_curso_by_id(curso_id):
    """
    Busca um curso pelo ID.
    
    Args:
        curso_id (int): ID do curso
        
    Returns:
        Curso: Objeto do curso ou None se não encontrado
    """
    return Curso.query.get(curso_id)

def create_curso(nome, unidade_id, codigo=None, descricao=None):
    """
    Cria um novo curso.
    
    Args:
        nome (str): Nome do curso
        unidade_id (int): ID da unidade
        codigo (str, optional): Código do curso
        descricao (str, optional): Descrição do curso
        
    Returns:
        Curso: Objeto do curso criado ou None em caso de erro
    """
    # Verifica se a unidade existe
    unidade = Unidade.query.get(unidade_id)
    if not unidade:
        return None
    
    # Verifica se já existe um curso com o mesmo nome na unidade
    existing = Curso.query.filter_by(unidade_id=unidade_id, nome=nome).first()
    if existing:
        return None
    
    try:
        # Cria o novo curso
        curso = Curso(
            nome=nome,
            unidade_id=unidade_id,
            codigo=codigo,
            descricao=descricao
        )
        
        db.session.add(curso)
        db.session.commit()
        
        return curso
    except Exception as e:
        current_app.logger.error(f"Erro ao criar curso: {str(e)}")
        db.session.rollback()
        return None

def update_curso(curso_id, nome, codigo=None, descricao=None, ativo=True):
    """
    Atualiza um curso existente.
    
    Args:
        curso_id (int): ID do curso
        nome (str): Nome do curso
        codigo (str, optional): Código do curso
        descricao (str, optional): Descrição do curso
        ativo (bool, optional): Status do curso
        
    Returns:
        bool: True se o curso foi atualizado com sucesso, False caso contrário
    """
    # Busca o curso pelo ID
    curso = Curso.query.get(curso_id)
    if not curso:
        return False
    
    # Verifica se já existe outro curso com o mesmo nome na unidade
    existing = Curso.query.filter_by(unidade_id=curso.unidade_id, nome=nome).first()
    if existing and existing.id != curso_id:
        return False
    
    try:
        # Atualiza o curso
        curso.update(
            nome=nome,
            codigo=codigo,
            descricao=descricao,
            ativo=ativo
        )
        
        db.session.commit()
        return True
    except Exception as e:
        current_app.logger.error(f"Erro ao atualizar curso: {str(e)}")
        db.session.rollback()
        return False

def delete_curso(curso_id):
    """
    Exclui um curso.
    
    Args:
        curso_id (int): ID do curso
        
    Returns:
        bool: True se o curso foi excluído com sucesso, False caso contrário
    """
    # Busca o curso pelo ID
    curso = Curso.query.get(curso_id)
    if not curso:
        return False
    
    try:
        # Exclui o curso
        db.session.delete(curso)
        db.session.commit()
        
        return True
    except Exception as e:
        current_app.logger.error(f"Erro ao excluir curso: {str(e)}")
        db.session.rollback()
        return False

def toggle_curso_status(curso_id):
    """
    Ativa ou desativa um curso.
    
    Args:
        curso_id (int): ID do curso
        
    Returns:
        bool: True se o status foi alterado com sucesso, False caso contrário
    """
    # Busca o curso pelo ID
    curso = Curso.query.get(curso_id)
    if not curso:
        return False
    
    try:
        # Inverte o status
        if curso.ativo:
            curso.inativar()
        else:
            curso.ativar()
        
        db.session.commit()
        return True
    except Exception as e:
        current_app.logger.error(f"Erro ao alterar status do curso: {str(e)}")
        db.session.rollback()
        return False
