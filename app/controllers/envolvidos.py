# app/controllers/envolvidos.py
from flask import current_app
from datetime import datetime

from ..models import db, Envolvido, Unidade, Curso

def get_all_envolvidos():
    """
    Retorna todos os envolvidos cadastrados, ordenados por nome.
    
    Returns:
        list: Lista de objetos Envolvido
    """
    return Envolvido.query.order_by(Envolvido.nome).all()

def get_envolvidos_by_unidade(unidade_id, tipo=None):
    """
    Retorna todos os envolvidos de uma unidade, filtrados por tipo (opcional).
    
    Args:
        unidade_id (int): ID da unidade
        tipo (str, optional): Tipo de envolvido ('Facilitador' ou 'Orientador')
        
    Returns:
        list: Lista de objetos Envolvido
    """
    query = Envolvido.query.filter_by(unidade_id=unidade_id)
    
    if tipo in ['Facilitador', 'Orientador']:
        query = query.filter_by(tipo=tipo)
    
    return query.order_by(Envolvido.nome).all()

def get_envolvido_by_id(envolvido_id):
    """
    Busca um envolvido pelo ID.
    
    Args:
        envolvido_id (int): ID do envolvido
        
    Returns:
        Envolvido: Objeto do envolvido ou None se não encontrado
    """
    return Envolvido.query.get(envolvido_id)

def get_envolvido_by_cpf(cpf):
    """
    Busca um envolvido pelo CPF.
    
    Args:
        cpf (str): CPF do envolvido
        
    Returns:
        Envolvido: Objeto do envolvido ou None se não encontrado
    """
    # Formata o CPF para garantir consistência
    cpf_formatado = Envolvido.formatar_cpf(cpf)
    return Envolvido.query.filter_by(cpf=cpf_formatado).first()

def create_envolvido(nome, cpf, cargo, tipo, unidade_id, cursos_ids=None, telefone=None, email=None):
    """
    Cria um novo envolvido.
    
    Args:
        nome (str): Nome do envolvido
        cpf (str): CPF do envolvido
        cargo (str): Cargo do envolvido
        tipo (str): Tipo de envolvido ('Facilitador' ou 'Orientador')
        unidade_id (int): ID da unidade
        cursos_ids (list, optional): Lista de IDs de cursos (apenas para orientadores)
        telefone (str, optional): Telefone do envolvido
        email (str, optional): Email do envolvido
        
    Returns:
        Envolvido: Objeto do envolvido criado ou None em caso de erro
    """
    # Verifica se a unidade existe
    unidade = Unidade.query.get(unidade_id)
    if not unidade:
        return None
    
    # Valida o tipo
    if tipo not in ['Facilitador', 'Orientador']:
        return None
    
    # Formata e valida o CPF
    cpf_formatado = Envolvido.formatar_cpf(cpf)
    if not Envolvido.validar_cpf(cpf_formatado):
        return None
    
    # Verifica se já existe um envolvido com o mesmo CPF
    existing = Envolvido.query.filter_by(cpf=cpf_formatado).first()
    if existing:
        return None
    
    # Verificações específicas por tipo
    if tipo == 'Orientador' and not cursos_ids:
        return None  # Orientadores devem ter pelo menos um curso
    
    try:
        # Cria o novo envolvido
        envolvido = Envolvido(
            nome=nome,
            cpf=cpf_formatado,
            cargo=cargo,
            tipo=tipo,
            unidade_id=unidade_id,
            telefone=telefone,
            email=email
        )
        
        db.session.add(envolvido)
        db.session.flush()  # Para obter o ID do envolvido
        
        # Para orientadores, associa aos cursos
        if tipo == 'Orientador' and cursos_ids:
            cursos = Curso.query.filter(
                Curso.id.in_(cursos_ids),
                Curso.unidade_id == unidade_id
            ).all()
            
            # Verifica se todos os cursos pertencem à unidade
            if len(cursos) != len(cursos_ids):
                db.session.rollback()
                return None
            
            envolvido.cursos = cursos
        
        db.session.commit()
        return envolvido
    except Exception as e:
        current_app.logger.error(f"Erro ao criar envolvido: {str(e)}")
        db.session.rollback()
        return None

def update_envolvido(envolvido_id, nome, cpf, cargo, tipo, cursos_ids=None, telefone=None, email=None, ativo=True):
    """
    Atualiza um envolvido existente.
    
    Args:
        envolvido_id (int): ID do envolvido
        nome (str): Nome do envolvido
        cpf (str): CPF do envolvido
        cargo (str): Cargo do envolvido
        tipo (str): Tipo de envolvido ('Facilitador' ou 'Orientador')
        cursos_ids (list, optional): Lista de IDs de cursos (apenas para orientadores)
        telefone (str, optional): Telefone do envolvido
        email (str, optional): Email do envolvido
        ativo (bool, optional): Status do envolvido
        
    Returns:
        bool: True se o envolvido foi atualizado com sucesso, False caso contrário
    """
    # Busca o envolvido pelo ID
    envolvido = Envolvido.query.get(envolvido_id)
    if not envolvido:
        return False
    
    # Valida o tipo
    if tipo not in ['Facilitador', 'Orientador']:
        return False
    
    # Formata e valida o CPF
    cpf_formatado = Envolvido.formatar_cpf(cpf)
    if not Envolvido.validar_cpf(cpf_formatado):
        return False
    
    # Verifica se já existe outro envolvido com o mesmo CPF
    existing = Envolvido.query.filter_by(cpf=cpf_formatado).first()
    if existing and existing.id != envolvido_id:
        return False
    
    # Verificações específicas por tipo
    if tipo == 'Orientador' and not cursos_ids:
        return False  # Orientadores devem ter pelo menos um curso
    
    try:
        # Atualiza o envolvido
        envolvido.update(
            nome=nome,
            cpf=cpf_formatado,
            cargo=cargo,
            tipo=tipo,
            telefone=telefone,
            email=email,
            ativo=ativo
        )
        
        # Atualiza os cursos conforme o tipo
        if tipo == 'Orientador' and cursos_ids:
            cursos = Curso.query.filter(
                Curso.id.in_(cursos_ids),
                Curso.unidade_id == envolvido.unidade_id
            ).all()
            
            # Verifica se todos os cursos pertencem à unidade
            if len(cursos) != len(cursos_ids):
                db.session.rollback()
                return False
            
            envolvido.cursos = cursos
        elif tipo == 'Facilitador':
            # Remove associações com cursos para facilitadores
            envolvido.cursos = []
        
        db.session.commit()
        return True
    except Exception as e:
        current_app.logger.error(f"Erro ao atualizar envolvido: {str(e)}")
        db.session.rollback()
        return False

def delete_envolvido(envolvido_id):
    """
    Exclui um envolvido.
    
    Args:
        envolvido_id (int): ID do envolvido
        
    Returns:
        bool: True se o envolvido foi excluído com sucesso, False caso contrário
    """
    # Busca o envolvido pelo ID
    envolvido = Envolvido.query.get(envolvido_id)
    if not envolvido:
        return False
    
    try:
        # Exclui o envolvido
        db.session.delete(envolvido)
        db.session.commit()
        
        return True
    except Exception as e:
        current_app.logger.error(f"Erro ao excluir envolvido: {str(e)}")
        db.session.rollback()
        return False

def toggle_envolvido_status(envolvido_id):
    """
    Ativa ou desativa um envolvido.
    
    Args:
        envolvido_id (int): ID do envolvido
        
    Returns:
        bool: True se o status foi alterado com sucesso, False caso contrário
    """
    # Busca o envolvido pelo ID
    envolvido = Envolvido.query.get(envolvido_id)
    if not envolvido:
        return False
    
    try:
        # Inverte o status
        if envolvido.ativo:
            envolvido.inativar()
        else:
            envolvido.ativar()
        
        db.session.commit()
        return True
    except Exception as e:
        current_app.logger.error(f"Erro ao alterar status do envolvido: {str(e)}")
        db.session.rollback()
        return False
