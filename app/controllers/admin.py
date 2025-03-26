# app/controllers/admin.py
from flask import current_app
from datetime import datetime

from ..models import db, User
from . import unidades as unidades_controller  # Importa o controlador de unidades

# Mantém apenas as funções específicas para administradores
def get_statistics():
    """
    Obtém estatísticas gerais do sistema para o dashboard do administrador.
    
    Returns:
        dict: Dicionário com as estatísticas
    """
    from ..models import Unidade, Curso, Envolvido
    
    stats = {
        'total_unidades': Unidade.query.count(),
        'total_cursos': Curso.query.count(),
        'total_envolvidos': Envolvido.query.count(),
        'total_orientadores': Envolvido.query.filter_by(tipo='Orientador').count(),
        'total_facilitadores': Envolvido.query.filter_by(tipo='Facilitador').count(),
        'unidades_por_tipo': {
            'Fatec': Unidade.query.filter_by(tipo='Fatec').count(),
            'Etec': Unidade.query.filter_by(tipo='Etec').count()
        },
        'cidades': db.session.query(Unidade.cidade, db.func.count(Unidade.id))
                   .group_by(Unidade.cidade)
                   .order_by(db.func.count(Unidade.id).desc())
                   .limit(10)
                   .all()
    }
    
    return stats

# Funções de unidades delegadas para o controlador de unidades
get_all_unidades = unidades_controller.get_all_unidades
get_unidade_by_id = unidades_controller.get_unidade_by_id
create_unidade = unidades_controller.create_unidade
update_unidade = unidades_controller.update_unidade
delete_unidade = unidades_controller.delete_unidade