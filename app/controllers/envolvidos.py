# app/controllers/envolvidos.py
from flask import current_app
from datetime import datetime

from ..models import db, Envolvido, Unidade, Curso

def get_all_envolvidos(page=1, per_page=10, search=None):
    """
    Retorna todos os envolvidos cadastrados, ordenados por nome, com paginação.
    
    Args:
        page (int): Número da página atual
        per_page (int): Número de itens por página
        search (str, optional): Termo de busca para filtrar os resultados
        
    Returns:
        Pagination: Objeto de paginação com os envolvidos
    """
    query = Envolvido.query.order_by(Envolvido.nome)
    
    # Aplica filtro de busca se fornecido
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Envolvido.nome.ilike(search_term)) | 
            (Envolvido.cpf.ilike(search_term))
        )
    
    # Retorna resultado paginado
    return query.paginate(page=page, per_page=per_page, error_out=False)

def get_envolvidos_by_unidade(unidade_id, tipo=None, page=1, per_page=10, search=None):
    """
    Retorna todos os envolvidos de uma unidade, filtrados por tipo (opcional), com paginação.
    
    Args:
        unidade_id (int): ID da unidade
        tipo (str, optional): Tipo de envolvido ('Orientador', 'Coordenador', 'ATA', 'Facilitador', 'Apoio')
        page (int): Número da página atual
        per_page (int): Número de itens por página
        search (str, optional): Termo de busca para filtrar os resultados
        
    Returns:
        Pagination: Objeto de paginação com os envolvidos
    """
    query = Envolvido.query.filter_by(unidade_id=unidade_id)
    
    if tipo:
        query = query.filter_by(tipo=tipo)
    
    # Aplica filtro de busca se fornecido
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Envolvido.nome.ilike(search_term)) | 
            (Envolvido.cpf.ilike(search_term))
        )
    
    # Ordem e paginação
    query = query.order_by(Envolvido.nome)
    return query.paginate(page=page, per_page=per_page, error_out=False)

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

def get_tipo_stats(unidade_id=None, search=None):
    """
    Retorna estatísticas de quantidade de envolvidos por tipo.
    
    Args:
        unidade_id (int, optional): ID da unidade para filtrar
        search (str, optional): Termo de busca para filtrar os resultados
        
    Returns:
        dict: Dicionário com as contagens por tipo
    """
    from sqlalchemy import func
    
    # Construir a query base
    query = db.session.query(Envolvido.tipo, func.count(Envolvido.id).label('count'))
    
    # Aplicar filtros
    if unidade_id:
        query = query.filter(Envolvido.unidade_id == unidade_id)
        
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Envolvido.nome.ilike(search_term)) | 
            (Envolvido.cpf.ilike(search_term))
        )
    
    # Agrupar por tipo e executar
    query = query.group_by(Envolvido.tipo)
    results = query.all()
    
    # Converter para dicionário
    stats = {}
    for tipo, count in results:
        stats[tipo] = count
    
    return stats

def create_envolvido(nome, cpf, cargo, tipo, unidade_id, 
                    email_institucional, celular,
                    cursos_ids=None ):
    """
    Cria um novo envolvido.
    
    Args:
        nome (str): Nome do envolvido
        cpf (str): CPF do envolvido
        cargo (str): Cargo do envolvido
        tipo (str): Tipo de envolvido ('Orientador', 'Coordenador', 'ATA', 'Facilitador', 'Apoio')
        unidade_id (int): ID da unidade
        email_institucional (str): Email institucional do envolvido
        celular (str): Número do celular do envolvido
        cursos_ids (list, optional): Lista de IDs de cursos        
        
    Returns:
        Envolvido: Objeto do envolvido criado ou None em caso de erro
    """
    # Verifica se a unidade existe
    unidade = Unidade.query.get(unidade_id)
    if not unidade:
        return None
    
    # Valida o tipo conforme o tipo da unidade
    tipos_validos = {
        'Fatec': ['Orientador', 'Coordenador', 'Apoio'],
        'Etec': ['ATA', 'Facilitador', 'Apoio']
    }
    
    if tipo not in tipos_validos.get(unidade.tipo, []):
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
    envolvido_obj = Envolvido(
        nome=nome,
        cpf=cpf_formatado,
        cargo=cargo,
        tipo=tipo,
        unidade_id=unidade_id,
        email_institucional=email_institucional,
        celular=celular
    )
    
    # Verificações específicas para tipos que exigem cursos
    if envolvido_obj.requires_cursos and not cursos_ids:
        return None
    
    try:
        # Cria o novo envolvido
        db.session.add(envolvido_obj)
        db.session.flush()  # Para obter o ID do envolvido
        
        # Associa aos cursos, se aplicável e fornecidos
        if envolvido_obj.allows_cursos and cursos_ids:
            cursos = Curso.query.filter(
                Curso.id.in_(cursos_ids),
                Curso.unidade_id == unidade_id
            ).all()
            
            # Verifica se todos os cursos pertencem à unidade
            if len(cursos) != len(cursos_ids):
                db.session.rollback()
                return None
            
            envolvido_obj.cursos = cursos
        
        db.session.commit()
        return envolvido_obj
    except Exception as e:
        current_app.logger.error(f"Erro ao criar envolvido: {str(e)}")
        db.session.rollback()
        return None

def update_envolvido(envolvido_id, nome, cpf, cargo, tipo, 
                    email_institucional, celular,
                    cursos_ids=None, ativo=True):
    """
    Atualiza um envolvido existente.
    
    Args:
        envolvido_id (int): ID do envolvido
        nome (str): Nome do envolvido
        cpf (str): CPF do envolvido
        cargo (str): Cargo do envolvido
        tipo (str): Tipo de envolvido
        email_institucional (str): Email institucional do envolvido
        celular (str): Número do celular do envolvido
        cursos_ids (list, optional): Lista de IDs de cursos
        ativo (bool, optional): Status do envolvido
        
    Returns:
        bool: True se o envolvido foi atualizado com sucesso, False caso contrário
    """
    # Busca o envolvido pelo ID
    envolvido = Envolvido.query.get(envolvido_id)
    if not envolvido:
        return False
    
    # Busca a unidade relacionada ao envolvido
    unidade = Unidade.query.get(envolvido.unidade_id)
    if not unidade:
        return False
    
    # Valida o tipo conforme o tipo da unidade
    tipos_validos = {
        'Fatec': ['Orientador', 'Coordenador', 'Apoio'],
        'Etec': ['ATA', 'Facilitador', 'Apoio']
    }
    
    if tipo not in tipos_validos.get(unidade.tipo, []):
        return False
    
    # Formata e valida o CPF
    cpf_formatado = Envolvido.formatar_cpf(cpf)
    if not Envolvido.validar_cpf(cpf_formatado):
        return False
    
    # Verifica se já existe outro envolvido com o mesmo CPF
    existing = Envolvido.query.filter_by(cpf=cpf_formatado).first()
    if existing and existing.id != envolvido_id:
        return False
    
    # Trata a alteração de tipo
    novo_obj = Envolvido(
        nome=nome,
        cpf=cpf_formatado,
        cargo=cargo,
        tipo=tipo,
        unidade_id=envolvido.unidade_id,
        email_institucional=email_institucional,
        celular=celular
    )
    
    # Verificações específicas para tipos que exigem cursos
    if novo_obj.requires_cursos and not cursos_ids:
        return False
        
    try:
        # Atualiza o envolvido
        envolvido.update(
            nome=nome,
            cpf=cpf_formatado,
            cargo=cargo,
            tipo=tipo,
            email_institucional=email_institucional,
            celular=celular,
            ativo=ativo
        )
        
        # Atualiza os cursos conforme o tipo
        if envolvido.allows_cursos and cursos_ids:
            cursos = Curso.query.filter(
                Curso.id.in_(cursos_ids),
                Curso.unidade_id == envolvido.unidade_id
            ).all()
            
            # Verifica se todos os cursos pertencem à unidade
            if len(cursos) != len(cursos_ids):
                db.session.rollback()
                return False
            
            envolvido.cursos = cursos
        elif not envolvido.allows_cursos:
            # Remove associações com cursos para tipos que não permitem
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

def get_allowed_tipos_for_unidade(unidade_id):
    """
    Retorna os tipos de envolvidos permitidos para a unidade especificada.
    
    Args:
        unidade_id (int): ID da unidade
        
    Returns:
        list: Lista de tipos permitidos ou lista vazia em caso de erro
    """
    unidade = Unidade.query.get(unidade_id)
    if not unidade:
        return []
        
    tipos_validos = {
        'Fatec': ['Orientador', 'Coordenador', 'Apoio'],
        'Etec': ['ATA', 'Facilitador', 'Apoio']
    }
    
    return tipos_validos.get(unidade.tipo, [])