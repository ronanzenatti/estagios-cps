# app/controllers/unidades.py
from flask import current_app
from datetime import datetime

from ..models import db, Unidade, User, Curso, Envolvido

def get_all_unidades():
    """
    Retorna todas as unidades cadastradas, ordenadas por tipo e número.
    
    Returns:
        list: Lista de objetos Unidade
    """
    return Unidade.query.order_by(Unidade.tipo, Unidade.numero).all()

def get_unidade_by_id(unidade_id):
    """
    Busca uma unidade pelo ID.
    
    Args:
        unidade_id (int): ID da unidade
        
    Returns:
        Unidade: Objeto da unidade ou None se não encontrada
    """
    return Unidade.query.get(unidade_id)

def get_unidades_by_cidade(cidade):
    """
    Busca unidades por cidade.
    
    Args:
        cidade (str): Nome da cidade
        
    Returns:
        list: Lista de objetos Unidade
    """
    return Unidade.query.filter_by(cidade=cidade).all()

def get_unidades_by_tipo(tipo):
    """
    Busca unidades por tipo (Fatec ou Etec).
    
    Args:
        tipo (str): Tipo da unidade ('Fatec' ou 'Etec')
        
    Returns:
        list: Lista de objetos Unidade
    """
    if tipo not in ['Fatec', 'Etec']:
        return []
    
    return Unidade.query.filter_by(tipo=tipo).order_by(Unidade.numero).all()

def create_unidade(tipo, numero, nome, cidade, telefone, nome_diretor, email_diretor):
    """
    Cria uma nova unidade e o usuário diretor associado.
    
    Args:
        tipo (str): Tipo da unidade ('Fatec' ou 'Etec')
        numero (str): Número da unidade
        nome (str): Nome da unidade
        cidade (str): Cidade da unidade
        telefone (str): Telefone da unidade
        nome_diretor (str): Nome do diretor
        email_diretor (str): Email do diretor
        
    Returns:
        Unidade: Objeto da unidade criada ou None em caso de erro
    """
    # Validações básicas
    if tipo not in ['Fatec', 'Etec']:
        return None
    
    # Verifica se já existe uma unidade com o mesmo tipo e número
    existing = Unidade.query.filter_by(tipo=tipo, numero=numero).first()
    if existing:
        return None
    
    try:
        # Cria a nova unidade
        unidade = Unidade(
            tipo=tipo,
            numero=numero,
            nome=nome,
            cidade=cidade,
            telefone=telefone,
            nome_diretor=nome_diretor,
            email_diretor=email_diretor
        )
        
        db.session.add(unidade)
        db.session.flush()  # Para obter o ID da unidade
        
        # Cria o usuário para o diretor
        email_institucional = unidade.email_institucional
        
        diretor_user = User(
            email=email_institucional,
            role='diretor',
            nome=nome_diretor,
            unidade_id=unidade.id
        )
        
        # Define a senha inicial como o número da unidade
        diretor_user.set_password(numero)
        
        db.session.add(diretor_user)
        db.session.commit()
        
        return unidade
    except Exception as e:
        current_app.logger.error(f"Erro ao criar unidade: {str(e)}")
        db.session.rollback()
        return None

def update_unidade(unidade_id, tipo, numero, nome, cidade, telefone, nome_diretor, email_diretor):
    """
    Atualiza uma unidade existente e o usuário diretor associado, se necessário.
    
    Args:
        unidade_id (int): ID da unidade
        tipo (str): Tipo da unidade ('Fatec' ou 'Etec')
        numero (str): Número da unidade
        nome (str): Nome da unidade
        cidade (str): Cidade da unidade
        telefone (str): Telefone da unidade
        nome_diretor (str): Nome do diretor
        email_diretor (str): Email do diretor
        
    Returns:
        bool: True se a unidade foi atualizada com sucesso, False caso contrário
    """
    # Busca a unidade pelo ID
    unidade = Unidade.query.get(unidade_id)
    if not unidade:
        return False
    
    # Validações básicas
    if tipo not in ['Fatec', 'Etec']:
        return False
    
    # Verifica se já existe outra unidade com o mesmo tipo e número
    if tipo != unidade.tipo or numero != unidade.numero:
        existing = Unidade.query.filter_by(tipo=tipo, numero=numero).first()
        if existing and existing.id != unidade_id:
            return False
    
    try:
        # Atualiza a unidade
        unidade.update(
            tipo=tipo,
            numero=numero,
            nome=nome,
            cidade=cidade,
            telefone=telefone,
            nome_diretor=nome_diretor,
            email_diretor=email_diretor
        )
        
        # Verifica se o email institucional mudou
        novo_email = f"{tipo[0]}{numero}dir@cps.sp.gov.br".lower()
        
        if unidade.email_institucional != novo_email:
            # Atualiza o email do usuário diretor
            diretor_user = User.query.filter_by(unidade_id=unidade_id, role='diretor').first()
            
            if diretor_user:
                diretor_user.email = novo_email
                diretor_user.nome = nome_diretor
        
        db.session.commit()
        return True
    except Exception as e:
        current_app.logger.error(f"Erro ao atualizar unidade: {str(e)}")
        db.session.rollback()
        return False

def delete_unidade(unidade_id):
    """
    Exclui uma unidade e o usuário diretor associado.
    
    Args:
        unidade_id (int): ID da unidade
        
    Returns:
        bool: True se a unidade foi excluída com sucesso, False caso contrário
    """
    # Busca a unidade pelo ID
    unidade = Unidade.query.get(unidade_id)
    if not unidade:
        return False
    
    try:
        # Exclui o usuário diretor associado
        diretor_user = User.query.filter_by(unidade_id=unidade_id, role='diretor').first()
        if diretor_user:
            db.session.delete(diretor_user)
        
        # Exclui a unidade (os relacionamentos com cascata cuidarão dos cursos e envolvidos)
        db.session.delete(unidade)
        db.session.commit()
        
        return True
    except Exception as e:
        current_app.logger.error(f"Erro ao excluir unidade: {str(e)}")
        db.session.rollback()
        return False

def get_unidade_statistics(unidade_id):
    """
    Obtém estatísticas de uma unidade específica.
    
    Args:
        unidade_id (int): ID da unidade
        
    Returns:
        dict: Dicionário com as estatísticas
    """
    stats = {
        'total_cursos': Curso.query.filter_by(unidade_id=unidade_id).count(),
        'cursos_ativos': Curso.query.filter_by(unidade_id=unidade_id, ativo=True).count(),
        'total_envolvidos': Envolvido.query.filter_by(unidade_id=unidade_id).count(),
        'orientadores': Envolvido.query.filter_by(unidade_id=unidade_id, tipo='Orientador').count(),
        'facilitadores': Envolvido.query.filter_by(unidade_id=unidade_id, tipo='