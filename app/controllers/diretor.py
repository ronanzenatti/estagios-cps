# app/controllers/diretor.py
from flask import current_app
from datetime import datetime

from ..models import db, Unidade, User

def get_unidade_by_diretor(user_id):
    """
    Busca a unidade associada a um diretor.
    
    Args:
        user_id (int): ID do usuário diretor
        
    Returns:
        Unidade: Objeto da unidade ou None se não encontrada
    """
    # Busca o usuário diretor
    diretor = User.query.get(user_id)
    
    # Verifica se é um diretor e tem uma unidade associada
    if not diretor or not diretor.is_diretor() or not diretor.unidade_id:
        return None
    
    # Retorna a unidade associada
    return Unidade.query.get(diretor.unidade_id)

def update_diretor_info(unidade_id, nome_diretor, telefone=None):
    """
    Atualiza as informações do diretor na unidade.
    Permite ao diretor atualizar seu nome e o telefone da unidade.
    
    Args:
        unidade_id (int): ID da unidade
        nome_diretor (str): Nome do diretor
        telefone (str, optional): Telefone da unidade
        
    Returns:
        bool: True se as informações foram atualizadas com sucesso, False caso contrário
    """
    # Busca a unidade pelo ID
    unidade = Unidade.query.get(unidade_id)
    if not unidade:
        return False
    
    try:
        # Atualiza o nome do diretor na unidade
        unidade.nome_diretor = nome_diretor
        
        # Atualiza o telefone, se informado
        if telefone:
            unidade.telefone = telefone
        
        # Atualiza o timestamp
        unidade.updated_at = datetime.utcnow()
        
        # Atualiza também o nome no usuário associado
        diretor_user = User.query.filter_by(unidade_id=unidade_id, role='diretor').first()
        if diretor_user:
            diretor_user.nome = nome_diretor
        
        db.session.commit()
        return True
    except Exception as e:
        current_app.logger.error(f"Erro ao atualizar informações do diretor: {str(e)}")
        db.session.rollback()
        return False

def get_diretor_statistics(unidade_id):
    """
    Obtém estatísticas da unidade para o dashboard do diretor.
    
    Args:
        unidade_id (int): ID da unidade
        
    Returns:
        dict: Dicionário com as estatísticas
    """
    from ..models import Curso, Envolvido
    
    stats = {
        'total_cursos': Curso.query.filter_by(unidade_id=unidade_id).count(),
        'total_envolvidos': Envolvido.query.filter_by(unidade_id=unidade_id).count(),
        'total_orientadores': Envolvido.query.filter_by(unidade_id=unidade_id, tipo='Orientador').count(),
        'total_facilitadores': Envolvido.query.filter_by(unidade_id=unidade_id, tipo='Facilitador').count()
    }
    
    # Envolvidos por curso (apenas para orientadores)
    stats['cursos_orientadores'] = db.session.query(
        Curso.nome, db.func.count(Envolvido.id)
    ).join(
        Envolvido.cursos
    ).filter(
        Curso.unidade_id == unidade_id,
        Envolvido.unidade_id == unidade_id,
        Envolvido.tipo == 'Orientador'
    ).group_by(Curso.id).all()
    
    return stats
