# app/routes/__init__.py
"""
Pacote de rotas da aplicação.
Define os Blueprints para organizar as rotas por contexto.
"""

from flask import Blueprint

# Criação dos blueprints
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
diretor_bp = Blueprint('diretor', __name__, url_prefix='/diretor')
unidades_bp = Blueprint('unidades', __name__, url_prefix='/unidades')
cursos_bp = Blueprint('cursos', __name__, url_prefix='/cursos')
envolvidos_bp = Blueprint('envolvidos', __name__, url_prefix='/envolvidos')
main_bp = Blueprint('main', __name__)

# Importa as rotas específicas
from . import auth_routes
from . import admin_routes
from . import diretor_routes
from . import unidades_routes
from . import cursos_routes
from . import envolvidos_routes
from . import main_routes

# Lista de blueprints para registrar na aplicação
blueprints = [
    auth_bp,
    admin_bp,
    diretor_bp,
    unidades_bp,
    cursos_bp,
    envolvidos_bp,
    main_bp,
]
